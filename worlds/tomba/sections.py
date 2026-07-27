from dataclasses import dataclass


@dataclass
class Section:
    area_id: int
    section_id: int

    def is_purified(self) -> int:
        """Give the cursed section ID"""
        return self in purified_sections.keys()

    def equals(self, other: object) -> bool:
        """Compare both un-purified versions for equality"""
        if not isinstance(other, Section):
            return False

        this = purified_sections.get(self, self)
        other = purified_sections.get(other, other)

        return this.area_id == other.area_id and this.section_id == other.section_id

    def __hash__(self) -> int:
        return hash((self.area_id, self.section_id))

    def __repr__(self) -> str:
        return f"0x{self.area_id:02x}-0x{self.section_id:02x}"


class Sections(Section):
    NONE = Section(0xFF, 0xFF)

    VILLAGE_OF_ALL_BEGINNING = Section(0x00, 0x00)
    FOREST_OF_ALL_BEGINNING_PART_1 = Section(0x00, 0x01)
    FOREST_OF_ALL_BEGINNING_PART_2 = Section(0x00, 0x02)
    HUNDREDS_YEAR_OLD_MANS_HUT = Section(0x00, 0x03)
    OL_POND = Section(0x00, 0x05)

    FOREST_OF_100_FLOWERS = Section(0x01, 0x00)
    RIGHT_ENTRANCE = Section(0x01, 0x01)
    WOBBLY_WARF = Section(0x01, 0x02)
    WATCH_TOWER = Section(0x01, 0x03)
    CHARITY_SQUARE = Section(0x01, 0x04)

    DWARF_VILLAGE = Section(0x02, 0x00)
    UNDERGROUND_MAZE = Section(0x02, 0x03)
    MILLION_YEAR_OLD_MANS_ROOM = Section(0x02, 0x04)
    THE_STRANGE_SMALL_ROOM = Section(0x02, 0x05)

    STORMY_MOUNTAINS = Section(0x03, 0x00)
    STORMY_MOUNTAINS_SECOND = Section(0x03, 0x01)
    LAVA_CAVES = Section(0x03, 0x02)
    PHOENIX_NEST = Section(0x03, 0x03)
    STORMY_MOUNTAINS_PURIFIED = Section(0x03, 0x04)
    STORMY_MOUNTAINS_SECOND_PURIFIED = Section(0x03, 0x05)

    HAUNTED_MANSION_NORTH = Section(0x04, 0x00)
    HAUNTED_MANSION_WEST = Section(0x04, 0x01)
    HAUNTED_MANSION_SOUTH = Section(0x04, 0x02)
    HAUNTED_MANSION_EAST = Section(0x04, 0x03)
    PINK_EVIL_PIG_BAG_ROOM = Section(0x04, 0x07)
    CIVILIZATION_ROOM = Section(0x04, 0x0B)
    THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x04, 0x0F)
    CRY_ROOM = Section(0x04, 0x13)

    BACCUS_VILLAGE = Section(0x05, 0x00)
    CENTRAL_PARK = Section(0x05, 0x01)
    BACCUS_VILLAGE_PURIFIED = Section(0x05, 0x02)
    CENTRAL_PARK_PURIFIED = Section(0x05, 0x03)

    FOREST_OF_100_FLOWERS_PURIFIED = Section(0x07, 0x00)
    RIGHT_ENTRANCE_PURIFIED = Section(0x07, 0x01)
    WOBBLY_WARF_PURIFIED = Section(0x07, 0x02)
    WATCH_TOWER_PURIFIED = Section(0x07, 0x03)
    CHARITY_SQUARE_PURIFIED = Section(0x07, 0x04)

    MUSHROOM_FOREST = Section(0x09, 0x00)

    MASAKARI_JUNGLE = Section(0x0A, 0x00)
    MASAKARI_RIVER = Section(0x0A, 0x01)
    OLD_TREE_HILL = Section(0x0A, 0x02)
    TRICK_VILLAGE = Section(0x0A, 0x03)
    MASAKARI_JUNGLE_PURIFIED = Section(0x0A, 0x04)
    MASAKARI_RIVER_PURIFIED = Section(0x0A, 0x05)
    OLD_TREE_HILL_PURIFIED = Section(0x0A, 0x06)
    TRICK_VILLAGE_PURIFIED = Section(0x0A, 0x07)

    TEN_THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x0A, 0x08)

    Y_CROSSING = Section(0x12, 0x01)

    HIDDEN_VILLAGE = Section(0x13, 0x02)


purified_sections: dict[Section, Section] = {
    # Dwarf Forest
    Sections.FOREST_OF_100_FLOWERS_PURIFIED: Sections.FOREST_OF_100_FLOWERS,
    Sections.RIGHT_ENTRANCE_PURIFIED: Sections.RIGHT_ENTRANCE,
    Sections.WOBBLY_WARF_PURIFIED: Sections.WOBBLY_WARF,
    Sections.WATCH_TOWER_PURIFIED: Sections.WATCH_TOWER,
    Sections.CHARITY_SQUARE_PURIFIED: Sections.CHARITY_SQUARE,
    # Phoenix Mountain
    Sections.STORMY_MOUNTAINS_PURIFIED: Sections.STORMY_MOUNTAINS,
    Sections.STORMY_MOUNTAINS_SECOND_PURIFIED: Sections.STORMY_MOUNTAINS_SECOND,
    # Baccus Village
    Sections.BACCUS_VILLAGE_PURIFIED: Sections.BACCUS_VILLAGE,
    Sections.CENTRAL_PARK_PURIFIED: Sections.CENTRAL_PARK,
    # Masakari Jungle
    Sections.MASAKARI_JUNGLE_PURIFIED: Sections.MASAKARI_JUNGLE,
    Sections.MASAKARI_RIVER_PURIFIED: Sections.MASAKARI_RIVER,
    Sections.OLD_TREE_HILL_PURIFIED: Sections.OLD_TREE_HILL,
    Sections.TRICK_VILLAGE_PURIFIED: Sections.TRICK_VILLAGE,
}
