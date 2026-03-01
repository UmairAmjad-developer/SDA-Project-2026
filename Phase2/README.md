# GDP Analysis System - Phase 2

**Modular Architecture with Dependency Inversion Principle**

A complete refactor of Phase 1 using clean architecture principles, strict separation of concerns, and dependency injection.

---

## 🎯 Overview

Phase 2 transforms the monolithic Phase 1 application into a **modular, loosely-coupled system** where:

- **Core** is independent of I/O specifics
- **Plugins** (inputs/outputs) have zero knowledge of business logic
- **Configuration** drives runtime behavior without code changes
- **Protocols** enforce contracts between modules

This follows the **Dependency Inversion Principle (DIP)**: depend on abstractions, not concrete implementations.

---

## 📦 Architecture

```
Phase2/
├── main.py                 # Orchestrator (Bootstrap)
├── config.json             # Configuration (input, output, parameters)
├── core/
│   ├── __init__.py
│   ├── contracts.py        # Protocols: DataSink, PipelineService
│   └── engine.py           # TransformationEngine (8 analytics)
├── plugins/
│   ├── __init__.py
│   ├── inputs.py           # CSVReader, JSONReader
│   └── outputs.py          # ConsoleWriter, ChartWriter
├── data/
│   └── gdp_dataset_fixed.csv
└── out/
    └── gdp_analysis_*.png  # Generated visualizations
```

---

## 🏗️ Design Pattern: Dependency Inversion

### The Golden Rules

1. **Inbound Abstraction**: Inputs implement `PipelineService` protocol
2. **Outbound Abstraction**: Core calls methods on `DataSink` protocol
3. **Core Ownership**: Core defines all contracts

### Data Flow

```
config.json → main.py
              ↓
         [Factory Pattern]
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Sink     Engine    Source
    │         │         │
 [DataSink] [Core]  [PipelineService]
    ↑         ↑         ↑
    └─────────┼─────────┘
        Duck Typing
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r ../Phase1/requirements.txt
```

### 2. Configure (config.json)

```json
{
  "input": "csv",
  "output": "console",
  "path": "data/gdp_dataset_fixed.csv",
  "region": "Asia",
  "year": 2020,
  "start_year": 2010,
  "end_year": 2024,
  "decline_years": 3
}
```

**Parameters:**
- `input`: `"csv"` or `"json"` (reader plugin)
- `output`: `"console"` or `"chart"` (writer plugin)
- `path`: Path to data file
- `region`: Target continent (Africa, Asia, Europe, etc.)
- `year`: Analysis year
- `start_year`: Start of growth range
- `end_year`: End of growth range
- `decline_years`: Years to check for consistent decline

### 3. Run

```bash
python main.py
```

---

## 📊 8 Analytics Delivered

### 1. **Top 10 Countries by GDP**
   - For selected region & year
   - Sorted by GDP value (descending)

### 2. **Bottom 10 Countries by GDP**
   - For selected region & year
   - Sorted by GDP value (ascending)

### 3. **GDP Growth Rate**
   - Per country in selected region
   - Calculated over `start_year` to `end_year`
   - Returns top 10 growth performers

### 4. **Average GDP by Continent**
   - For each continent in dataset
   - For selected year
   - Includes country count

### 5. **Global GDP Trend**
   - Total global GDP per year
   - Over date range (`start_year` to `end_year`)
   - Shows macro economic patterns

### 6. **Fastest Growing Continent**
   - Compares continent-level growth rates
   - Over date range
   - Single best performer

### 7. **Countries with Consistent Decline**
   - Identifies countries with declining GDP
   - Over last `decline_years` years
   - Requires uninterrupted decline

### 8. **Continent Contribution to Global GDP**
   - Breakdown by continent for selected year
   - Shows % contribution
   - Identifies economic centers

---

## 🔌 Plugin Architecture

### Inputs (readers)

#### CSVReader
```python
CSVReader(service: PipelineService, path: str)
```
- Reads CSV file via pandas
- Converts to list of dicts
- Calls `service.execute(raw_data)`

#### JSONReader
```python
JSONReader(service: PipelineService, path: str)
```
- Reads JSON array
- Compatible with `service.execute()`

**Add more readers** without touching Core:

```python
class ExcelReader:
    def __init__(self, service, path):
        self.service = service
        self.path = path
    def read(self):
        # your logic
        self.service.execute(raw_data)
```

Then update `main.py`:

```python
INPUT_DRIVERS = {
    "csv": CSVReader,
    "json": JSONReader,
    "excel": ExcelReader
}
```

### Outputs (writers)

#### ConsoleWriter
```python
ConsoleWriter().write(records: List[dict])
```
- Pretty-prints formatted analytics
- 8 sections with detailed breakdown
- No dependencies on Core logic

#### ChartWriter
```python
ChartWriter(out_dir: str = 'out').write(records)
```
- Generates 9-panel visualization
- Saves to PNG file
- Includes:
  - Top/Bottom 10 bar charts
  - Growth rates benchmark
  - Continental averages
  - Global trend line
  - Pie chart (contribution)
  - Stats boxes

**Add more writers**:

```python
class FileWriter:
    def write(self, records):
        with open("results.json", "w") as f:
            json.dump(records, f, indent=2)

class DatabaseWriter:
    def write(self, records):
        # store in database
```

---

## 🔄 Workflow Example

### Console Output (Default)

