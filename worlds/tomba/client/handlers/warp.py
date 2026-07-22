from CommonClient import logger

from . import Handler, AbstractHandler
from ...constants import Events, EventStatus, Items, Addresses
from ...sections import Section, Sections
from ...items import ItemHandler
from ...bitutils import Bitmask

warp_masks: dict[Section, Bitmask] = {
    Sections.VILLAGE_OF_ALL_BEGINNING: Bitmask(Addresses.WARP_ENTRY_STATE + 0x00, 0x01),
    Sections.FOREST_OF_ALL_BEGINNING: Bitmask(Addresses.WARP_ENTRY_STATE + 0x00, 0x02),
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
    Sections.PHOENIX_NEST: Bitmask(Addresses.WARP_ENTRY_STATE + 0x06, 0x04),
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


class WarpHandler(AbstractHandler):
    """Handles logic that should be processed when accessing specific area/section of the game"""

    async def unlock_warp(self, section: Section):
        bitmask = warp_masks.get(section, None)
        if bitmask is None:
            logger.error(f"Can't unlock warp for section {section}: This does not exists")
            return

        playsation = self.ctx.tomba.playstation
        await playsation.set_flag(bitmask.address, bitmask.mask)

    def init_handlers(self):
        self.handlers = {Sections.MASAKARI_RIVER: Handler(self.on_masakari_river, 0, 0)}

    async def on_masakari_river(self):
        if self.ctx.tomba.get_event_state(Events.I_CANT_SWIM) is not EventStatus.CLEARED:
            charity_wing = ItemHandler.by_name[Items.CHARITY_WINGS]
            await self.ctx.tomba.receive_item(charity_wing.id, 0)
