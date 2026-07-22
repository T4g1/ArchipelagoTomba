from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import TombaContext
else:
    TombaContext = object

from CommonClient import ClientCommandProcessor

from ..constants import EventStatus, Items, SFX
from ..items import ItemHandler
from ..events import EventHandler
from .handlers.warp import warp_masks


class TombaCommandProcessor(ClientCommandProcessor):
    ctx: TombaContext

    async def _cmd_add(self, game_id: str):
        """Add an item by game ID"""
        if isinstance(self.ctx, TombaContext):
            item = ItemHandler.by_game_id.get(int(game_id, 16), None)
            if item is not None:
                await self.ctx.tomba.receive_item(item.id, 0)

    def _cmd_start(self, event_id: str):
        """Start an event"""
        if isinstance(self.ctx, TombaContext):
            event = EventHandler.by_id[int(event_id, 16)]
            self.ctx.tomba.set_event_state(event, EventStatus.STARTED)

    def _cmd_clear(self, event_id: str):
        """Clear an event"""
        if isinstance(self.ctx, TombaContext):
            event = EventHandler.by_id[int(event_id, 16)]
            self.ctx.tomba.set_event_state(event, EventStatus.CLEARED)

    def _cmd_forget(self, event_id: str):
        """Forget an event"""
        if isinstance(self.ctx, TombaContext):
            event = EventHandler.by_id[int(event_id, 16)]
            self.ctx.tomba.set_event_state(event, EventStatus.UNDISCOVERED)

    async def _cmd_ap(self):
        """Adds 50,000 AP"""
        if isinstance(self.ctx, TombaContext):
            ap_score = await self.ctx.tomba.get_ap_score()
            self.ctx.tomba.set_ap_score(ap_score + 50000)

    async def _cmd_fart(self):
        """Fart"""
        if isinstance(self.ctx, TombaContext):
            self.ctx.tomba.play_sfx(SFX.FART)

    async def _cmd_warp(self):
        """Unlock all warp targets and gives a charity wing"""
        if isinstance(self.ctx, TombaContext):
            for section in warp_masks.keys():
                await self.ctx.tomba.warp_hanlder.unlock_warp(section)

            item = ItemHandler.by_name[Items.CHARITY_WINGS]
            await self.ctx.tomba.receive_item(item.id, 0)
