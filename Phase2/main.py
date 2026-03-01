import json
import os

class MultiSink:
    """Composite sink that forwards to multiple output drivers."""
    def __init__(self, sinks):
        self.sinks = sinks
    
    def write(self, records):
        for sink in self.sinks:
            sink.write(records)

def bootstrap():
    """Load configuration, wire components, and start pipeline."""
    from core.engine import TransformationEngine
    from plugins.inputs import CSVReader, JSONReader
    from plugins.outputs import ConsoleWriter, ChartWriter

    INPUT_DRIVERS = {"csv": CSVReader, "json": JSONReader}
    OUTPUT_DRIVERS = {"console": ConsoleWriter, "chart": ChartWriter}

    # Find config.json relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    config = json.load(open(config_path))

    input_type = config.get('input', 'csv')
    output_types = config.get('output', 'console')
    
    # Support both single string and list of outputs
    if isinstance(output_types, str):
        output_types = [output_types]
    
    # Create all sinks
    sinks = []
    for output_type in output_types:
        SinkCls = OUTPUT_DRIVERS[output_type]
        # ChartWriter no longer requires or uses an output directory parameter
        sink = SinkCls()
        sinks.append(sink)
    
    # Use MultiSink if multiple outputs, otherwise single sink
    if len(sinks) == 1:
        composite_sink = sinks[0]
    else:
        composite_sink = MultiSink(sinks)
    
    SourceCls = INPUT_DRIVERS[input_type]
    engine = TransformationEngine(composite_sink, config)
    
    # Resolve data path relative to script directory
    data_path = config.get('path')
    if not os.path.isabs(data_path):
        data_path = os.path.join(script_dir, data_path)
    
    source = SourceCls(engine, data_path)

    source.read()

if __name__ == '__main__':
    bootstrap()
