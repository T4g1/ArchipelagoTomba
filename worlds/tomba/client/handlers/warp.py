from typing import Any

from CommonClient import logger

from . import Handler, AbstractHandler
from ...constants import Events, EventStatus, Items, Addresses, Regions, Locations
from ...sections import Section, Sections
from ...items import ItemHandler
from ...events import EventHandler
from ...bitutils import Bitmask

warp_masks: dict[Section, Bitmask] = {
    Sections.VILLAGE_OF_ALL_BEGINNING: Bitmask(Addresses.WARP_ENTRY_STATE + 0x00, 0x01),
    Sections.FOREST_OF_ALL_BEGINNING_PART_1: Bitmask(Addresses.WARP_ENTRY_STATE + 0x00, 0x02),
    Sections.OL_POND: Bitmask(Addresses.WARP_ENTRY_STATE + 0x00, 0x04),
    Sections.HUNDREDS_YEAR_OLD_MANS_HUT: Bitmask(Addresses.WARP_ENTRY_STATE + 0x00, 0x08),
    Sections.FOREST_OF_100_FLOWERS: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x01),
    Sections.DWARF_VILLAGE: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x02),
    Sections.WOBBLY_WARF: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x04),
    Sections.WATCH_TOWER: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x08),
    Sections.CHARITY_SQUARE: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x10),
    Sections.UNDERGROUND_MAZE: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x20),
    Sections.MILLION_YEAR_OLD_MANS_ROOM: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x40),
    Sections.THE_STRANGE_SMALL_ROOM: Bitmask(Addresses.WARP_ENTRY_STATE + 0x02, 0x80),
    Sections.MUSHROOM_FOREST: Bitmask(Addresses.WARP_ENTRY_STATE + 0x04, 0x01),
    Sections.STORMY_MOUNTAINS: Bitmask(Addresses.WARP_ENTRY_STATE + 0x06, 0x01),
    Sections.LAVA_CAVES: Bitmask(Addresses.WARP_ENTRY_STATE + 0x06, 0x02),
    Sections.PHOENIXS_NEST: Bitmask(Addresses.WARP_ENTRY_STATE + 0x06, 0x04),
    Sections.BACCUS_VILLAGE: Bitmask(Addresses.WARP_ENTRY_STATE + 0x08, 0x01),
    Sections.HAUNTED_MANSION_EAST: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0A, 0x01),
    Sections.HAUNTED_MANSION_SOUTH: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0A, 0x02),
    Sections.HAUNTED_MANSION_WEST: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0A, 0x04),
    Sections.HAUNTED_MANSION_NORTH: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0A, 0x08),
    Sections.THOUSAND_YEAR_OLD_MANS_ROOM: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0A, 0x10),
    Sections.MASAKARI_JUNGLE: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0C, 0x01),
    Sections.OLD_TREE_HILL: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0C, 0x02),
    Sections.Y_CROSSING: Bitmask(Addresses.WARP_ENTRY_STATE + 0x0E, 0x01),
    Sections.TRICK_VILLAGE: Bitmask(Addresses.WARP_ENTRY_STATE + 0x10, 0x01),
    Sections.TEN_THOUSAND_YEAR_OLD_MANS_ROOM: Bitmask(Addresses.WARP_ENTRY_STATE + 0x10, 0x02),
}

purified_mask: dict[str, int] = {
    Regions.FOREST_OF_100_FLOWERS: 0x01,
    Regions.STORMY_MOUNTAIN: 0x02,
    Regions.LAVA_CAVES: 0x04,
    Regions.HAUNTED_MANSION: 0x08,
    Regions.BACCUS_VILLAGE: 0x10,
    Regions.MASAKARI_JUNGLE: 0x20,
    Regions.TRICK_VILLAGE: 0x40,
}


