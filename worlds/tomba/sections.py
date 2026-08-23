from dataclasses import dataclass
from .constants import Regions


@dataclass
class Section:
    area_id: int
    section_id: int
    name: str = ""

    def is_purified(self) -> bool:
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
        if self.name == "":
            return f"0x{self.area_id:02x}-0x{self.section_id:02x}"
        return self.name


class Sections:
    VILLAGE_OF_ALL_BEGINNING = Section(0x00, 0x00, Regions.VILLAGE_OF_ALL_BEGINNINGS)
    FOREST_OF_ALL_BEGINNING_PART_1 = Section(0x00, 0x01, Regions.FOREST_OF_ALL_BEGINNINGS)
    FOREST_OF_ALL_BEGINNING_PART_2 = Section(0x00, 0x02, "Forest of All Beginnings part 2")
    HUNDREDS_YEAR_OLD_MANS_HUT = Section(0x00, 0x03, "100 Year Old Man's Hut")
    GARAGE = Section(0x00, 0x04, "Motocross Garage")
    OL_POND = Section(0x00, 0x05, Regions.OL_POND)

    FOREST_OF_100_FLOWERS = Section(0x01, 0x00, Regions.FOREST_OF_100_FLOWERS)
    RIGHT_ENTRANCE = Section(0x01, 0x01, "Forest of 100 Flowers Right Entrance")
    WOBBLY_WHARF = Section(0x01, 0x02, Regions.WOBBLY_WHARF)
    WATCH_TOWER = Section(0x01, 0x03, Regions.WATCH_TOWER)
    CHARITY_SQUARE = Section(0x01, 0x04, Regions.CHARITY_SQUARE)

    DWARF_VILLAGE = Section(0x02, 0x00, Regions.DWARF_VILLAGE)
    DWARF_VILLAGE = Section(0x02, 0x01, Regions.DWARF_ELDER_HUT)
    DWARF_VILLAGE = Section(0x02, 0x02, Regions.UNDERGROUND_PRISON)
    UNDERGROUND_MAZE = Section(0x02, 0x03, Regions.UNDERGROUND_MAZE)
    MILLION_YEAR_OLD_MANS_ROOM = Section(0x02, 0x04, Regions.MILLION_YEAR_OLD_MANS_ROOM)
    THE_STRANGE_SMALL_ROOM = Section(0x02, 0x05, Regions.THE_STRANGE_SMALL_ROOM)

    STORMY_MOUNTAINS = Section(0x03, 0x00, Regions.STORMY_MOUNTAIN)
    STORMY_MOUNTAINS_SECOND = Section(0x03, 0x01, "Stormy Mountain Second")
    LAVA_CAVES = Section(0x03, 0x02, Regions.LAVA_CAVES)
    PHOENIXS_NEST = Section(0x03, 0x03, Regions.PHOENIXS_NEST)
    STORMY_MOUNTAINS_PURIFIED = Section(0x03, 0x04)
    STORMY_MOUNTAINS_SECOND_PURIFIED = Section(0x03, 0x05)

    HAUNTED_MANSION_NORTH = Section(0x04, 0x00, "North Side Of Mansion")
    HAUNTED_MANSION_WEST = Section(0x04, 0x01, "West Side Of Mansion")
    HAUNTED_MANSION_SOUTH = Section(0x04, 0x02, "South Side Of Mansion")
    HAUNTED_MANSION_EAST = Section(0x04, 0x03, "East Side Of Mansion")
    SUNNY_ROOM = Section(0x04, 0x04, "Sunny Room")
    THIEFS_ROOM_ONE = Section(0x04, 0x05, "Thief's Room One")
    SWIMMING_ROOM = Section(0x04, 0x06, "Swimming Room")
    KEYHOLE_ROOM = Section(0x04, 0x07, "Keyhole Room")
    HIDING_ROOM = Section(0x04, 0x08, "Hidding Room")
    TRIBULATION_ROOM = Section(0x04, 0x09, "Room Of Tribulation")
    LAUGHING_ROOM = Section(0x04, 0x0A, "Laughing Room")
    CIVILIZATION_ROOM = Section(0x04, 0x0B)
    TRAP_ROOM = Section(0x04, 0x0C, "Trap Room")
    TRICK_ROOM = Section(0x04, 0x0D, "Trick Room")
    CIVILIZATION_ROOM = Section(0x04, 0x0E, "Sun Torch Stand")
    THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x04, 0x0F, "1,000 Year Old Man's Room")
    SHADOW_ROOM = Section(0x04, 0x10, "Shadow Room")
    THIEFS_ROOM_TWO = Section(0x04, 0x11, "Thief's Room Two")
    THIEFS_ROOM_THREE = Section(0x04, 0x12, "Thief's Room Three")
    CRY_ROOM = Section(0x04, 0x13, "Crying Room")

    BACCUS_VILLAGE = Section(0x05, 0x00)
    CENTRAL_PARK = Section(0x05, 0x01)
    BACCUS_VILLAGE_PURIFIED = Section(0x05, 0x02)
    CENTRAL_PARK_PURIFIED = Section(0x05, 0x03)

    MOTOCROSS = Section(0x06, 0x00, "Motocross Course")
    MOTOCROSS = Section(0x06, 0x01, "The Mermaid Singing Rock Beach")
    MOTOCROSS = Section(0x06, 0x02, "The Mermaid Singing Rock Mermaid")

    FOREST_OF_100_FLOWERS_PURIFIED = Section(0x07, 0x00)
    RIGHT_ENTRANCE_PURIFIED = Section(0x07, 0x01)
    WOBBLY_WHARF_PURIFIED = Section(0x07, 0x02)
    WATCH_TOWER_PURIFIED = Section(0x07, 0x03)
    CHARITY_SQUARE_PURIFIED = Section(0x07, 0x04)

    BACCUS_LAKE = Section(0x08, 0x00, Regions.BACCUS_LAKE)
    BACCUS_LAKE_PIER = Section(0x08, 0x01, "Baccus Pier")
    BACCUS_LAKE_PURIFIED = Section(0x08, 0x02, "Baccus Lake Purified")
    BACCUS_LAKE_PIER_PURIFIED = Section(0x08, 0x03, "Baccus Pier Purified")

    MUSHROOM_FOREST = Section(0x09, 0x00, Regions.MUSHROOM_FOREST)
    LAKE = Section(0x09, 0x01, "Lake")
    MANSION_JUNGLE_PIG_ROOM = Section(0x09, 0x02, "Mansion Grandfather Clock Room")
    MANSION = Section(0x09, 0x03, Regions.MANSION)
    MANSION_STAIRS_DOWN = Section(0x09, 0x04, "Mansion Descending Stairs")
    MANSION_STAIRTS_UP = Section(0x09, 0x05, "Mansion Ascending Stairs")
    LEAF_SLIDER = Section(0x09, 0x06, "Leaf Slider")

    MASAKARI_JUNGLE = Section(0x0A, 0x00, Regions.MASAKARI_JUNGLE)
    MASAKARI_RIVER = Section(0x0A, 0x01, "Masakari River")
    OLD_TREE_HILL = Section(0x0A, 0x02, Regions.OLD_TREE_HILL)
    TRICK_VILLAGE = Section(0x0A, 0x03, Regions.TRICK_VILLAGE)
    MASAKARI_JUNGLE_PURIFIED = Section(0x0A, 0x04)
    MASAKARI_RIVER_PURIFIED = Section(0x0A, 0x05)
    OLD_TREE_HILL_PURIFIED = Section(0x0A, 0x06)
    TRICK_VILLAGE_PURIFIED = Section(0x0A, 0x07)
    TEN_THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x0A, 0x08, "10000 Year Old Man's Room")

    LUMBERJACK_TOWN = Section(0x0B, 0x00, "Lumberjack Town")
    LUMBERJACK_FACTORY = Section(0x0B, 0x01, "Lumberjack Factory")
    DRIED_WISHING_WELL = Section(0x0B, 0x02, "Dried Wishing Well")

    FLOWER_TOWER = Section(0x0D, 0x00, "Flower Tower")
    PIG_ISLAND_CAVE = Section(0x0D, 0x01, "Pig Island Cave")
    PIG_ISLAND_CAVE_END = Section(0x0D, 0x02, "Pig Island Cave End")

    BOSS_STORM_PIG = Section(0x0E, 0x00, "Storm Pig")
    BOSS_MOUSE_PIG = Section(0x0E, 0x01, "Mouse Pig")
    BOSS_TRICK_PIG = Section(0x0E, 0x02, "Trick Pig")
    BOSS_LAVA_PIG = Section(0x0E, 0x03, "Lava Pig")
    BOSS_FOREST_PIG = Section(0x0E, 0x04, "Forest Pig")
    BOSS_JUNGLE_PIG = Section(0x0E, 0x05, "Jungle Pig")
    BOSS_HAUNTED_PIG = Section(0x0E, 0x06, "Haunted Pig")
    BOSS_REAL_PIG = Section(0x0E, 0x07, "Real Pig")

    SOFTLOCK_1 = (Section(0x0F, 0x00, "Softlock 1"),)
    SOFTLOCK_2 = (Section(0x0F, 0x01, "Softlock 2"),)
    BLACKSCREEN_1 = (Section(0x0F, 0x02, "Blackscreen 1"),)
    BLACKSCREEN_2 = (Section(0x0F, 0x03, "Blackscreen 2"),)

    STONES_TOWN = Section(0x10, 0x00, "Stones Town")
    CLOCK_TOWER_SOFTLOCK = Section(0x10, 0x01, "Clock Tower Softlock")
    CLOCK_TOWER_CRASH = Section(0x10, 0x02, "Clock Tower Crash")
    CLOCK_TOWER_ENGINE_ROOM = Section(0x10, 0x03, "Clock Tower Engines Room")
    CLOCK_TOWER_ENTRANCE = Section(0x10, 0x04, "Clock Tower Entrance")
    CLOCK_TOWER_HALFWAY_UP = Section(0x10, 0x05, "Clock Tower Halfway Up")
    CLOCK_TOWER_ENGINE_ROOM_NO_EXIT = Section(0x10, 0x06, "Clock Tower Engines Room No Exit")

    IRON_TOWN = Section(0x11, 0x00, "Iron Town")
    IRON_CASTLE_ENTRANCE = Section(0x11, 0x01, "Iron Castle Entrance")
    IRON_CASTLE_MAIN_ROOM = Section(0x11, 0x02, "Iron Castle Main Room")
    IRON_CASTLE_LEFT_ROOM = Section(0x11, 0x03, "Iron Castle Left Room")
    IRON_CASTLE_RIGHT_ROOM = Section(0x11, 0x04, "Iron Castle Right Room")
    IRON_CASTLE_ENGINE_ROOM = Section(0x11, 0x05, "Iron Castle Engine Room")
    IRON_CASTLE_SOFTLOCK_1 = Section(0x11, 0x06, "Iron Castle Softlock 1")
    IRON_CASTLE_SOFTLOCK_2 = Section(0x11, 0x07, "Iron Castle Softlock 2")
    IRON_CASTLE_SOFTLOCK_3 = Section(0x11, 0x08, "Iron Castle Softlock 3")
    IRON_CASTLE_CRASH = Section(0x11, 0x09, "Iron Castle Crash")
    IRON_CASTLE_SOFTLOCK_4 = Section(0x11, 0x0A, "Iron Castle Softlock 4")
    IRON_CASTLE_SOFTLOCK_5 = Section(0x11, 0x0B, "Iron Castle Softlock 5")

    VILLAGE_OF_CIVILIZATION = Section(0x12, 0x00, "Village of Civilization")
    Y_CROSSING = Section(0x12, 0x01, Regions.Y_CROSSING)
    WITCH_HUT = Section(0x12, 0x02, "With's Hut")

    A13_S00 = Section(0x13, 0x00, Regions.DWARF_VILLAGE)
    A13_S01 = Section(0x13, 0x01, Regions.DWARF_ELDER_HUT)
    HIDDEN_VILLAGE = Section(0x13, 0x02, Regions.HIDDEN_VILLAGE)

    @classmethod
    def all_sections(cls) -> list[Section]:
        """Dynamically loops through and retrieves all defined Sections"""
        return [value for _, value in cls.__dict__.items() if isinstance(value, Section)]

    @classmethod
    def get(cls, section: Section) -> Section:
        for _, value in cls.__dict__.items():
            if not isinstance(value, Section):
                continue

            if value.equals(section):
                return value

        return section


purified_sections: dict[Section, Section] = {
    # Dwarf Forest
    Sections.FOREST_OF_100_FLOWERS_PURIFIED: Sections.FOREST_OF_100_FLOWERS,
    Sections.RIGHT_ENTRANCE_PURIFIED: Sections.RIGHT_ENTRANCE,
    Sections.WOBBLY_WHARF_PURIFIED: Sections.WOBBLY_WHARF,
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
    # TODO: Haunted Mansion
}
