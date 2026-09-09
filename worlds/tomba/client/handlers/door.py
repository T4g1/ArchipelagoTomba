from . import AbstractHandler
from ...bitutils import Bitmask


class Doors:
    BACCUS_DOOR = Bitmask(0x09C258, 0x02)
    FOAB_UNDERGROUND_MAZE_DOOR = Bitmask(0x09C355, 0x01)


class DoorHandler(AbstractHandler):
    """Manipulates connection/door between areas/sections"""

    async def set_door(self, door: Bitmask, open: bool):
        await self.tomba.playstation.set_flag(door.address, door.mask, open)

    async def open(self, door: Bitmask):
        await self.set_door(door, True)

    async def close(self, door: Bitmask):
        await self.set_door(door, False)
