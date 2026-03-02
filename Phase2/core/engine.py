afrom typing import List, Any, Dict
from .contracts import DataSink
import math

class TransformationEngine:
    def __init__(self, sink: DataSink, config: Dict = None):
        """
        Initialize engine with injected sink and optional config.
        Config contains: region, year, start_year, end_year, decline_years
        """
        self.sink = sink
        self.config = config or {}
        self.df = None

    def execute(self, raw_data: List[Any]) -> None:
        """
        Process raw_data and compute 8 analytics.
        Then forward all results to the sink.
        """
        self.df = raw_data
        
        region = self.config.get('region', 'Asia')
        year = str(self.config.get('year', 2020))
        start_year = str(self.config.get('start_year', 2000))
        end_year = str(self.config.get('end_year', 2024))
        decline_years = self.config.get('decline_years', 3)
        
        # Filter data by region
        region_data = [r for r in self.df if r.get('Continent') == region]
        
        results = {
            'metadata': {
                'region': region,
                'year': year,
                'total_countries': len(region_data)
            },
            'analytics': {}
        }
        
        # 1. Top 10 Countries by GDP
        results['analytics']['top_10_gdp'] = self._top_10_gdp(region_data, year)
        
        # 2. Bottom 10 Countries by GDP
        results['analytics']['bottom_10_gdp'] = self._bottom_10_gdp(region_data, year)
        
        # 3. GDP Growth Rate per Country
        results['analytics']['growth_rates'] = self._gdp_growth_rate(region_data, start_year, end_year)
        
        # 4. Average GDP by Continent
        results['analytics']['avg_gdp_by_continent'] = self._avg_gdp_by_continent(self.df, year)
        
        # 5. Global GDP Trend
        results['analytics']['global_gdp_trend'] = self._global_gdp_trend(self.df, start_year, end_year)
        
        # 6. Fastest Growing Continent
        results['analytics']['fastest_growing_continent'] = self._fastest_growing_continent(self.df, start_year, end_year)
        
        # 7. Countries with Consistent Decline
        results['analytics']['consistent_decline'] = self._consistent_decline(region_data, decline_years)
        
        # 8. Continent Contribution to Global GDP
        results['analytics']['continent_contribution'] = self._continent_contribution(self.df, year)
        
        self.sink.write([results])

    def _top_10_gdp(self, region_data, year):
        """Top 10 countries by GDP in given year and region."""
        valid = [(r['Country Name'], self._safe_get(r, year)) for r in region_data]
        valid = [(name, gdp) for name, gdp in valid if gdp is not None and not math.isnan(gdp)]
        top = sorted(valid, key=lambda x: x[1], reverse=True)[:10]
        return [{'country': name, 'gdp': gdp} for name, gdp in top]

    def _bottom_10_gdp(self, region_data, year):
        """Bottom 10 countries by GDP in given year and region."""
        valid = [(r['Country Name'], self._safe_get(r, year)) for r in region_data]
        valid = [(name, gdp) for name, gdp in valid if gdp is not None and not math.isnan(gdp)]
        bottom = sorted(valid, key=lambda x: x[1])[:10]
        return [{'country': name, 'gdp': gdp} for name, gdp in bottom]

    def _gdp_growth_rate(self, region_data, start_year, end_year):
        """Calculate GDP growth rate per country over given range."""
        result = []
        for country in region_data:
            start_gdp = self._safe_get(country, start_year)
            end_gdp = self._safe_get(country, end_year)
            if start_gdp and end_gdp and not math.isnan(start_gdp) and not math.isnan(end_gdp) and start_gdp != 0:
                growth_rate = ((end_gdp - start_gdp) / start_gdp) * 100
                result.append({'country': country['Country Name'], 'growth_rate': growth_rate})
        return sorted(result, key=lambda x: x['growth_rate'], reverse=True)

    def _avg_gdp_by_continent(self, all_data, year):
        """Average GDP by continent for given year."""
        continents = {}
        for record in all_data:
            continent = record.get('Continent', 'Unknown')
            gdp = self._safe_get(record, year)
            if gdp is not None and not math.isnan(gdp):
                if continent not in continents:
                    continents[continent] = []
                continents[continent].append(gdp)
        
        result = []
        for continent, gdps in continents.items():
            avg = sum(gdps) / len(gdps) if gdps else 0
            result.append({'continent': continent, 'average_gdp': avg, 'country_count': len(gdps)})
        return sorted(result, key=lambda x: x['average_gdp'], reverse=True)

    def _global_gdp_trend(self, all_data, start_year, end_year):
        """Global GDP trend over year range."""
        years = range(int(start_year), int(end_year) + 1)
        trend = []
        for year in years:
            year_str = str(year)
            total = 0
            count = 0
            for record in all_data:
                gdp = self._safe_get(record, year_str)
                if gdp is not None and not math.isnan(gdp):
                    total += gdp
                    count += 1
            if count > 0:
                trend.append({'year': year, 'total_gdp': total})
        return trend

    def _fastest_growing_continent(self, all_data, start_year, end_year):
        """Identify continent with fastest growth rate."""
        continents = {}
        for record in all_data:
            continent = record.get('Continent', 'Unknown')
            start_gdp = self._safe_get(record, start_year)
            end_gdp = self._safe_get(record, end_year)
            if continent not in continents:
                continents[continent] = {'start': 0, 'end': 0, 'count': 0}
            if start_gdp and not math.isnan(start_gdp):
                continents[continent]['start'] += start_gdp
            if end_gdp and not math.isnan(end_gdp):
                continents[continent]['end'] += end_gdp
            continents[continent]['count'] += 1
        
        growth = []
        for continent, data in continents.items():
            if data['start'] > 0:
                rate = ((data['end'] - data['start']) / data['start']) * 100
                growth.append({'continent': continent, 'growth_rate': rate})
        return sorted(growth, key=lambda x: x['growth_rate'], reverse=True)[0] if growth else {}

    def _consistent_decline(self, region_data, decline_years):
        """Countries with consistent GDP decline in last x years."""
        result = []
        for country in region_data:
            year_range = range(2024 - decline_years, 2024)
            gdps = []
            for year in year_range:
                gdp = self._safe_get(country, str(year))
                if gdp is not None and not math.isnan(gdp):
                    gdps.append(gdp)
            
            if len(gdps) == decline_years and all(gdps[i] > gdps[i+1] for i in range(len(gdps)-1)):
                result.append({'country': country['Country Name'], 'years': decline_years})
        return result

    def _continent_contribution(self, all_data, year):
        """Contribution of each continent to global GDP."""
        continents = {}
        total_gdp = 0
        
        for record in all_data:
            continent = record.get('Continent', 'Unknown')
            gdp = self._safe_get(record, year)
            if gdp is not None and not math.isnan(gdp):
                if continent not in continents:
                    continents[continent] = 0
                continents[continent] += gdp
                total_gdp += gdp
        
        result = []
        for continent, gdp in continents.items():
            percentage = (gdp / total_gdp * 100) if total_gdp > 0 else 0
            result.append({'continent': continent, 'gdp': gdp, 'percentage': percentage})
        return sorted(result, key=lambda x: x['gdp'], reverse=True)

    def _safe_get(self, record, year):
        """Safely extract numeric GDP value from record."""
        try:
            val = record.get(year)
            if val is None:
                return None
            if isinstance(val, str):
                val = float(val)
            return float(val) if not math.isnan(val) else None
        except (ValueError, TypeError):
            return None
