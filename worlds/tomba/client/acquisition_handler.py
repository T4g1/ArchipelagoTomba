from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import TombaGame

from .handler import Handler
from ..constants import Items, Events, EventStatus
from ..items import ItemData
from ..events import EventHandler


class AcquisitionHandler:
    """This class defines additional operations upon receiving a specific item from the multiworld"""

    ctx: TombaGame
    handlers: dict[str, Handler]

    def __init__(self, ctx: TombaGame):
        self.ctx = ctx
        self.handlers = {Items.FLOWER_SEEDS: Handler(self.on_flower_seeds, 0, 0)}

    async def handle(self, item: ItemData):
        handler = self.handlers.get(item.name, None)
        if handler:
            await handler.callback()

    async def on_flower_seeds(self):
        """The Flower Seeds event must be started to be able to use the seeds"""
        event = EventHandler.by_name.get(Events.FLOWER_SEEDS)
        assert event is not None
        self.ctx.set_event_state(event, EventStatus.STARTED)
