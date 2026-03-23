# Phase 3 - Generic Concurrent Real-Time Pipeline

This phase extends Phase 2 into a fully generic, concurrent, config-driven pipeline.

## Main Entry
- `main.py`

## Folder Layout

```text
Phase3/
├── main.py
├── config.json
├── readme.txt
├── requirements.txt
├── core/
│   ├── contracts.py
│   ├── functional.py
│   ├── workers.py
│   └── aggregator.py
├── plugins/
│   ├── inputs.py
│   └── outputs.py
├── monitoring/
│   └── telemetry.py
├── data/
│   └── training_climate_data.csv
├── out/
└── design/
    ├── class_diagram.puml
    ├── sequence_diagram.puml
    ├── class_diagram.png
    └── sequence_diagram.png
```

## Features Implemented

1. **Generic schema mapping** from config (`source_name -> internal_mapping -> data_type`).
2. **Producer-Consumer multiprocessing** with bounded queues.
3. **Scatter-Gather** core:
   - Multiple stateless verifier workers (scatter)
   - Single re-sequencing + running-average aggregator (gather)
4. **Functional Core, Imperative Shell**:
   - Functional: `verify_signature`, `update_running_average`
   - Imperative: process orchestration, queue and stream state
5. **Observer pattern telemetry**:
   - `PipelineTelemetry` polls queue sizes
   - `RealTimeDashboard` subscribes as observer
   - Green/Yellow/Red backpressure states

## Detailed Design Entities (Class Diagram Coverage)

This section documents all classes/entities represented in `design/class_diagram.puml`.

### 1) Contracts (`core/contracts.py`)

- `InputPort` (Protocol)
   - Method: `run() -> None`
- `StatelessProcessor` (Protocol)
   - Method: `run() -> None`
- `AggregationProcessor` (Protocol)
   - Method: `run() -> None`
- `TelemetryObserver` (Protocol)
   - Method: `on_telemetry(snapshot: Dict[str, Any]) -> None`

### 2) Functional Core (`core/functional.py`)

- `FunctionalCore` (utility representation in diagram)
   - `normalize_metric_value(value: float) -> str`
   - `generate_signature(raw_value_str: str, key: str, iterations: int) -> str`
   - `verify_signature(packet: Dict, secret_key: str, iterations: int) -> bool`
   - `update_running_average(window: Deque, new_value: float, window_size: int) -> Tuple`

### 3) Input Plugin (`plugins/inputs.py`)

- `GenericInputProducer`
   - Attributes:
      - `dataset_path: str`
      - `schema_columns: List[Dict]`
      - `raw_queue: Queue`
      - `worker_count: int`
      - `input_delay_seconds: float`
   - Methods:
      - `_read_rows() -> List[Dict]`
      - `run() -> None`

### 4) Core Processing (`core/workers.py`, `core/aggregator.py`)

- `StatelessVerifierWorker`
   - Attributes:
      - `worker_id: int`
      - `raw_queue: Queue`
      - `intermediate_queue: Queue`
      - `secret_key: str`
      - `iterations: int`
   - Method:
      - `run() -> None`

- `ResequencingAggregator`
   - Attributes:
      - `intermediate_queue: Queue`
      - `processed_queue: Queue`
      - `worker_count: int`
      - `window_size: int`
   - Internal behavior in diagram:
      - `_flush_available_from_expected() : int` (modeled helper)
   - Method:
      - `run() -> None`

### 5) Output Plugin (`plugins/outputs.py`)

- `RealTimeDashboard`
   - Attributes:
      - `processed_queue: Queue`
      - `output_dir: str`
      - `visuals_config: Dict`
      - `telemetry_snapshot: Dict`
      - `time_points: List[float]`
      - `metric_values: List[float]`
      - `running_averages: List[float]`
      - `final_records: List[Dict]`
      - `max_points: int`
      - `render_every_n_frames: int`
   - Methods:
      - `on_telemetry(snapshot: Dict) -> None`
      - `_render(frame_index: int) -> None`
      - `_print_previous_style_summary() -> None`
      - `_render_previous_style_graphs() -> None`
      - `_plot_top_entities_bar() -> None`
      - `_plot_metric_histogram() -> None`
      - `_plot_metric_dotplot() -> None`
      - `_plot_entity_share_pie() -> None`
      - `run() -> None`

### 6) Monitoring (`monitoring/telemetry.py`)

- `PipelineTelemetry`
   - Attributes:
      - `raw_queue: Queue`
      - `intermediate_queue: Queue`
      - `processed_queue: Queue`
      - `queue_max_size: int`
      - `observers: List[TelemetryObserver]`
      - `_running: bool`
      - `_thread: Thread`
   - Methods:
      - `subscribe(observer: TelemetryObserver) -> None`
      - `unsubscribe(observer: TelemetryObserver) -> None`
      - `_snapshot() -> Dict`
      - `_build_metric(size: int) -> Dict`
      - `_run(poll_seconds: float) -> None`
      - `start(poll_seconds: float = 0.25) -> None`
      - `stop() -> None`

### 7) Main Orchestration (`main.py`)

- `Bootstrap` (diagram abstraction of module orchestration)
   - `load_config(config_path: str) -> Dict`
   - `bootstrap() -> None`

### 8) Queue Entities

- `RawQueue` (`mp.Queue`, bounded by `stream_queue_max_size`)
- `IntermediateQueue` (`mp.Queue`, bounded)
- `ProcessedQueue` (`mp.Queue`, bounded)

### 9) Relationships (from class diagram)

