from __future__ import annotations

import logging
import time
from contextlib import AbstractContextManager
from types import TracebackType

logger = logging.getLogger("quorum.utils.timing")


class DebateTimer(AbstractContextManager):
    def __init__(self) -> None:
        self._start: float | None = None
        self._end: float | None = None
        self.tokens_processed: int = 0

    def __enter__(self) -> DebateTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._end = time.perf_counter()

    @property
    def elapsed_ms(self) -> int:
        if self._start is None or self._end is None:
            return 0
        return int((self._end - self._start) * 1000)

    def benchmark_payload(self) -> dict:
        return {
            "cycle_latency_ms": self.elapsed_ms,
            "agents_parallel": 7,
            "tokens_processed": self.tokens_processed,
            "gpu": "AMD MI300X",
        }
