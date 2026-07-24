from dataclasses import dataclass

from CommonClient import logger

from . import AbstractHandler
from ... import constants
from ...constants import Addresses, CustomCommand
from ...items import ItemData, ItemHandler, ItemException, ItemBehavior
from ...sections import Section
from ...locations import LocationHandler


@dataclass
class FoundItem:
    item: ItemData
    camera_horizontal: int
    camera_vertical: int
    section: Section

    @staticmethod
    def from_bytes(data: bytearray):
        # Item Structure:
        # * ITEM_ID: 1
        # * CAMERA_H: 2
        # * CAMERA_V: 2
        # * AREA: 1
        # * SECTION: 1
        game_id = data[0]
        item = ItemHandler.by_game_id.get(game_id, None)
        if item is None:
            raise ItemException(f"Player got an unknown item game ID: {game_id}")

        return FoundItem(
            item=item,
            camera_horizontal=int.from_bytes(data[1:3], byteorder="little", signed=False),
            camera_vertical=int.from_bytes(data[3:5], byteorder="little", signed=False),
            section=Section(data[5], data[6]),
        )


class ItemCheckHandler(AbstractHandler):
    """This class defines additional operations upon receiving a specific item from the multiworld"""

    found_items: list[FoundItem] = []

    async def get_found_items_counter(self) -> int:
        return (await self.tomba.playstation.async_read_memory(Addresses.FOUND_ITEMS_STACK_SIZE))[0]

    async def get_found_items_stack(self) -> list[FoundItem]:
        count = await self.get_found_items_counter()
        data = await self.tomba.playstation.read_memory_block(
            Addresses.FOUND_ITEMS_STACK, count * constants.FOUND_ITEM_STRUCTURE_SIZE
        )

        found_items = []
        for i in range(count):
            start_index = i * constants.FOUND_ITEM_STRUCTURE_SIZE
            item_data = data[start_index : start_index + constants.FOUND_ITEM_STRUCTURE_SIZE]
            found_items.append(FoundItem.from_bytes(item_data))
        return found_items

    async def get_pending_found_items(self) -> list[FoundItem] | None:
        """Give list of found items from the game.

        Returns:
            list[int]: The list of item collected by the player.
            None: If we can't read it yet (not patched or emulator issue)
        """
        if not await self.tomba.patcher.is_patched():
            return None

        if await self.has_pending_clear_obtained_items():
            # Wait until the emulator has cleared the stack before processing it again
            return []

        return await self.get_found_items_stack()

    async def request_clear_obtained_items(self):
        await self.tomba.set_command(CustomCommand.CLEAR_STACK)

    async def has_pending_clear_obtained_items(self) -> bool:
        return bool(await self.tomba.get_command(CustomCommand.CLEAR_STACK))

    async def update_found_items(self):
        """Update the list of found items to be processed"""
        newly_found_items = await self.get_pending_found_items()
        if newly_found_items is None:
            return

        for found_item in newly_found_items:
            self.found_items.append(found_item)

        if len(newly_found_items):
            await self.request_clear_obtained_items()

    async def process_found_items(self):
        # TODO: If the client crashes while found_items is not empty, those are lost forever
        if len(self.found_items) <= 0:
            return

        item = self.found_items.pop(0)
        if not await self.on_item_get(item):
            # Put back the item in the queue if it fails to process
            self.found_items.append(item)

    async def on_item_get(self, found_item: FoundItem) -> bool:
        item = found_item.item
        if item.behavior is ItemBehavior.ORIGINAL:
            return await self.tomba.inventory_handler.receive_item(item, 0)

        location_ids = LocationHandler.filter_and_sort(
            item, found_item.section, found_item.camera_horizontal, found_item.camera_vertical
        )
        if location_ids is None:
            logger.error(f"Player got an item with no location: {item.name}")
            # TODO: Should be removed for release so player can't get unintended items
            return await self.tomba.inventory_handler.receive_item(item, 0)

        first_unchecked = next((id for id in location_ids if id not in self.ctx.checked_locations), None)

        location_id = first_unchecked
        if location_id is None:
            logger.error(f"Player has found {item.name} but there are no location left to send it.")
            logger.debug(f"Candidates were: {location_ids}")
            return True

        logger.debug(f"Sending location check to server for {location_id}")
        await self.ctx.check_locations([location_id])
        return True
