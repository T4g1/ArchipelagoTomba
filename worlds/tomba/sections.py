from dataclasses import dataclass

purified_sections: dict[int, dict[int, int]] = {
    # Phoenix Mountain
    0x03: {0x04: 0x00, 0x05: 0x01},
    # Baccus Village
    0x05: {0x02: 0x00, 0x03: 0x01},
    # Masakari Jungle
    0x0A: {0x04: 0x00, 0x05: 0x01, 0x06: 0x02, 0x07: 0x03},
}


@dataclass
class Section:
    area_id: int
    section_id: int

    def is_purified(self) -> int:
        """Give the cursed section ID"""
        cursed_sections = purified_sections.get(self.area_id, {})
        return self.section_id in cursed_sections.keys()

    def __members(self):
        section_id = self.section_id
        if self.is_purified():
            section_id = purified_sections[self.area_id][self.section_id]

        return (self.area_id, section_id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Section):
            return self.__members() == other.__members()
        return False

    def __hash__(self) -> int:
        return hash(self.__members())

    def __repr__(self) -> str:
        return f"0x{self.area_id:02x}-0x{self.section_id:02x}"


class Sections(Section):
    NONE = Section(0xFF, 0xFF)

    VILLAGE_OF_ALL_BEGINNING = Section(0x00, 0x00)
    FOREST_OF_ALL_BEGINNING = Section(0x00, 0x01)
    HUNDREDS_YEAR_OLD_MANS_HUT = Section(0x00, 0x03)
    OL_POND = Section(0x00, 0x05)

    FOREST_OF_100_FLOWERS = Section(0x01, 0x00)
    WOBBLY_WARF = Section(0x01, 0x02)
    WATCH_TOWER = Section(0x01, 0x03)
    CHARITY_SQUARE = Section(0x01, 0x04)

    DWARF_VILLAGE = Section(0x02, 0x00)
    UNDERGROUND_MAZE = Section(0x02, 0x03)
    MILLION_YEAR_OLD_MANS_ROOM = Section(0x02, 0x04)
    THE_STRANGE_SMALL_ROOM = Section(0x02, 0x05)

    STORMY_MOUNTAINS = Section(0x03, 0x00)
    LAVA_CAVES = Section(0x03, 0x02)
    PHOENIX_NEST = Section(0x03, 0x03)

    HAUNTED_MANSION_NORTH = Section(0x04, 0x00)
    HAUNTED_MANSION_WEST = Section(0x04, 0x01)
    HAUNTED_MANSION_SOUTH = Section(0x04, 0x02)
    HAUNTED_MANSION_EAST = Section(0x04, 0x03)
    THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x04, 0x0F)

    BACCUS_VILLAGE = Section(0x05, 0x00)

    MUSHROOM_FOREST = Section(0x09, 0x00)

    MASAKARI_JUNGLE = Section(0x0A, 0x00)
    MASAKARI_RIVER = Section(0x0A, 0x01)
    OLD_TREE_HILL = Section(0x0A, 0x02)
    TRICK_VILLAGE = Section(0x0A, 0x03)

    TEN_THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x0A, 0x08)

    Y_CROSSING = Section(0x12, 0x01)