class WarpHandler(AbstractHandler):
    """Handles logic that should be processed when accessing specific area/section of the game"""

    leaving_handlers: dict[Section, Handler] = {}

    async def is_purified(self, region: str) -> bool:
        return await self.tomba.playstation.get_flag(Addresses.PURIFICATION_FLAGS, purified_mask[region])

    async def unlock_warp(self, section: Section):
        bitmask = warp_masks.get(section, None)
        if bitmask is None:
            logger.error(f"Can't unlock warp for section {section}: This does not exists")
            return

        playsation = self.ctx.tomba.playstation
        await playsation.set_flag(bitmask.address, bitmask.mask)

    async def handle_leaving(self, section: Section, *args: Any, **kwargs: Any):
        handler = self.leaving_handlers.get(section, None)
        if handler:
            await handler.callback(*args, **kwargs)

    def init_handlers(self):
        # Handlers for when we leave a section
        self.leaving_handlers = {
            Sections.FOREST_OF_ALL_BEGINNING_PART_1: Handler(self.on_forest_of_all_beginning_left),
            Sections.WOBBLY_WARF: Handler(self.on_wobbly_warf_left),
            Sections.HIDDEN_VILLAGE: Handler(self.on_hidden_village_left),
        }

        # Handlers for when we enter a section
        self.handlers = {
            Sections.CIVILIZATION_ROOM: Handler(self.on_haunted_mansion_irregular_entry),
            Sections.THOUSAND_YEAR_OLD_MANS_ROOM: Handler(self.on_haunted_mansion_irregular_entry),
            Sections.MASAKARI_RIVER: Handler(self.on_masakari_river),
            Sections.FOREST_OF_100_FLOWERS: Handler(self.on_forest_of_100_flowers_entry),
        }

    async def on_forest_of_all_beginning_left(self, to: Section):
        # Replace the blue apple if needed
        if not self.ctx.check_handler.is_checked(Locations.BITING_PLANT_FLOWER, Regions.FOREST_OF_ALL_BEGINNINGS):
            await self.tomba.playstation.set_flag(0x09BD00, 0x20, False)

    async def on_wobbly_warf_left(self, to: Section):
        # Put back the barrel if the event is not discovered
        if await self.tomba.events_handler.get_event_state(Events.WHERE_THE_BARREL_ROLLS) is EventStatus.UNDISCOVERED:
            await self.tomba.playstation.set_flag(0x09BD1C, 0x40, False)

    async def on_hidden_village_left(self, to: Section):
        if to.equals(Sections.LAVA_CAVES):
            # TODO: Check spawn location is on top of the cave
            if await self.tomba.events_handler.get_event_state(Events.LAVA_CAVES) is not EventStatus.CLEARED:
                # TODO: This will be a glitched if player has not received Charle's Pants yet
                pass

    async def on_forest_of_100_flowers_entry(self, coming_from: Section):
        if not await self.is_purified(Regions.FOREST_OF_100_FLOWERS):
            return

        logger.debug(f"Tiggerring Hidden Chest in {Regions.FOREST_OF_100_FLOWERS}")

        # Check two missable location from the chest hidden in the tree
        await self.ctx.check_handler.check(Locations.HIDDEN_CHEST_FOREST_100_FLOWER_1, Regions.FOREST_OF_100_FLOWERS)
        await self.ctx.check_handler.check(Locations.HIDDEN_CHEST_FOREST_100_FLOWER_2, Regions.FOREST_OF_100_FLOWERS)

    async def on_haunted_mansion_irregular_entry(self, coming_from: Section):
        # Haunted Mansion will not load correctly if this is not cleared
        event = EventHandler.by_name[Events.A_DRINK_FOR_GROWNUPS]
        await self.tomba.events_handler.set_event_state(event, EventStatus.CLEARED)

        # Prevent softlock when accessing Baccus Lake
        event = EventHandler.by_name[Events.ROAD_TO_BACCUS_LAKE]
        await self.tomba.events_handler.set_event_state(event, EventStatus.CLEARED)

    async def on_masakari_river(self, coming_from: Section):
        if await self.tomba.events_handler.get_event_state(Events.I_CANT_SWIM) is not EventStatus.CLEARED:
            charity_wing = ItemHandler.by_name[Items.CHARITY_WINGS]
            await self.tomba.inventory_handler.receive_item(charity_wing)
