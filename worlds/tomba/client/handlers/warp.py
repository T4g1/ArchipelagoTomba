from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import TombaGame

from . import Handler
from ...constants import Items, Events, EventStatus
from ...regions import Section
from ...items import ItemData, ItemHandler
from ...events import EventHandler


MASAKARI_RIVER = Section(0x0A, 0x01)


class WarpHandler:
    """Handles logic that should be processed in specific area/section of the game"""

    ctx: TombaGame
    handlers: dict[Section, Handler]

    def __init__(self, ctx: TombaGame):
        self.ctx = ctx
        self.handlers = {
            MASAKARI_RIVER: Handler(self.on_masakari_river, 0, 0)
        }

    async def handle(self, section: Section):
        handler = self.handlers.get(section, None)
        if handler:
            await handler.callback()

    async def on_masakari_river(self):
        if self.ctx.get_event_state(Events.I_CANT_SWIM) is not EventStatus.CLEARED:
            # TODO: Warp player back to village of beginnings
            pass
