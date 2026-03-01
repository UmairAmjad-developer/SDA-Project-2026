from typing import Protocol, List, Any, runtime_checkable

@runtime_checkable
class DataSink(Protocol):
    """
    Outbound Abstraction: The Core calls this to save data.
    Any Output module must implement this method signature.
    """
    def write(self, records: List[dict]) -> None:
        ...


@runtime_checkable
class PipelineService(Protocol):
    """
    Inbound Abstraction: The Input Module calls this to send data to the Core.
    """
    def execute(self, raw_data: List[Any]) -> None:
        ...
