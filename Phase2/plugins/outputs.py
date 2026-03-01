from typing import List, Dict
from core.contracts import DataSink
import os
import tempfile
import subprocess
import time


class ConsoleWriter:
    """Formatted console output for analytics results."""
    
    def write(self, records: List[Dict]) -> None:
        if not records:
            print("[ConsoleWriter] No records to display.")
            return
        
        result = records[0]
        metadata = result.get('metadata', {})
        analytics = result.get('analytics', {})
        
        print("\n" + "="*80)
        print("GDP ANALYSIS REPORT".center(80))
        print("="*80)
        print(f"\nRegion: {metadata.get('region')}")
        print(f"Analysis Year: {metadata.get('year')}")
        print(f"Total Countries: {metadata.get('total_countries')}\n")
        
        # 1. Top 10 GDP
        print("\n" + "-"*80)
        print("1. TOP 10 COUNTRIES BY GDP")
        print("-"*80)
        for i, item in enumerate(analytics.get('top_10_gdp', []), 1):
            print(f"  {i}. {item['country']}: ${item['gdp']:,.2f}")
        
        # 2. Bottom 10 GDP
        print("\n" + "-"*80)
        print("2. BOTTOM 10 COUNTRIES BY GDP")
        print("-"*80)
        for i, item in enumerate(analytics.get('bottom_10_gdp', []), 1):
            print(f"  {i}. {item['country']}: ${item['gdp']:,.2f}")
        
        # 3. Growth Rates
        print("\n" + "-"*80)
        print("3. GDP GROWTH RATES (Top 10)")
        print("-"*80)
        for i, item in enumerate(analytics.get('growth_rates', [])[:10], 1):
            print(f"  {i}. {item['country']}: {item['growth_rate']:+.2f}%")
        
        # 4. Avg GDP by Continent
        print("\n" + "-"*80)
        print("4. AVERAGE GDP BY CONTINENT")
        print("-"*80)
        for item in analytics.get('avg_gdp_by_continent', []):
            print(f"  {item['continent']}: ${item['average_gdp']:,.2f} ({item['country_count']} countries)")
        
        # 5. Global GDP Trend
        print("\n" + "-"*80)
        print("5. GLOBAL GDP TREND (First 5 & Last 5 Years)")
        print("-"*80)
        trend = analytics.get('global_gdp_trend', [])
        for item in trend[:5]:
            print(f"  {item['year']}: ${item['total_gdp']:,.2f}")
        if len(trend) > 10:
            print("  ...")
        for item in trend[-5:]:
            print(f"  {item['year']}: ${item['total_gdp']:,.2f}")
        
        # 6. Fastest Growing Continent
        print("\n" + "-"*80)
        print("6. FASTEST GROWING CONTINENT")
        print("-"*80)
        fastest = analytics.get('fastest_growing_continent', {})
        if fastest:
            print(f"  {fastest['continent']}: {fastest['growth_rate']:+.2f}%")
        
        # 7. Consistent Decline
        print("\n" + "-"*80)
        print("7. COUNTRIES WITH CONSISTENT GDP DECLINE")
        print("-"*80)
        decline_list = analytics.get('consistent_decline', [])
        if decline_list:
            for item in decline_list[:10]:
                print(f"  • {item['country']} (last {item['years']} years)")
        else:
            print("  (None found in this region)")
        
        # 8. Continent Contribution
        print("\n" + "-"*80)
        print("8. CONTRIBUTION TO GLOBAL GDP BY CONTINENT")
        print("-"*80)
        for item in analytics.get('continent_contribution', []):
            print(f"  {item['continent']}: ${item['gdp']:,.2f} ({item['percentage']:.1f}%)")
        
        print("\n" + "="*80 + "\n")


