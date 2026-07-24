from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections.abc import Hashable
from typing import Callable, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import TombaContext
    from ..game import TombaGame


@dataclass
class Handler:
    callback: Callable[..., Any]
    interval_ms: float = 0
    last_run: float = 0.0
    args: Tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        self.last_run = time.perf_counter() * 1000


class AbstractHandler:
    """Base class for any handler"""

    ctx: TombaContext
    tomba: TombaGame
    handlers: dict[Hashable, Handler]

    def __init__(self, ctx: TombaContext, tomba: TombaGame):
        self.ctx = ctx
        self.tomba = tomba
        self.handlers = {}

        self.init_handlers()

    def init_handlers(self):
        """Override this to define handlers"""
        pass

    async def handle(self, something: object, *args: Any, **kwargs: Any):
        handler = self.handlers.get(something, None)
        if handler:
            await handler.callback(*args, **kwargs)
