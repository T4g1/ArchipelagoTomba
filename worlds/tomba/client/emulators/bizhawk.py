from worlds._bizhawk import (
    BizHawkContext,
    connect,
    get_script_version,
    get_hash,
    get_system,
    ConnectionStatus,
    ping,
    SyncError,
    RequestFailedError,
    read,
    write,
)

from .emulator import Emulator, EmulatorStatus, CORE_TYPE, InvalidEmulatorStateError
from ... import options


class BizHawk(Emulator):
    ID: int = options.Emulator.option_bizhawk
    name: str = "BizHawk"

    ctx: BizHawkContext

    def __init__(self, address, port) -> None:
        self.ctx = BizHawkContext()

    async def connect(self) -> bool:
        try:
            return await connect(self.ctx)
        except Exception:
            return False

    async def get_version(self):
        try:
            return str(await get_script_version(self.ctx))
        except Exception:
            raise InvalidEmulatorStateError("BizHawk: Unable to get version")

    async def get_status(self):
        try:
            core_type = await get_system(self.ctx)
            rom_crc = await get_hash(self.ctx)

            status = EmulatorStatus.UNKNOWN
            if self.ctx.connection_status is ConnectionStatus.CONNECTED:
                if rom_crc != "":
                    status = EmulatorStatus.PLAYING
                else:
                    status = EmulatorStatus.CONTENTLESS

            if core_type == "PSX":
                core_type = CORE_TYPE

            return (
                status,
                core_type,
                "?",
                rom_crc,
            )
        except Exception:
            raise InvalidEmulatorStateError("BizHawk: Unable to get status")

    async def keep_alive(self):
        try:
            await ping(self.ctx)
        except (SyncError, RequestFailedError):
            raise InvalidEmulatorStateError("BizHawk: Unable to ping")

    async def write_memory(self, address, bytes: bytearray | bytes):
        try:
            await write(self.ctx, [(address, bytes, "")])
        except Exception:
            raise InvalidEmulatorStateError(f"BizHawk: Unable to write at {hex(address)}")

    async def async_read_memory(self, address: int, size: int = 1) -> bytearray:
        try:
            result = await read(self.ctx, [(address, size, "")])
            return bytearray(b"".join(result))
        except Exception:
            raise InvalidEmulatorStateError(f"BizHawk: Unable to read at {hex(address)}")
