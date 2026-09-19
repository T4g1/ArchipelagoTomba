from . import AbstractHandler

from ...constants import (
    GameState,
    HudState,
    Addresses,
    GameState1,
    GameState2,
    GameState3,
    Items,
)
from ...items import ItemHandler


class GameStateHandler(AbstractHandler):
    """Handles state changes"""

    previous_status = GameState.TITLE

    async def get_status(self) -> GameState:
        """Called when needed in order to always have the most updated status"""
        state_1 = await self.get_game_state_1()
        status = GameState.UNKNOWN

        if state_1 == GameState1.GAME_SCREEN:
            state_2 = await self.get_game_state_2()
            if state_2 == GameState2.CUTSCENE:
                status = GameState.CUTSCENE
            else:
                state_3 = await self.get_game_state_3()
                if state_3 == GameState3.LOADING:
                    status = GameState.LOADING
                elif state_3 == GameState3.IN_MENU:
                    status = GameState.IN_MENU
                elif await self.is_hud_visible():
                    status = GameState.PLAYING
                elif await self.tomba.inventory_handler.is_accessible():
                    status = GameState.NO_HUD
                else:
                    status = GameState.DIALOGS
        elif state_1 == GameState1.OPTION_SCREEN:
            status = GameState.OPTIONS
        elif state_1 == GameState1.TRAILER_SCREEN or state_1 == GameState1.TITLE_SCREEN:
            status = GameState.TITLE

        return status

    async def get_menu_state(self):
        return (await self.tomba.playstation.async_read_memory(Addresses.MENU_STATE))[0]

    async def get_game_state_1(self) -> GameState1:
        state_raw = (await self.tomba.playstation.async_read_memory(Addresses.GAME_STATE_1))[0]

        try:
            return GameState1(state_raw)
        except Exception:
            return GameState1.TITLE_SCREEN

    async def get_game_state_2(self) -> GameState2:
        state_raw = (await self.tomba.playstation.async_read_memory(Addresses.GAME_STATE_2))[0]

        try:
            return GameState2(state_raw)
        except Exception:
            return GameState2.CUTSCENE

    async def get_game_state_3(self) -> GameState3:
        state_raw = (await self.tomba.playstation.async_read_memory(Addresses.GAME_STATE_3))[0]

        try:
            return GameState3(state_raw)
        except Exception:
            return GameState3.LOADING

    async def is_hud_visible(self):
        hud_visibility = (await self.tomba.playstation.async_read_memory(Addresses.HUD_VISIBILITY))[0]
        hud_visibility_timer = (await self.tomba.playstation.async_read_memory(Addresses.HUD_VISIBILITY_TIMER))[0]

        return hud_visibility == HudState.VISIBLE and hud_visibility_timer == HudState.VISIBLE

    async def is_playing(self, status: GameState | None = None):
        if status is None:
            status = await self.get_status()

        return status == GameState.PLAYING or status == GameState.NO_HUD or status == GameState.DIALOGS

    async def is_in_menu(self, status: GameState | None = None):
        if status is None:
            status = await self.get_status()

        return status == GameState.IN_MENU

    async def has_game_in_progress(self, status: GameState | None = None):
        if status is None:
            status = await self.get_status()

        return await self.is_in_menu(status) or await self.is_playing(status)

    async def update_status(self):
        status = await self.get_status()

        if await self.is_playing(status) and await self.is_in_menu(self.previous_status):
            await self.on_close_menu()

        self.previous_status = status

    async def on_close_menu(self):
        if self.ctx.slot_data.get("entrance_randomization", False):
            # Make sure player has at least one Charity Wings
            charity_wing = ItemHandler.by_name.get(Items.CHARITY_WINGS)
            assert charity_wing is not None

            if await self.tomba.inventory_handler.get_item_amount(charity_wing.game_id) < 1:
                await self.ctx.tomba.inventory_handler.give_item(charity_wing)