- **Implements / Protocol conformance**
   - `GenericInputProducer ..|> InputPort`
   - `StatelessVerifierWorker ..|> StatelessProcessor`
   - `ResequencingAggregator ..|> AggregationProcessor`
   - `RealTimeDashboard ..|> TelemetryObserver`
- **Creation/Composition by orchestrator**
   - `Bootstrap` creates/spawns input, workers (N), aggregator, dashboard, telemetry.
- **Data-flow dependencies**
   - Input writes to `RawQueue`.
   - Workers read `RawQueue`, write `IntermediateQueue`.
   - Aggregator reads `IntermediateQueue`, writes `ProcessedQueue`.
   - Dashboard reads `ProcessedQueue`.
- **Functional dependencies**
   - Worker depends on `verify_signature()`.
   - Aggregator depends on `update_running_average()`.
- **Observer pattern relation**
   - `PipelineTelemetry` notifies observers implementing `TelemetryObserver`.
   - `RealTimeDashboard` receives telemetry snapshots.

## Detailed Runtime Flow (Sequence Diagram Coverage)

This section maps `design/sequence_diagram.puml` into explicit runtime phases.

### Phase 1 - Bootstrap & Spawn

1. User runs `python main.py`.
2. Main loads `config.json` and reads dataset path, schema mapping, processing, and dynamics.
3. Main sets multiprocessing start method to `spawn`.
4. Main creates three bounded queues: raw/intermediate/processed.
5. Main starts 4 process groups (dashboard, aggregator, N workers, input producer).
6. Main initializes telemetry subject, subscribes dashboard, and starts polling.

### Phase 2 - Input Streaming

1. Input process reads dataset (CSV/JSON support).
2. Each row is mapped by schema (`source_name -> internal_mapping`) and cast by type.
3. Mapped packet is pushed into `RawQueue`.
4. Input delay is applied (`input_delay_seconds`).
5. After data end, producer sends `None` sentinel x `worker_count`.

### Phase 3 - Scatter Verification (Parallel Workers)

1. Each worker pulls packet from `RawQueue`.
2. Worker normalizes metric and computes PBKDF2-HMAC signature.
3. If signature is valid, worker emits `{type: verified_packet, packet}` to `IntermediateQueue`.
4. If invalid, packet is dropped.
5. On sentinel, worker emits `{type: worker_done, worker_id}` and exits.

### Phase 4 - Gather, Resequence, Stateful Aggregate

1. Aggregator consumes events from `IntermediateQueue`.
2. For `verified_packet`, it stores by `sequence_id` in pending map.
3. It flushes all contiguous packets from `expected_sequence` onward.
4. Running average is updated with sliding window (`window_size`).
5. Processed packets are emitted to `ProcessedQueue` with computed metric.
6. For `worker_done`, done counter increments.
7. Once all workers are done and pending is drained (including gap-handling jump to min pending key), aggregator sends final `None` sentinel.

### Phase 5 - Output Rendering

1. Dashboard consumes processed packets from `ProcessedQueue`.
2. It updates live arrays (`time_points`, `metric_values`, `running_averages`) and trims to `max_points`.
3. It renders live dashboard frames and writes `out/live_dashboard_latest.png`.
4. On final sentinel, it prints summary and writes additional charts:
    - `summary_01_top_entities_bar.png`
    - `summary_02_metric_histogram.png`
    - `summary_03_metric_dotplot.png`
    - `summary_04_entity_share_pie.png`

### Phase 6 - Observer Telemetry Loop (Concurrent)

1. Telemetry daemon polls queue sizes every ~0.2 seconds.
2. Queue ratios are converted into levels (`green/yellow/red`).
3. Snapshot is pushed to dashboard via `on_telemetry(snapshot)`.
4. Dashboard uses snapshot in telemetry bars.

### Phase 7 - Completion

1. Main waits for input, worker, aggregator, and dashboard processes (`join`).
2. Telemetry is stopped.
3. Main prints pipeline completion message.

## Run

```bash
cd Phase3
python main.py
```

Output files are written to:
- `out/live_dashboard_latest.png` (existing real-time telemetry dashboard)
- `out/summary_01_top_entities_bar.png`
- `out/summary_02_metric_histogram.png`
- `out/summary_03_metric_dotplot.png`
- `out/summary_04_entity_share_pie.png`

Console also prints a final data summary table (record count, metric range, average, and sample rows).

## Config Contract

Pipeline behavior is controlled by `config.json`:
- `dataset_path`
- `pipeline_dynamics.input_delay_seconds`
- `pipeline_dynamics.core_parallelism`
- `pipeline_dynamics.stream_queue_max_size`
- `schema_mapping.columns[]`
- `processing.stateless_tasks` (`pbkdf2_hmac`, iterations, secret key)
- `processing.stateful_tasks.running_average_window_size`
- `visualizations.telemetry`
- `visualizations.data_charts[]`

## Signature Verification Rule

- Raw value is normalized to two decimals.
- Hash uses PBKDF2-HMAC SHA256.
- Password = `secret_key`
- Salt = normalized raw value string
- Iterations from config
- Invalid signatures are dropped before aggregation.

## Unseen Dataset Readiness

To test live grading datasets:
1. Place unseen dataset in `Phase3/data/`
2. Update `config.json` schema mapping and `dataset_path`
3. Run `python main.py`

No core logic changes are required for domain shifts.

## Diagram Generation

PlantUML source is in `design/*.puml`.
If `plantuml` is installed:

```bash
cd design
plantuml class_diagram.puml sequence_diagram.puml
```
