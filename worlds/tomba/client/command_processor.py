from __future__ import annotations
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from .client import TombaContext
else:
    TombaContext = object

from CommonClient import ClientCommandProcessor, logger

from ..constants import EventStatus, Items, SFX, Addresses
from ..items import ItemHandler
from ..events import EventHandler
from ..locations import LocationHandler, ItemLocData
from ..helpers import codify
from .handlers.warp import warp_masks
from .debug.entity import EntityHandler


class TombaCommandProcessor(ClientCommandProcessor):
    ctx: TombaContext

    async def _cmd_deathlink(self):
        """Toggle deathlink on/off"""
        if isinstance(self.ctx, TombaContext):
            self.ctx.deathlink_status = not self.ctx.deathlink_status

    async def _cmd_ap(self):
        """Adds 50,000 AP"""
        if isinstance(self.ctx, TombaContext):
            ap_score = await self.ctx.tomba.get_ap_score()
            await self.ctx.tomba.set_ap_score(ap_score + 50000)

    async def _cmd_fart(self):
        """Fart: This will not be a fart in every area of the game due to how the game handles SFX"""
        if isinstance(self.ctx, TombaContext):
            await self.ctx.tomba.play_sfx(SFX.FART)

    async def _cmd_add(self, game_id: str):
        """DEBUG: Add an item by game ID"""
        if isinstance(self.ctx, TombaContext):
            item = ItemHandler.by_game_id.get(int(game_id, 16), None)
            if item is not None:
                await self.ctx.tomba.inventory_handler.give_item(item)

    async def _cmd_start(self, event_id: str):
        """DEBUG: Start an event"""
        if isinstance(self.ctx, TombaContext):
            event = EventHandler.by_id[int(event_id, 16)]
            await self.ctx.tomba.events_handler.set_event_state(event, EventStatus.STARTED)

    async def _cmd_clear(self, event_id: str):
        """DEBUG: Clear an event"""
        if isinstance(self.ctx, TombaContext):
            event = EventHandler.by_id[int(event_id, 16)]
            await self.ctx.tomba.events_handler.set_event_state(event, EventStatus.CLEARED)

    async def _cmd_forget(self, event_id: str):
        """DEBUG: Forget an event"""
        if isinstance(self.ctx, TombaContext):
            event = EventHandler.by_id[int(event_id, 16)]
            await self.ctx.tomba.events_handler.set_event_state(event, EventStatus.UNDISCOVERED)

    async def _cmd_corrupt(self):
        """DEBUG: Corrupt all areas"""
        if isinstance(self.ctx, TombaContext):
            await self.ctx.tomba.playstation.write_memory(Addresses.PURIFICATION_FLAGS, bytes([0x00]))

    async def _cmd_purify(self):
        """DEBUG: Purify all areas"""
        if isinstance(self.ctx, TombaContext):
            await self.ctx.tomba.playstation.write_memory(Addresses.PURIFICATION_FLAGS, bytes([0xFF]))

    async def _cmd_warp(self):
        """DEBUG: Unlock all warp targets and gives a charity wing"""
        if isinstance(self.ctx, TombaContext):
            for section in warp_masks.keys():
                await self.ctx.tomba.warp_hanlder.unlock_warp(section)

            item = ItemHandler.by_name[Items.CHARITY_WINGS]
            await self.ctx.tomba.inventory_handler.give_item(item)

    async def _cmd_check(self, location_id: str):
        """DEBUG: Manualy check a location for debug purposes"""
        id = int(location_id)
        await self.ctx.check_locations([id])

    async def _cmd_debug(self):
        """DEBUG: List all locations and IDs"""
        if isinstance(self.ctx, TombaContext):
            for location in LocationHandler.location_table:
                logger.info(f"{location.id}: {location.name}")

    async def _cmd_popup(self):
        """DEBUG: Debug popup message"""
        if isinstance(self.ctx, TombaContext):
            test_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            await self.ctx.tomba.popup_handler.print(test_string.upper())
            await self.ctx.tomba.popup_handler.print(test_string.lower())
            await self.ctx.tomba.popup_handler.print("0123456789*+!?. ,'/")

    async def _cmd_entity(self):
        """DEBUG: List loaded entities informations"""
        if isinstance(self.ctx, TombaContext):
            entities = await EntityHandler.load_entities(self.ctx.tomba.playstation)
            for entity in entities:
                if entity.occupied <= 0x00:
                    continue

                logger.info(entity)

    async def _cmd_patch(self):
        """DEBUG: Force re-patch"""
        if isinstance(self.ctx, TombaContext):
            await self.ctx.tomba.patcher._patch()

    async def _cmd_replay(self):
        """DEBUG: Replay every checked event and remove location with bitmask from the current game"""
        if isinstance(self.ctx, TombaContext):
            for id in self.ctx.checked_locations:
                location = LocationHandler.by_id[id]
                if location.name.endswith("Cleared"):
                    await self.ctx.tomba.events_handler.clear(location.name[: -len(" Cleared")])
                elif location.at is not None:
                    await self.ctx.tomba.playstation.set_flag(location.at.address, location.at.mask)

    async def _cmd_disable(self, type: str):
        """DEBUG: Disable entity type"""
        if isinstance(self.ctx, TombaContext):
            await EntityHandler.disable(self.ctx.tomba.playstation, int(type, 16))

    async def _cmd_poptracker(self, type: str):
        """Export data for Poptracker"""
        if isinstance(self.ctx, TombaContext):
            if type == "item":
                for item in ItemHandler.item_table:
                    name = codify(item.name)
                    if item.countable:
                        print(f'    [BASE_ITEM_ID + {item.id}] = {{ {{ "{name}", nil, {item.amount} }} }},')
                    else:
                        print(f'    [BASE_ITEM_ID + {item.id}] = {{ {{ "{name}" }} }},')

            elif type == "location":
                for location in LocationHandler.location_table:
                    name = codify(location.name)
                    if not isinstance(location, ItemLocData):
                        name = name.replace("_cleared", "")
                        name = "event_" + name
                    else:
                        name = f"@{location.base_name}/{location.name}"

                    print(f'    [BASE_LOCATION_ID + {location.id}] = {{ {{ "{name}" }} }},')

            elif type == "check":
                locations = []

                for location in LocationHandler.location_table:
                    if not isinstance(location, ItemLocData):
                        continue

                    location_json = {
                        "name": location.base_name,
                        "map_locations": [{"map": "village_of_all_beginnings", "x": 0, "y": 0}],
                        "sections": [{"name": location.name}],
                    }

                    locations.append(location_json)

                for location in locations:
                    print(f"    {json.dumps(location)},")
