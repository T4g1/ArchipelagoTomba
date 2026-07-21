import asyncio
import time
from dataclasses import dataclass
from typing import Callable

from BaseClasses import ItemClassification as IC
from CommonClient import logger

from .. import constants
from ..constants import (
    EventStatus,
    GameState,
    HudState,
    MenuState,
    SFX,
    CustomCommand,
    Addresses,
    Events,
    Screens,
)
from .handler import Handler
from .acquisition_handler import AcquisitionHandler
from ..client import retroarch
from ..regions import Section
from ..locations import LocationHandler
from ..items import ItemHandler, ItemData
from ..events import EventHandler, EventData
from .patcher import Patcher

CORE_TYPE = "playstation"


class TombaException(Exception):
    pass


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
            raise TombaException(f"Player got an unknown item game ID: {game_id}")

        return FoundItem(
            item=item,
            camera_horizontal=int.from_bytes(data[1:3], byteorder="little", signed=False),
            camera_vertical=int.from_bytes(data[3:5], byteorder="little", signed=False),
            section=Section(data[5], data[6]),
        )


class TombaGame:
    """Interface with the game itself"""

    playstation: retroarch.RetroArch
    area_id: int
    section_id: int
    event_states: bytearray = bytearray(0xFF)
    checked_locations: set[int]
    acquisition_handler: AcquisitionHandler

    def __init__(self, on_victory_achieved, on_event_updated, retroarch_address="127.0.0.1", retroarch_port=55355):
        self.retroarch_address = retroarch_address
        self.retroarch_port = retroarch_port
        self.should_reset_auth = False
        self.status = GameState.UNKNOWN
        self.area_id: int = 0
        self.section_id: int = 0
        self.screen: Screens = Screens.TITLE_SCREEN
        self.events: bytearray
        self.on_victory_achieved = on_victory_achieved
        self.on_event_updated = on_event_updated
        self.handlers: list[Handler] = []
        self.acquisition_handler = AcquisitionHandler(self)

    def init_handlers(self):
        self.handlers: list[Handler] = [
            Handler(self.update_status, interval_ms=500),
            Handler(self.patcher.patch_game, interval_ms=1000),
            Handler(self.update_area_and_section, interval_ms=2000),
            Handler(self.prevent_softlock, interval_ms=5000),
        ]

        self.add_handler(self.check_win_conditions, interval_ms=10000, on_victory_achieved=self.on_victory_achieved)
        self.add_handler(self.update_events, interval_ms=2000, on_event_updated=self.on_event_updated)

    def add_handler(self, callback: Callable, interval_ms: float, *args, **kwargs):
        handler = Handler(callback=callback, interval_ms=interval_ms, args=args, kwargs=kwargs)
        self.handlers.append(handler)

    async def wait_for_retroarch_connection(self):
        logger.info("Waiting on connection to Retroarch...")
        self.playstation = retroarch.RetroArch(self.retroarch_address, self.retroarch_port)
        self.patcher = Patcher(self.playstation)

        while True:
            try:
                version = await self.playstation.get_retroarch_version()
                status, core_type, rom_name, _ = await self.playstation.get_retroarch_status()

                if retroarch.is_connected(status) and core_type == CORE_TYPE:
                    break
            except (BlockingIOError, TimeoutError, ConnectionResetError):
                await asyncio.sleep(1.0)
                pass

            await asyncio.sleep(1.0)

        logger.info(f"Connected to Retroarch {version} running {rom_name}")

        self.init_handlers()

    # --------
    # Custom feature patched into the RAM
    # --------

    def play_sfx(self, sfx_id: int):
        logger.debug(f"Playing SFX {sfx_id}")
        self.playstation.write_memory(Addresses.PLAY_SFX, sfx_id.to_bytes())

    async def show_message(self, code: int):
        logger.debug(f"Display message: {code:04x}")
        self.playstation.write_memory(Addresses.MESSAGE, code.to_bytes(2))
        await self.set_command(CustomCommand.SHOW_MESSAGE)

    async def get_command(self, command_mask=0xFF) -> int:
        command = (await self.playstation.async_read_memory(Addresses.CUSTOM_COMMAND))[0]
        return command & command_mask

    async def set_command(self, command_mask):
        command = await self.get_command()
        command |= command_mask

        self.playstation.write_memory(Addresses.CUSTOM_COMMAND, command.to_bytes())

    async def request_clear_obtained_items(self):
        await self.set_command(CustomCommand.CLEAR_STACK)

    async def has_pending_clear_obtained_items(self) -> bool:
        return bool(await self.get_command(CustomCommand.CLEAR_STACK))

    async def get_saved_archipelago_index(self) -> int | None:
        """Give saved last index of item received from Archipelago.

        Returns:
            int: The last successfully processed item index.
            None: If we can't read it yet (not patched or emulator issue)
        """
        if not await self.patcher.is_patched():
            return None

        # Assumes Tomba! set this to zero at game start
        stored_index = await self.playstation.read_memory_block(Addresses.ARCHIPELAGO_RECEIVED_INDEX, 2)
        return int.from_bytes(stored_index, byteorder="big")

    def set_saved_archipelago_index(self, index):
        index = index.to_bytes(2, byteorder="big")
        self.playstation.write_memory(Addresses.ARCHIPELAGO_RECEIVED_INDEX, index)

    # --------
    # Handle in game inventory
    # --------

    async def get_inventory_counter(self) -> int:
        return (await self.playstation.async_read_memory(Addresses.INVENTORY_COUNTER))[0]

    async def get_inventory_stack(self) -> bytearray:
        return await self.playstation.read_memory_block(Addresses.INVENTORY_STACK, constants.INVENTORY_STACK_SIZE)

    async def get_item_amount(self, game_id: int) -> int:
        return (await self.playstation.async_read_memory(Addresses.INVENTORY_ITEM_AMOUNT + game_id))[0]

    async def get_inventory(self) -> list[dict]:
        inventory = []
        inventory_stack = await self.get_inventory_stack()
        inventory_counter = await self.get_inventory_counter()

        item_processed = 0

        for i in range(0, constants.INVENTORY_STACK_SIZE, 4):
            game_id = inventory_stack[i]
            item = ItemHandler.by_game_id.get(game_id, None)
            if item is not None:
                inventory.append(item)

            item_processed += 1
            if item_processed >= inventory_counter:
                return inventory

        return inventory

    # --------
    # Handle in game received items
    # --------

    async def get_found_items_counter(self) -> int:
        return (await self.playstation.async_read_memory(Addresses.FOUND_ITEMS_STACK_SIZE))[0]

    async def get_found_items_stack(self) -> list[FoundItem]:
        count = await self.get_found_items_counter()
        data = await self.playstation.read_memory_block(
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
        if not await self.patcher.is_patched():
            return None

        if await self.has_pending_clear_obtained_items():
            # Wait until the emulator has cleared the stack before processing it again
            return []

        return await self.get_found_items_stack()

    # --------
    # Handle victory conditions
    # --------

    async def is_victory(self):
        return (await self.get_event_state(Events.GRANDPAS_BRACELET)) == EventStatus.CLEARED

    async def get_event_state(self, event_name: str) -> EventStatus:
        event = EventHandler.by_name[event_name]
        return EventStatus(self.event_states[event.id])

    def set_event_state(self, event: EventData, status: EventStatus):
        self.playstation.write_memory(Addresses.EVENT_FLAGS + event.id, status.to_bytes())

    async def update_events(self, on_event_updated):
        old_states = self.event_states
        new_states = await self.playstation.read_memory_block(Addresses.EVENT_FLAGS, 0xFF)

        self.event_states = new_states

        for id in range(len(new_states)):
            if old_states[id] != new_states[id]:
                event = EventHandler.by_id.get(id, None)
                if event is None:
                    continue

                await on_event_updated(event, EventStatus(new_states[id]))

    async def receive_item(self, item_id: int, player) -> bool:
        """Give iem to the player

        Returns:
            True: The player now owns the item or the item is impossible to give to the player
            False: The item has not been given and should be retried (game is not ready to receive items)
        """
        if not self.check_safe_gameplay():
            return False

        inventory_counter = await self.get_inventory_counter()

        # Item stack is limited
        if inventory_counter >= 0xFF:
            logger.warning("Player has too much items: Cannot receive more items")
            return False

        item = ItemHandler.by_id.get(item_id, None)
        if item is None:
            logger.warning(f"Received an unknown item from {player}: ID is {item_id}")
            return True

        inventory_stack = await self.get_inventory_stack()

        has_item_already = item.game_id.to_bytes() in inventory_stack[:inventory_counter]
        should_display_acquired = False

        if item.countable:
            current_amount = await self.get_item_amount(item.game_id)
            has_item_already = has_item_already or current_amount > 0

            new_amount = current_amount + 1
            self.playstation.write_memory(Addresses.INVENTORY_ITEM_AMOUNT + item.game_id, new_amount.to_bytes())

            should_display_acquired = True

        if not has_item_already:
            # Adding an item means shifting the whole stack to the right
            # and putting the item at the first position
            inventory_stack = item.game_id.to_bytes() + inventory_stack[:-1]
            inventory_counter += 1

            self.playstation.write_memory(Addresses.INVENTORY_STACK, inventory_stack)
            self.playstation.write_memory(Addresses.INVENTORY_COUNTER, inventory_counter.to_bytes())

            should_display_acquired = True

        if should_display_acquired:
            logger.debug(f"Received {item.name} from {player}")

            if item.classification is IC.filler:
                self.play_sfx(SFX.FART)
            else:
                self.play_sfx(SFX.ACQUIRED)

        await self.acquisition_handler.handle(item)

        return True

    async def get_menu_state(self):
        return (await self.playstation.async_read_memory(Addresses.MENU_STATE))[0]

    async def get_screen_state(self) -> Screens:
        screen_raw = (await self.playstation.async_read_memory(Addresses.MAIN_SCREEN_STATE))[0]

        try:
            return Screens(screen_raw)
        except Exception:
            logger.debug(f"Unsuported screen state: {screen_raw}")
            return Screens.TITLE_SCREEN

    async def is_hud_visible(self):
        hud_visibility = (await self.playstation.async_read_memory(Addresses.HUD_VISIBILITY))[0]
        hud_visibility_timer = (await self.playstation.async_read_memory(Addresses.HUD_VISIBILITY_TIMER))[0]

        return hud_visibility == HudState.VISIBLE and hud_visibility_timer == HudState.VISIBLE

    async def update_status(self):
        screen = await self.get_screen_state()
        self.screen = screen

        if screen == Screens.GAME_SCREEN:
            if await self.get_menu_state() == MenuState.OPEN:
                self.status = GameState.IN_MENU
            elif await self.is_hud_visible():
                self.status = GameState.PLAYING
            else:
                self.status = GameState.CUTSCENE
        elif screen == Screens.OPTION_SCREEN:
            self.status = GameState.OPTIONS
        elif screen == Screens.TRAILER_SCREEN or screen == Screens.TITLE_SCREEN:
            self.status = GameState.TITLE

    async def update_area_and_section(self):
        self.area_id = (await self.playstation.async_read_memory(Addresses.SELECTED_AREA))[0]
        self.section_id = (await self.playstation.async_read_memory(Addresses.SELECTED_SECTION))[0]

    async def prevent_softlock(self):
        if self.screen != Screens.GAME_SCREEN:
            return

        # TODO: Read memory region, localy set flags and write results: 2 calls instead of len(list) * 2
        for location in LocationHandler.with_bitmask:
            assert location.at is not None
            if location.at.on_cheked:
                if location.id in self.checked_locations:
                    await self.playstation.set_flag(location.at.address, location.at.mask, location.at.target_value)
            else:
                if location.id not in self.checked_locations:
                    await self.playstation.set_flag(location.at.address, location.at.mask, location.at.target_value)

        # Put back the barrel if the event is not discovered
        if await self.get_event_state(Events.WHERE_THE_BARREL_ROLLS) == EventStatus.UNDISCOVERED:
            await self.playstation.set_flag(0x09BD1C, 0x40, False)

        # Fix the Take Out event being softlocked if Hide and Go Seek is already cleared
        if await self.get_event_state(Events.TAKE_OUT) is not EventStatus.CLEARED:
            if await self.get_event_state(Events.HIDE_AND_GO_SEEK) is EventStatus.CLEARED:
                event = EventHandler.by_name.get(Events.TAKE_OUT)
                assert event is not None

                self.set_event_state(event, EventStatus.CLEARED)
                await self.on_event_updated(event, EventStatus.CLEARED)

    def check_safe_gameplay(self):
        return self.status == GameState.PLAYING

    async def check_win_conditions(self, on_victory_achieved):
        if not self.check_safe_gameplay():
            return

        if await self.is_victory():
            await on_victory_achieved()

    async def main_tick(self, checked_locations: set[int]):
        self.checked_locations = checked_locations

        if self.should_reset_auth:
            self.should_reset_auth = False
            raise TombaException("Resetting due to wrong archipelago server")

        current_time = time.perf_counter() * 1000
        for handler in self.handlers:
            if current_time - handler.last_run >= handler.interval_ms:
                await handler.callback(*handler.args, **handler.kwargs)
                handler.last_run = current_time
