import asyncio

from . import bizhawk_connect
from ..emulators.emulator import Emulator
from ...sections import Sections, Section
from ..handlers.transition import Entrance

MAX_ENTRANCE_COUNT = 30


async def extract_entrances(psx: Emulator, section: Section) -> list[Entrance]:
    entrances = []
    entrance_address = await Entrance.compute_entrances_array(psx, section)
    count = 0
    while count < MAX_ENTRANCE_COUNT:
        entrance_data = await psx.read_memory_block(entrance_address, Entrance.SIZE)
        entrance = Entrance(entrance_address, entrance_data)

        if entrance.animation > 0x10:
            break
        if entrance.section.area_id > 0x20:
            break
        if entrance.section.section_id > 0x20:
            break
        if entrance.spawn > 0x20:
            break

        entrances.append(entrance)

        entrance_address += Entrance.SIZE
        count += 1

    return entrances


async def main():
    psx = await bizhawk_connect()

    for section in Sections.all_sections():
        print(f"Entrances in section {section}:")
        try:
            entrances = await extract_entrances(psx, section)
            for i in range(len(entrances)):
                entrance = entrances[i]

                print(f"* ID 0x{i:02X}: {entrance}")
        except AttributeError as exception:
            print(exception)


if __name__ == "__main__":
    asyncio.run(main())
