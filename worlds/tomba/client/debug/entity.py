import asyncio

from ..emulators.emulator import CORE_TYPE, EmulatorStatus
from ..emulators.bizhawk import BizHawk
from ..entity.entity import (
    EntityHandler,
    GAME_ENTITY_ADDRESS,
    GAME_ENTITY_COUNT,
)
from ..entity.event_entity import (
    EVENT_CHAR_ADDRESS,
    EVENT_CHAR_COUNT,
)


async def main():
    """Primarly used as a tool to reverse"""
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

    entities = await EntityHandler.load_entities(emulator, GAME_ENTITY_ADDRESS, GAME_ENTITY_COUNT)
    for entity in entities:
        if entity.occupied <= 0x00:
            continue

        print(entity)

    entities = await EntityHandler.load_entities(emulator, EVENT_CHAR_ADDRESS, EVENT_CHAR_COUNT)
    for entity in entities:
        if entity.occupied <= 0x00:
            continue

        print(entity)


if __name__ == "__main__":
    asyncio.run(main())
