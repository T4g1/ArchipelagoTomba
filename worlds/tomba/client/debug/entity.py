import asyncio

from . import bizhawk_connect
from ..entity.entity import (
    EntityHandler,
    GAME_ENTITY_ADDRESS,
    GAME_ENTITY_COUNT,
    OBJECT_SLOTS_ADDRESS,
    OBJECT_SLOTS_COUNT,
)
from ..entity.event_entity import (
    EVENT_CHAR_ADDRESS,
    EVENT_CHAR_COUNT,
)


async def main():
    """Primarly used as a tool to reverse"""
    emulator = await bizhawk_connect()

    print("Entities:")
    entities = await EntityHandler.load_entities(emulator, GAME_ENTITY_ADDRESS, GAME_ENTITY_COUNT, is_occupied=True)
    for entity in entities:
        print(entity)

    print("Event cube chars:")
    entities = await EntityHandler.load_entities(emulator, EVENT_CHAR_ADDRESS, EVENT_CHAR_COUNT, is_occupied=True)
    for entity in entities:
        print(entity)

    print("Object slots:")
    entities = await EntityHandler.load_entities(
        emulator, OBJECT_SLOTS_ADDRESS, OBJECT_SLOTS_COUNT, 0x78, is_occupied=True
    )
    for entity in entities:
        print(entity)


if __name__ == "__main__":
    asyncio.run(main())
