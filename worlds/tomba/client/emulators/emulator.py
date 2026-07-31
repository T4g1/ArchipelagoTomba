from enum import Enum
from socket import socket as SocketType


class EmulatorException(Exception):
    pass


class EmulatorDisconnectError(EmulatorException):
    pass


class InvalidEmulatorStateError(EmulatorException):
    pass


class BadEmulatorResponse(EmulatorException):
    pass


class EmulatorStatus(Enum):
    UNKNOWN = 1
    PAUSED = 2
    PLAYING = 3
    CONTENTLESS = 3


CORE_TYPE = "playstation"
KEEP_ALIVE_INTERVAL = 4000  # In ms: Determined by BizHawk which has a timeout of 5 seconds


class Emulator:
    name: str = "emulator"
    ID: int = -1

    cache = []
    last_cache_read = None
    socket: SocketType

    def __init__(self, address, port) -> None:
        pass

    async def keep_alive(self):
        pass

    async def connect(self) -> bool:
        return True

    async def get_version(self) -> str:
        return ""

    async def get_status(self) -> tuple[EmulatorStatus, str, str, bytes]:
        return (EmulatorStatus.UNKNOWN, "", "", bytes())

    async def write_memory(self, address: int, bytes: bytearray | bytes):
        pass

    async def async_read_memory(self, address: int, size: int = 1) -> bytearray:
        return bytearray(1)

    async def read_memory_block(self, address: int, size: int):
        block = bytearray()
        remaining_size = size
        while remaining_size:
            chunk = await self.async_read_memory(address + len(block), remaining_size)
            remaining_size -= len(chunk)
            block += chunk

        return block

    async def get_flag(self, address: int, mask: int) -> bool:
        value = (await self.async_read_memory(address))[0]
        return bool(value & mask)

    async def set_flag(self, address: int, mask: int, set: bool = True):
        value = (await self.async_read_memory(address))[0]
        if set:
            value |= mask
        else:
            value &= ~mask
        await self.write_memory(address, value.to_bytes())
