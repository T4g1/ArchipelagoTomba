import time
from dataclasses import dataclass, field
from typing import Callable, Tuple, Any


@dataclass
class Handler:
    callback: Callable
    interval_ms: float
    last_run: float = 0.0
    args: Tuple = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        self.last_run = time.perf_counter() * 1000
