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


class MemoryBank:
    address: int
    size: int
    data: bytearray

    def __init__(self, address: int, data: bytearray):
        self.address = address
        self.size = len(data)
        self.data = data

    def read(self, address: int, size: int = 1) -> bytearray | None:
        if address < self.address or address + size > self.address + self.size:
            return None

        offset = address - self.address
        return self.data[offset : offset + size]


class Emulator:
    name: str = "emulator"
    ID: int = -1

    cache: list[MemoryBank] = []
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

    async def create_cache(self, address: int, size: int = 1):
        """Put a memory bank in cache
        Any operation landing in that range will read value from cache"""
        data = await self.read_memory_block(address, size)
        self.cache.append(MemoryBank(address, data))

    def destroy_cache(self):
        self.cache = []

    async def read_memory(self, address: int, size: int = 1) -> bytearray:
        """Performs a cached read"""
        # TODO: This call should be used everywhere, ill leave it for later as only update_locations are using cache
        for memory_bank in self.cache:
            data = memory_bank.read(address, size)

            if data is not None:
                return data

        return await self.async_read_memory(address, size)

    async def write_memory(self, address: int, bytes: bytearray | bytes):
        pass

    async def async_read_memory(self, address: int, size: int = 1) -> bytearray:
        return bytearray(1)

    async def read_memory_block(self, address: int, size: int):
        block = bytearray()
        remaining_size = size
        while remaining_size:
            chunk = await self.read_memory(address + len(block), remaining_size)
            remaining_size -= len(chunk)
            block += chunk

        return block

    async def get_flag(self, address: int, mask: int) -> bool:
        value = (await self.read_memory(address))[0]
        return bool(value & mask)

    async def set_flag(self, address: int, mask: int, set: bool = True):
        value = (await self.read_memory(address))[0]
        original_value = value
        if set:
            value |= mask
        else:
            value &= ~mask

        if value != original_value:
            await self.write_memory(address, value.to_bytes())
