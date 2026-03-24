from multiprocessing import Queue
from queue import Empty
from typing import Dict
from .functional import verify_signature


class StatelessVerifierWorker:
    """
    Scatter node: stateless cryptographic verification.
    Pulls packets from raw queue and pushes verified packets to intermediate queue.
    """

    def __init__(
        self,
        worker_id: int,
        raw_queue: Queue,
        intermediate_queue: Queue,
        secret_key: str,
        iterations: int,
        value_field: str,
        signature_field: str,
    ) -> None:
        self.worker_id = worker_id
        self.raw_queue = raw_queue
        self.intermediate_queue = intermediate_queue
        self.secret_key = secret_key
        self.iterations = iterations
        self.value_field = value_field
        self.signature_field = signature_field

    def run(self) -> None:
        while True:
            try:
                packet = self.raw_queue.get(timeout=1)
            except Empty:
                continue

            if packet is None:
                self.intermediate_queue.put({"type": "worker_done", "worker_id": self.worker_id})
                break

            if verify_signature(
                packet,
                self.secret_key,
                self.iterations,
                self.value_field,
                self.signature_field,
            ):
                self.intermediate_queue.put({"type": "verified_packet", "packet": packet})
