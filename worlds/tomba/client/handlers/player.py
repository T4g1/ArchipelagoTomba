from enum import IntEnum

from . import AbstractHandler
from ...constants import Addresses, CustomCommand


class TombaState(IntEnum):
    NORMAL = 0x00
    LAUGHING = 0x01
    CRYING = 0x02


class PlayerHandler(AbstractHandler):
    """Handles player methods"""

    lives: int = 0
    dying: bool = False

    async def update_deathlink(self):
        """Periodically checks if the player is dead"""
        if not self.ctx.slot_data["deathlink"]:
            return

        current_lives = (await self.tomba.playstation.async_read_memory(Addresses.LIVES))[0]

        if current_lives < self.lives:
            # If dying is true: It means a deathlink triggered this life loss
            if self.dying:
                self.dying = False
            else:
                # Send deathlinks
                await self.ctx.send_death("The evil pigs won")

        # Receive deathlink
        if self.ctx.deathlink_pending:
            await self.tomba.set_command(CustomCommand.KILL_TOMBA)
            self.ctx.deathlink_pending = False

            self.dying = True

        self.lives = current_lives

    async def add_life(self):
        lifes = (await self.tomba.playstation.async_read_memory(Addresses.LIVES))[0]
        lifes = min(lifes + 1, 99)
        await self.tomba.playstation.write_memory(Addresses.LIVES, lifes.to_bytes())

    async def add_vitality(self):
        psx = self.tomba.playstation
        golden_bowl_status = (await psx.async_read_memory(Addresses.GOLDEN_BOWL_STATUS))[0]
        pv_max = (await psx.async_read_memory(Addresses.PV_MAX))[0]

        if golden_bowl_status == 0x00:
            if pv_max >= 0x08:
                pv_max_surplus = (await psx.async_read_memory(Addresses.PV_MAX_SURPLUS))[0] + 1
                await psx.write_memory(Addresses.PV_MAX_SURPLUS, pv_max_surplus.to_bytes())
            else:
                pv_max += 1
        elif pv_max < 0x0F:
            pv_max += 1

        await psx.write_memory(Addresses.PV_MAX, pv_max.to_bytes())
        await self.set_pv(pv_max)

    async def set_pv(self, amount: int):
        await self.tomba.playstation.write_memory(Addresses.PV_CURRENT_DISPLAY, amount.to_bytes())
        await self.tomba.playstation.write_memory(Addresses.PV_CURRENT_REAL, amount.to_bytes())
        await self.tomba.playstation.write_memory(Addresses.PV_CURRENT_COPY, amount.to_bytes())

    async def heal(self):
        """Heal all PV lost"""
        psx = self.tomba.playstation
        pv_max = (await psx.async_read_memory(Addresses.PV_MAX))[0]
        await self.set_pv(pv_max)

        await self.set_status(TombaState.NORMAL)

    async def set_status(self, status: TombaState):
        """Change Tomba! status"""
        await self.tomba.playstation.write_memory(Addresses.TOMBA_STATE, status.to_bytes())
