import asyncio

from ..emulators.bizhawk import BizHawk
from ..emulators.emulator import Emulator, EmulatorStatus, CORE_TYPE


async def bizhawk_connect() -> Emulator:
    emulator_address = "127.0.0.1"
    emulator_port = 55355

    emulator = BizHawk(emulator_address, emulator_port)

    print("Waiting on connection to emulator...")

    while True:
        try:
            if not await emulator.connect():
                continue

            _ = await emulator.get_version()
            status, core_type, _, _ = await emulator.get_status()

            if (status == EmulatorStatus.PAUSED or status == EmulatorStatus.PLAYING) and core_type == CORE_TYPE:
                break
        except (BlockingIOError, TimeoutError, ConnectionResetError):
            await asyncio.sleep(1.0)
            pass

    return emulator