```bash
$ python main.py

================================================================================
                              GDP ANALYSIS REPORT
================================================================================

Region: Asia
Analysis Year: 2020
Total Countries: 57

--------------------------------------------------------------------------------
1. TOP 10 COUNTRIES BY GDP
--------------------------------------------------------------------------------
  1. East Asia & Pacific (excluding high income): $17,805,166,443,182.20
  2. China: $14,996,414,166,715.10
  3. Japan: $5,054,068,005,376.28
  ...
```

### Chart Output

```bash
$ cat config.json  # change output to "chart"
$ python main.py

[ChartWriter] Saved visualization to: out/gdp_analysis_Asia_2020.png
```

Then open `out/gdp_analysis_Asia_2020.png` to view the 9-panel dashboard.

---

## 🛠️ Configuration Examples

### Europe Analysis

```json
{
  "input": "csv",
  "output": "console",
  "path": "data/gdp_dataset_fixed.csv",
  "region": "Europe",
  "year": 2022,
  "start_year": 2015,
  "end_year": 2023,
  "decline_years": 2
}
```

### Global Overview with Charts

```json
{
  "input": "csv",
  "output": "chart",
  "path": "data/gdp_dataset_fixed.csv",
  "region": "Global",
  "year": 2024,
  "start_year": 2000,
  "end_year": 2024,
  "decline_years": 5
}
```

---

## 📐 Module Documentation

### core/contracts.py

```python
@runtime_checkable
class DataSink(Protocol):
    """Any output module must implement this."""
    def write(self, records: List[dict]) -> None: ...

@runtime_checkable
class PipelineService(Protocol):
    """Any input module must call this."""
    def execute(self, raw_data: List[Any]) -> None: ...
```

### core/engine.py

```python
class TransformationEngine:
    def __init__(self, sink: DataSink, config: Dict):
        """Receives injected sink and config."""
        
    def execute(self, raw_data: List[Any]) -> None:
        """Orchestrates all 8 analytics."""
        # Computes results
        # Sends to sink via sink.write([results])
```

### plugins/inputs.py

```python
class CSVReader:
    def __init__(self, service: PipelineService, path: str):
        self.service = service  # receives Core (duck-typed)
        self.path = path
    
    def read(self):
        df = pd.read_csv(self.path)
        raw_data = df.to_dict(orient='records')
        self.service.execute(raw_data)  # interface-based call
```

### plugins/outputs.py

```python
class ConsoleWriter:
    def write(self, records: List[Dict]) -> None:
        """Formatted display of analytics."""
        
class ChartWriter:
    def write(self, records: List[Dict]) -> None:
        """Matplotlib visualization."""
```

---

## 🌟 Key Principles Applied

### 1. Separation of Concerns
- Core handles logic, not I/O
- Plugins handle I/O, not logic
- Main handles wiring only

### 2. Loose Coupling
- Plugins don't import Core classes
- Core doesn't import plugins
- Communication via Protocols

### 3. High Cohesion
- Each module has single responsibility
- Clear boundaries between layers

### 4. Interface Segregation
- Small, focused Protocols
- Plugins implement cleanly

### 5. Factory Pattern
- Config-driven instantiation
- No hardcoded dependencies
- Easy to add new drivers

---

## 🧪 Testing

### Test with Different Regions

```bash
# Edit config.json
regions=("Africa" "Europe" "Asia" "Oceania")
for region in "${regions[@]}"; do
    sed -i "s/\"region\".*/\"region\": \"$region\",/" config.json
    python main.py
done
```

### Test with Different Years

```bash
for year in 2015 2018 2020 2022 2024; do
    sed -i "s/\"year\".*/\"year\": $year,/" config.json
    python main.py
done
```

### Test with Charts

```bash
sed -i 's/"output".*/"output": "chart",/' config.json
python main.py
ls -l out/
```

---

## 📈 Performance Notes

- **CSV Loading**: ~50ms for full GDP dataset
- **Analytics Computation**: ~100ms
- **Console Output**: <10ms
- **Chart Generation**: ~500ms (matplotlib overhead)

---

## 🔮 Future Extensions

### New Input Formats
```python
- SQLiteReader (read from database)
- APIReader (fetch from REST endpoint)
- ExcelReader (read .xlsx)
```

### New Output Formats
```python
- HTMLReport (interactive dashboard)
- CSVExport (tabular data export)
- JSONExport (machine-readable)
- EmailReport (automated distribution)
```

### Enhanced Analytics
```python
- Correlation analysis
- Forecasting (trend extrapolation)
- Anomaly detection
- Time-series decomposition
```

---

## 🎓 Learning Outcomes

This Phase demonstrates:

1. **Dependency Inversion** - High-level modules independent of low-level details
2. **Design Patterns** - Factory, Strategy, Adapter
3. **Clean Architecture** - Clear separation, testability
4. **SOLID Principles** - S, O, I, D all applied
5. **Python Protocols** - Structural typing without inheritance
6. **Configuration-Driven Design** - Plugins selected at runtime
7. **Modular Thinking** - Systems as composable units

---

## 📝 Summary

Phase 2 successfully refactors Phase 1 using industry-standard architectural patterns. The system is now:

✅ **Modular** - Independent components  
✅ **Extensible** - Add plugins without core changes  
✅ **Testable** - Inject mock sinks/sources  
✅ **Maintainable** - Clear responsibilities  
✅ **Professional** - Production-ready design  

---

## 👥 Contributors

- Umair Amjad
- Ali Khan Lodhi

---

**Date**: February 28, 2026  
**Version**: 2.0.0  
**Status**: Production Ready
