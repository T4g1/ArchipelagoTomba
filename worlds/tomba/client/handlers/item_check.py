from dataclasses import dataclass

from CommonClient import logger

from . import Handler, AbstractHandler
from ... import constants
from ...constants import Addresses, CustomCommand, Locations, Regions
from ...items import ItemData, ItemHandler, ItemException, ItemBehavior
from ...sections import Section
from ...locations import LocationHandler, get_name


@dataclass
class FoundItem:
    item: ItemData
    camera_horizontal: int
    camera_vertical: int
    section: Section

    @staticmethod
    def from_bytes(data: bytearray):
        # Item Structure:
        # * CAMERA_H: 2
        # * CAMERA_V: 2
        # * ITEM_ID: 1
        # * AREA: 1
        # * SECTION: 1
        game_id = data[4]
        item = ItemHandler.by_game_id.get(game_id, None)
        if item is None:
            raise ItemException(f"Player got an unknown item game ID: {game_id}")

        return FoundItem(
            item=item,
            camera_horizontal=int.from_bytes(data[0:2], byteorder="little", signed=False),
            camera_vertical=int.from_bytes(data[2:4], byteorder="little", signed=False),
            section=Section(data[5], data[6]),
        )


class ItemCheckHandler(AbstractHandler):
    """This class defines additional operations upon receiving a specific item from the multiworld"""

    found_items: list[FoundItem] = []

    def init_handlers(self):
        self.handlers = {get_name(Locations.GOLDEN_FRUIT, Regions.BACCUS_VILLAGE): Handler(self.on_golden_fruit)}

    async def on_golden_fruit(self):
        """Trigger locations from Some Cheese Please"""
        await self.check(Locations.SOME_CHEESE_PLEASE_1, Regions.BACCUS_VILLAGE)
        await self.check(Locations.SOME_CHEESE_PLEASE_2, Regions.BACCUS_VILLAGE)

    async def check(self, location_name: str, region_name: str):
        location = LocationHandler.by_name.get(get_name(location_name, region_name), None)
        assert location is not None
        await self.ctx.check_locations([location.id])

    async def get_found_items_counter(self) -> int:
        return (await self.tomba.playstation.async_read_memory(Addresses.FOUND_ITEMS_STACK_SIZE))[0]

    async def get_found_item(self) -> FoundItem | None:
        """Ask the game for any found item.

        Returns:
            FoundItem: Informations about the next item found to be processed.
            None: If we can't read it yet (not patched or emulator issue)
        """
        if not await self.tomba.patcher.is_patched():
            return None

        # Do not process until it's popped
        if await self.has_pending_pop_stack():
            return None

        count = await self.get_found_items_counter()
        if count <= 0:
            return None

        data = await self.tomba.playstation.read_memory_block(
            Addresses.FOUND_ITEMS_STACK, constants.FOUND_ITEM_STRUCTURE_SIZE
        )

        return FoundItem.from_bytes(data)

    async def request_pop_stack(self):
        await self.tomba.set_command(CustomCommand.POP_STACK)

    async def has_pending_pop_stack(self) -> bool:
        return bool(await self.tomba.get_command(CustomCommand.POP_STACK))

    async def update_found_items(self):
        """Process the items found in game"""
        found_item = await self.get_found_item()
        if found_item is None:
            return

        if await self.on_item_get(found_item):
            # Pop the stack upon success
            await self.request_pop_stack()

    async def on_item_get(self, found_item: FoundItem) -> bool:
        item = found_item.item
        logger.debug(f"Player has found {item.name}")

        if item.behavior is ItemBehavior.ORIGINAL:
            logger.debug(f"Normal pickup for {item.name} (not a randomized location)")
            return await self.tomba.inventory_handler.receive_item(item, 0)

        locations = LocationHandler.filter_and_sort(
            item, found_item.section, found_item.camera_horizontal, found_item.camera_vertical
        )
        if locations is None:
            logger.error(f"Player got an item with no location: {item.name}")
            logger.debug(
                f"Found item: {found_item.section}, x={found_item.camera_horizontal}, y={found_item.camera_vertical}"
            )
            # TODO: Should be removed for release so player can't get unintended items
            return await self.tomba.inventory_handler.receive_item(item, 0)

        first_unchecked = next(
            (location for location in locations if location.id not in self.ctx.checked_locations), None
        )

        location = first_unchecked
        if location is None:
            logger.error(f"Player has found {item.name} but there are no location left to send it.")
            logger.debug(
                f"Found item: {found_item.section}, x={found_item.camera_horizontal}, y={found_item.camera_vertical}"
            )
            logger.debug(f"Candidates were: {[location.name for location in locations]}")
            return True

        logger.debug(f"Sending location check to server for {location.id}: {location.name}")
        await self.ctx.check_locations([location.id])

        await self.handle(location.name)
        return True
