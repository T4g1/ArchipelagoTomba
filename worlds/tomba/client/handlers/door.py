from enum import IntEnum

from . import AbstractHandler


class Doors(IntEnum):
    BACCUS_DOOR = 0x09C258


class DoorState(IntEnum):
    CLOSED = 0x00
    OPEN = 0x02


class DoorHandler(AbstractHandler):
    """Manipulates connection/door between areas/sections"""

    async def set_door(self, door: Doors, state: DoorState):
        await self.tomba.playstation.write_memory(door, state.to_bytes())

    async def open(self, door: Doors):
        await self.set_door(door, DoorState.OPEN)

    async def close(self, door: Doors):
        await self.set_door(door, DoorState.CLOSED)