class ChartWriter:
    """Display analytics as graphs using system image viewer."""
    
    def __init__(self):
        """Constructor intentionally takes no parameters; any previous out_dir
        arguments are ignored. Graphs are rendered directly via temporary
        files and a system viewer rather than being persisted to disk.
        """
        # nothing to initialize
        return

    def write(self, records: List[Dict]) -> None:
        if not records:
            print("[ChartWriter] No records to visualize.")
            return
        
        result = records[0]
        metadata = result.get('metadata', {})
        analytics = result.get('analytics', {})
        region = metadata.get('region', 'Global')
        year = str(metadata.get('year', 'N/A'))
        
        print("\n" + "="*80)
        print("DISPLAYING VISUALIZATIONS".center(80))
        print("="*80 + "\n")
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import matplotlib
            matplotlib.use('Agg')
            
            # 1. Top 10 GDP
            self._show_chart(
                f"TOP 10 COUNTRIES BY GDP\n({region} - {year})",
                analytics.get('top_10_gdp', [])[:10],
                'steelblue'
            )

            # 2. Bottom 10 GDP
            self._show_chart(
                f"BOTTOM 10 COUNTRIES BY GDP\n({region} - {year})",
                analytics.get('bottom_10_gdp', [])[:10],
                'coral'
            )

            # 3. Growth Rates
            self._show_growth_chart(
                f"TOP 10 GDP GROWTH RATES\n({region})",
                analytics.get('growth_rates', [])[:10]
            )

            # 4. Average GDP by Continent
            self._show_continent_avg_chart(
                f"AVERAGE GDP BY CONTINENT\n({year})",
                analytics.get('avg_gdp_by_continent', [])
            )

            # 5. Global GDP Trend
            self._show_trend_chart(
                "GLOBAL GDP TREND",
                analytics.get('global_gdp_trend', [])
            )

            # 6. Fastest Growing Continent
            fastest = analytics.get('fastest_growing_continent', {})
            if fastest:
                self._show_fastest_continent_chart(
                    "FASTEST GROWING CONTINENT",
                    fastest
                )

            # 7. Countries with Consistent Decline
            self._show_decline_chart(
                f"COUNTRIES WITH CONSISTENT GDP DECLINE\n({region})",
                analytics.get('consistent_decline', [])
            )

            # 8. Continent Contribution
            self._show_contribution_chart(
                f"CONTRIBUTION TO GLOBAL GDP\n({year})",
                analytics.get('continent_contribution', [])
            )
            
            print("\n" + "="*80)
            print("All visualizations displayed!".center(80))
            print("="*80 + "\n")
            
        except ImportError as e:
            print(f"[ChartWriter] ERROR: matplotlib not available - {e}")
            print("Install with: pip install matplotlib")

    def _show_window(self, fig, title: str) -> None:
        """Save to temp file and display with system image viewer."""
        import matplotlib.pyplot as plt
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_file = f.name
        
        fig.savefig(temp_file, dpi=100, bbox_inches='tight')
        print(f"  📊 {title}")
        
        # Try different image viewers
        viewers = ['eog', 'feh', 'display', 'xdg-open']
        opened = False
        
        for viewer in viewers:
            try:
                subprocess.Popen([viewer, temp_file], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                opened = True
                time.sleep(2)  # Give viewer time to open
                break
            except FileNotFoundError:
                continue
        
        if not opened:
            print(f"     (Could not open - saved: {temp_file})")
        
        # Clean up
        try:
            os.unlink(temp_file)
        except:
            pass
        
        plt.close(fig)

    def _show_chart(self, title: str, data: List[Dict], color: str) -> None:
        """Display bar chart for top/bottom countries."""
        import matplotlib.pyplot as plt
        
        if not data:
            return
        
        countries = [x['country'][:20] for x in data]
        gdps = [x['gdp'] / 1e12 for x in data]
        
        fig, ax = plt.subplots(figsize=(14, 9))
        ax.barh(countries, gdps, color=color, edgecolor='black', linewidth=1.2)
        ax.set_xlabel('GDP (Trillions USD)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels
        for i, (country, gdp) in enumerate(zip(countries, gdps)):
            ax.text(gdp, i, f'  ${gdp:.2f}T', va='center', fontsize=9)
        
        plt.tight_layout()
        self._show_window(fig, title)

    def _show_growth_chart(self, title: str, data: List[Dict]) -> None:
        """Display growth rate chart."""
        import matplotlib.pyplot as plt
        
        if not data:
            return
        
        countries = [x['country'][:18] for x in data]
        rates = [x['growth_rate'] for x in data]
        colors = ['#2ecc71' if r > 0 else '#e74c3c' for r in rates]
        
        fig, ax = plt.subplots(figsize=(14, 9))
        bars = ax.barh(countries, rates, color=colors, edgecolor='black', linewidth=1.2)
        ax.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.axvline(0, color='black', linewidth=1.5)
        
        # Add value labels
        for i, (country, rate) in enumerate(zip(countries, rates)):
            ax.text(rate, i, f'  {rate:+.1f}%', va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        self._show_window(fig, title)

    def _show_continent_avg_chart(self, title: str, data: List[Dict]) -> None:
        """Display average GDP by continent."""
        import matplotlib.pyplot as plt
        
        if not data:
            return
        
        continents = [x['continent'] for x in data]
        avgs = [x['average_gdp'] / 1e12 for x in data]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        bars = ax.bar(continents, avgs, color='#9b59b6', edgecolor='black', linewidth=1.2)
        ax.set_ylabel('Average GDP (Trillions USD)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.tick_params(axis='x', rotation=45, labelsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar, avg in zip(bars, avgs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${avg:.2f}T', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        self._show_window(fig, title)

    def _show_trend_chart(self, title: str, data: List[Dict]) -> None:
        """Display global GDP trend line."""
        import matplotlib.pyplot as plt
        
        if not data:
            return
        
        years = [x['year'] for x in data]
        gdps = [x['total_gdp'] / 1e15 for x in data]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(years, gdps, marker='o', linewidth=3, markersize=8,
                color='#27ae60', markerfacecolor='#2ecc71', markeredgecolor='#27ae60', markeredgewidth=2)
        ax.fill_between(years, gdps, alpha=0.2, color='#2ecc71')
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total GDP (Quadrillions USD)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add year labels
        for year, gdp in zip(years[::2], gdps[::2]):  # Every 2nd year
            ax.text(year, gdp, f'{gdp:.1f}Q', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        self._show_window(fig, title)

    def _show_fastest_continent_chart(self, title: str, data: Dict) -> None:
        """Display fastest growing continent highlight."""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        continent = data.get('continent', 'N/A')
        growth_rate = data.get('growth_rate', 0)
        
        text = f"{continent}\n\n{growth_rate:+.2f}%\n\nFastest Growing"
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=32, fontweight='bold',
               bbox=dict(boxstyle='round,pad=1.5', facecolor='#2ecc71', edgecolor='#27ae60', linewidth=4),
               transform=ax.transAxes, color='white')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._show_window(fig, title)

    def _show_decline_chart(self, title: str, data: List[Dict]) -> None:
        """Display countries with consistent decline."""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('off')
        
        if data:
            countries_text = "\n".join([f"{i}. {x['country']}" for i, x in enumerate(data[:15], 1)])
            text = f"Countries with Consistent GDP Decline:\n\n{countries_text}"
        else:
            text = "No countries with consistent GDP decline found"
        
        ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=11, family='monospace',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='#fff9e6', edgecolor='#f39c12', linewidth=2, pad=1))
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._show_window(fig, title)

    def _show_contribution_chart(self, title: str, data: List[Dict]) -> None:
        """Display contribution pie chart."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        if not data:
            return
        
        continents = [x['continent'] for x in data]
        percentages = [x['percentage'] for x in data]
        
        fig, ax = plt.subplots(figsize=(12, 10))
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
        wedges, texts, autotexts = ax.pie(percentages, labels=continents, autopct='%1.1f%%',
                                           colors=colors, startangle=90,
                                           textprops={'fontsize': 11, 'weight': 'bold'})
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._show_window(fig, title)
