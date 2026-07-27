from enum import IntEnum

from . import AbstractHandler


class Doors(IntEnum):
    BACCUS_DOOR = 0x09C258


class DoorState(IntEnum):
    CLOSED = 0x00
    OPEN = 0x02


class DoorsHandler(AbstractHandler):
    """Manipulates connection/door between areas/sections"""

    def set_door(self, door: Doors, state: DoorState):
        self.tomba.playstation.write_memory(door, state.to_bytes())

    def open(self, door: Doors):
        self.set_door(door, DoorState.OPEN)

    def close(self, door: Doors):
        self.set_door(door, DoorState.CLOSED)
