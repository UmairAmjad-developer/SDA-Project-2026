from typing import List, Any
from core.contracts import PipelineService

class CSVReader:
    def __init__(self, service: PipelineService, path: str):
        self.service = service
        self.path = path

    def read(self) -> None:
        import pandas as pd
        df = pd.read_csv(self.path)
        raw_data = df.to_dict(orient='records')
        self.service.execute(raw_data)

class JSONReader:
    def __init__(self, service: PipelineService, path: str):
        self.service = service
        self.path = path

    def read(self) -> None:
        import json
        with open(self.path, 'r') as f:
            raw_data = json.load(f)
        self.service.execute(raw_data)
