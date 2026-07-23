from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import TombaContext

from CommonClient import logger

from ..constants import (
    EventStatus,
    GameState,
    HudState,
    MenuState,
    CustomCommand,
    Addresses,
    Events,
    Screens,
)
from .handlers.inventory import InventoryHandler
from .handlers.pickup import PickupHandler
from .handlers.warp import WarpHandler
from ..client import retroarch
from ..sections import Sections, Section
from ..locations import LocationHandler
from ..events import EventHandler, EventData
from .patcher import Patcher

CORE_TYPE = "playstation"


class TombaException(Exception):
    pass


class TombaGame:
    """Interface with the game itself"""

    ctx: TombaContext
    patcher: Patcher
    playstation: retroarch.RetroArch
    section: Section
    event_states: bytearray = bytearray(0xFF)
    checked_locations: set[int]

    inventory_handler: InventoryHandler
    pickup_handler: PickupHandler
    warp_hanlder: WarpHandler

    def __init__(self, ctx: TombaContext, retroarch_address="127.0.0.1", retroarch_port=55355):
        self.ctx = ctx

        self.retroarch_address = retroarch_address
        self.retroarch_port = retroarch_port
        self.should_reset_auth = False

        self.status = GameState.UNKNOWN
        self.section: Section = Sections.NONE
        self.screen: Screens = Screens.TITLE_SCREEN
        self.events: bytearray

        self.inventory_handler = InventoryHandler(self.ctx, self)
        self.pickup_handler = PickupHandler(self.ctx, self)
        self.warp_hanlder = WarpHandler(self.ctx, self)

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

    # --------
    # Custom feature patched into the RAM
    # --------

    async def patch_game(self):
        await self.patcher.patch_game()

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
    # Handle victory conditions
    # --------

    async def is_victory(self):
        return (await self.get_event_state(Events.GRANDPAS_BRACELET)) == EventStatus.CLEARED

    async def get_event_state(self, event_name: str) -> EventStatus:
        event = EventHandler.by_name[event_name]
        return EventStatus(self.event_states[event.id])

    def set_event_state(self, event: EventData, status: EventStatus):
        self.playstation.write_memory(Addresses.EVENT_FLAGS + event.id, status.to_bytes())

    async def update_events(self):
        old_states = self.event_states
        new_states = await self.playstation.read_memory_block(Addresses.EVENT_FLAGS, 0xFF)

        self.event_states = new_states

        for id in range(len(new_states)):
            if old_states[id] != new_states[id]:
                event = EventHandler.by_id.get(id, None)
                if event is None:
                    continue

                new_state = new_states[id]
                try:
                    await self.ctx.on_event_update(event, EventStatus(new_state))
                except ValueError:
                    # At least Beginners Dward Language event is expected to have other values as its a multi step event
                    logger.debug(f"Event {event.name} got updated to {new_state} which is not useful")

    async def get_ap_score(self):
        ap_score_raw = await self.playstation.read_memory_block(Addresses.AP_SCORE, 4)
        return int.from_bytes(ap_score_raw, byteorder="little")

    def set_ap_score(self, value: int):
        self.playstation.write_memory(Addresses.AP_SCORE, value.to_bytes(4, byteorder="little"))

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
        old_status = self.status

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

        if old_status != self.status:
            logger.debug(f"Status changed to: {self.status}")

    async def update_section(self):
        area_id = (await self.playstation.async_read_memory(Addresses.SELECTED_AREA))[0]
        section_id = (await self.playstation.async_read_memory(Addresses.SELECTED_SECTION))[0]
        new_section = Section(area_id, section_id)

        if new_section != self.section:
            self.section = new_section
            await self.warp_hanlder.handle(self.section)

    async def prevent_softlock(self):
        if self.screen != Screens.GAME_SCREEN:
            return

        # TODO: Read memory region, localy set flags and write results: 2 calls instead of len(list) * 2
        for location in LocationHandler.with_bitmask:
            assert location.at is not None
            if location.at.on_cheked:
                if location.id in self.ctx.checked_locations:
                    await self.playstation.set_flag(location.at.address, location.at.mask, location.at.target_value)
            else:
                if location.id not in self.ctx.checked_locations:
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
                await self.ctx.on_event_update(event, EventStatus.CLEARED)

    def check_safe_gameplay(self):
        return self.status == GameState.PLAYING

    async def check_win_conditions(self):
        if not self.check_safe_gameplay():
            return

        if await self.is_victory():
            await self.ctx.on_victory()

    async def update_inventory(self):
        await self.inventory_handler.update_inventory()
