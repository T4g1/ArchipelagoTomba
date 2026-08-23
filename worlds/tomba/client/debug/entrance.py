import asyncio

from . import bizhawk_connect
from ..emulators.emulator import Emulator
from ...sections import Sections, Section
from ...bitutils import TypeSize, read_int, is_address

AREAS_ARRAY_ADDRESS = 0x07C54C


class Entrance:
    SIZE = 0x08

    address: int
    raw: bytearray
    unknown: int
    animation: int
    section: Section
    spawn: int

    def __init__(self, address: int, raw: bytearray):
        self.address = address
        self.load(raw)

    def load(self, raw: bytearray):
        self.raw = raw
        self.unknown = read_int(raw, 0, TypeSize.WORD, byteorder="big")
        self.animation = raw[4]
        self.section = Sections.get(Section(raw[5], raw[6]))
        self.spawn = raw[7]

    def __str__(self) -> str:
        return f"Entrance {self.address:08X} to {self.section} at spawn {self.spawn} with {self.animation:02X} method ({self.unknown:08X})"


async def extract_entrances(psx: Emulator, section: Section) -> list[Entrance]:
    entrances = []

    sections_array = await psx.read_int(AREAS_ARRAY_ADDRESS + section.area_id * TypeSize.WORD)
    if not is_address(sections_array):
        raise AttributeError(f"sections array is not loaded: {sections_array:08X}")

    entrances_array = await psx.read_int(sections_array + section.section_id * TypeSize.WORD)
    if not is_address(entrances_array):
        raise AttributeError(f"entrances array is not loaded: {entrances_array:08X}")

    entrance_address = entrances_array
    while True:
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

    return entrances


async def main():
    psx = await bizhawk_connect()

    for section in Sections.all_sections():
        print(f"Entrances in section {section}:")
        try:
            entrances = await extract_entrances(psx, section)
            for i in range(len(entrances)):
                entrance = entrances[i]

                print(f"ID {i}: {entrance}")
        except AttributeError as exception:
            print(exception)


if __name__ == "__main__":
    asyncio.run(main())
