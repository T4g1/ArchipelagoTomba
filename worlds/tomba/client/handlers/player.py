from . import AbstractHandler
from ...constants import Addresses


class PlayerHandler(AbstractHandler):
    """Handles player methods"""

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
        await psx.write_memory(Addresses.PV_CURRENT, pv_max.to_bytes())
