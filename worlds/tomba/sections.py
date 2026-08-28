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
            return self.network_key()
        return f"{self.network_key()} - {self.name}"

    def network_key(self) -> str:
        """Archipelago only allows str keys on the network
        Some dict are indexed by section and this is the key to use
        instead of the object"""
        return f"0x{self.area_id:02x}-0x{self.section_id:02x}"


class Sections:
    VILLAGE_OF_ALL_BEGINNING = Section(0x00, 0x00, Regions.VILLAGE_OF_ALL_BEGINNINGS)
    FOREST_OF_ALL_BEGINNING_PART_1 = Section(0x00, 0x01, Regions.FOREST_OF_ALL_BEGINNINGS)
    FOREST_OF_ALL_BEGINNING_PART_2 = Section(0x00, 0x02, Regions.FOREST_OF_ALL_BEGINNINGS_BIS)
    HUNDREDS_YEAR_OLD_MANS_HUT = Section(0x00, 0x03, Regions.HUNDRED_YEAR_OLD_MANS_HUT)
    GARAGE = Section(0x00, 0x04, Regions.GARAGE)
    OL_POND = Section(0x00, 0x05, Regions.OL_POND)

    FOREST_OF_100_FLOWERS_PART_1 = Section(0x01, 0x00, Regions.FOREST_OF_100_FLOWERS)
    FOREST_OF_100_FLOWERS_PART_2 = Section(0x01, 0x01, Regions.FOREST_OF_100_FLOWERS_BIS)
    WOBBLY_WHARF = Section(0x01, 0x02, Regions.WOBBLY_WHARF)
    WATCH_TOWER = Section(0x01, 0x03, Regions.WATCH_TOWER)
    CHARITY_SQUARE = Section(0x01, 0x04, Regions.CHARITY_SQUARE)

    DWARF_VILLAGE = Section(0x02, 0x00, Regions.DWARF_VILLAGE)
    DWARF_ELDER_HUT = Section(0x02, 0x01, Regions.DWARF_ELDER_HUT)
    UNDERGROUND_PRISON = Section(0x02, 0x02, Regions.UNDERGROUND_PRISON)
    UNDERGROUND_MAZE = Section(0x02, 0x03, Regions.UNDERGROUND_MAZE)
    MILLION_YEAR_OLD_MANS_ROOM = Section(0x02, 0x04, Regions.MILLION_YEAR_OLD_MANS_ROOM)
    THE_STRANGE_SMALL_ROOM = Section(0x02, 0x05, Regions.THE_STRANGE_SMALL_ROOM)

    STORMY_MOUNTAINS_PART_1 = Section(0x03, 0x00, Regions.STORMY_MOUNTAIN)
    STORMY_MOUNTAINS_PART_2 = Section(0x03, 0x01, Regions.STORMY_MOUNTAIN_BIS)
    LAVA_CAVES = Section(0x03, 0x02, Regions.LAVA_CAVES)
    PHOENIXS_NEST = Section(0x03, 0x03, Regions.PHOENIXS_NEST)
    STORMY_MOUNTAINS_PART_1_PURIFIED = Section(0x03, 0x04, "Stormy Mountain (Part 1) Purified")
    STORMY_MOUNTAINS_PART_2_PURIFIED = Section(0x03, 0x05, "Stormy Mountain (Part 2) Purified")

    HAUNTED_MANSION_NORTH = Section(0x04, 0x00, Regions.HAUNTED_MANSION_NORTH)
    HAUNTED_MANSION_WEST = Section(0x04, 0x01, Regions.HAUNTED_MANSION_WEST)
    HAUNTED_MANSION_SOUTH = Section(0x04, 0x02, Regions.HAUNTED_MANSION_SOUTH)
    HAUNTED_MANSION_EAST = Section(0x04, 0x03, Regions.HAUNTED_MANSION_EAST)
    SUNNY_ROOM = Section(0x04, 0x04, Regions.SUNNY_ROOM)
    THIEFS_ROOM_ONE = Section(0x04, 0x05, Regions.THIEFS_ROOM_ONE)
    SWIMMING_ROOM = Section(0x04, 0x06, Regions.SWIMMING_ROOM)
    KEYHOLE_ROOM = Section(0x04, 0x07, Regions.KEYHOLE_ROOM)
    HIDING_ROOM = Section(0x04, 0x08, Regions.HIDING_ROOM)
    TRIBULATION_ROOM = Section(0x04, 0x09, Regions.TRIBULATION_ROOM)
    LAUGHING_ROOM = Section(0x04, 0x0A, Regions.LAUGHING_ROOM)
    CIVILIZATION_ROOM = Section(0x04, 0x0B, Regions.CIVILIZATION_ROOM)
    TRAP_ROOM = Section(0x04, 0x0C, Regions.TRAP_ROOM)
    TRICK_ROOM = Section(0x04, 0x0D, Regions.TRICK_ROOM)
    SUN_TORCH_STAND = Section(0x04, 0x0E, Regions.SUN_TORCH_STAND)
    THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x04, 0x0F, Regions.THOUSAND_YEAR_OLD_MANS_ROOM)
    SHADOW_ROOM = Section(0x04, 0x10, Regions.SHADOW_ROOM)
    THIEFS_ROOM_TWO = Section(0x04, 0x11, Regions.THIEFS_ROOM_TWO)
    THIEFS_ROOM_THREE = Section(0x04, 0x12, Regions.THIEFS_ROOM_THREE)
    CRY_ROOM = Section(0x04, 0x13, Regions.CRY_ROOM)

    BACCUS_VILLAGE = Section(0x05, 0x00, Regions.BACCUS_VILLAGE)
    CENTRAL_PARK = Section(0x05, 0x01, Regions.CENTRAL_PARK)
    BACCUS_VILLAGE_PURIFIED = Section(0x05, 0x02, "Baccus Village Purified")
    CENTRAL_PARK_PURIFIED = Section(0x05, 0x03, "Central Park Purified")

    MOTOCROSS_COURSE = Section(0x06, 0x00, Regions.MOTOCROSS_COURSE)
    THE_MERMAIDS_SINGING_BEACH = Section(0x06, 0x01, Regions.THE_MERMAIDS_SINGING_BEACH)
    THE_MERMAIDS_SINGING_ROCK = Section(0x06, 0x02, Regions.THE_MERMAIDS_SINGING_ROCK)

    FOREST_OF_100_FLOWERS_PART_1_PURIFIED = Section(0x07, 0x00, "Forest of 100 Flowers (Part 1) Purified")
    FOREST_OF_100_FLOWERS_PART_2_PURIFIED = Section(0x07, 0x01, "Forest of 100 Flowers (Part 2) Purified")
    WOBBLY_WHARF_PURIFIED = Section(0x07, 0x02, "Wobbly Wharf Purified")
    WATCH_TOWER_PURIFIED = Section(0x07, 0x03, "Watch Tower Purified")
    CHARITY_SQUARE_PURIFIED = Section(0x07, 0x04, "Charity Square Purified")

    BACCUS_LAKE = Section(0x08, 0x00, Regions.BACCUS_LAKE)
    BACCUS_LAKE_PIER = Section(0x08, 0x01, Regions.BACCUS_PIER)
    BACCUS_LAKE_PURIFIED = Section(0x08, 0x02, "Baccus Lake Purified")
    BACCUS_LAKE_PIER_PURIFIED = Section(0x08, 0x03, "Baccus Pier Purified")

    MUSHROOM_FOREST = Section(0x09, 0x00, Regions.MUSHROOM_FOREST)
    LAKE = Section(0x09, 0x01, Regions.LAKE)
    LAKE_LEFT_BANK = Section(0x09, 0x01, Regions.LAKE_LEFT_BANK)
    MANSION_JUNGLE_PIG_ROOM = Section(0x09, 0x02, Regions.MANSION_JUNGLE_PIG_ROOM)
    MANSION = Section(0x09, 0x03, Regions.MANSION)
    MANSION_STAIRS_UP = Section(0x09, 0x04, Regions.MANSION_STAIRS_UP)
    MANSION_STAIRS_DOWN = Section(0x09, 0x05, Regions.MANSION_STAIRS_DOWN)
    LEAF_SLIDER = Section(0x09, 0x06, Regions.LEAF_SLIDER)

    MASAKARI_JUNGLE = Section(0x0A, 0x00, Regions.MASAKARI_JUNGLE)
    MASAKARI_RIVER = Section(0x0A, 0x01, Regions.MASAKARI_RIVER)
    OLD_TREE_HILL = Section(0x0A, 0x02, Regions.OLD_TREE_HILL)
    TRICK_VILLAGE = Section(0x0A, 0x03, Regions.TRICK_VILLAGE)
    MASAKARI_JUNGLE_PURIFIED = Section(0x0A, 0x04, "Maskari Jungle Purified")
    MASAKARI_RIVER_PURIFIED = Section(0x0A, 0x05, "Masakari River Purified")
    OLD_TREE_HILL_PURIFIED = Section(0x0A, 0x06, "Old Tree Hill Purified")
    TRICK_VILLAGE_PURIFIED = Section(0x0A, 0x07, "Trick Village Purified")
    TEN_THOUSAND_YEAR_OLD_MANS_ROOM = Section(0x0A, 0x08, Regions.TEN_THOUSAND_YEAR_OLD_MANS_ROOM)

    LUMBERJACK_TOWN = Section(0x0B, 0x00, "Lumberjack Town")
    LUMBERJACK_FACTORY = Section(0x0B, 0x01, Regions.LUMBERJACK_FACTORY)
    DRIED_WISHING_WELL = Section(0x0B, 0x02, Regions.DRIED_WISHING_WELL)

    FLOWER_TOWER = Section(0x0D, 0x00, Regions.FLOWER_TOWER)
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

    SOFTLOCK_1 = Section(0x0F, 0x00, "Softlock 1")
    SOFTLOCK_2 = Section(0x0F, 0x01, "Softlock 2")
    BLACKSCREEN_1 = Section(0x0F, 0x02, "Blackscreen 1")
    BLACKSCREEN_2 = Section(0x0F, 0x03, "Blackscreen 2")

    STONES_TOWN = Section(0x10, 0x00, "Stones Town")
    CLOCK_TOWER_ENTRANCE_PURIFIED = Section(0x10, 0x01, "Clock Tower Entrance Purified")
    CLOCK_TOWER_HALFWAY_UP_PURIFIED = Section(0x10, 0x02, "Clock Tower Halfway Up Purified")
    CLOCK_TOWER_ENGINE_ROOM_PURIFIED = Section(0x10, 0x03, "Clock Tower Engines Room Purified")
    CLOCK_TOWER_ENTRANCE = Section(0x10, 0x04, Regions.CLOCK_TOWER_ENTRANCE)
    CLOCK_TOWER_HALFWAY_UP = Section(0x10, 0x05, Regions.CLOCK_TOWER_HALFWAY_UP)
    CLOCK_TOWER_ENGINE_ROOM = Section(0x10, 0x06, Regions.CLOCK_TOWER_ENGINE_ROOM)

    IRON_TOWN = Section(0x11, 0x00, "Iron Town")
    IRON_CASTLE_ENTRANCE = Section(0x11, 0x01, Regions.IRON_CASTLE_ENTRANCE)
    IRON_CASTLE_MAIN_ROOM = Section(0x11, 0x02, Regions.IRON_CASTLE_MAIN_ROOM)
    IRON_CASTLE_LEFT_ROOM = Section(0x11, 0x03, Regions.IRON_CASTLE_LEFT_ROOM)
    IRON_CASTLE_RIGHT_ROOM = Section(0x11, 0x04, Regions.IRON_CASTLE_RIGHT_ROOM)
    IRON_CASTLE_ENGINE_ROOM = Section(0x11, 0x05, Regions.IRON_CASTLE_ENGINE_ROOM)
    IRON_CASTLE_ENTRANCE_PURIFIED = Section(0x11, 0x06, "Iron Castle Entrance Purified")
    IRON_CASTLE_MAIN_ROOM_PURIFIED = Section(0x11, 0x07, "Iron Castle Main Room Purified")
    IRON_CASTLE_LEFT_ROOM_PURIFIED = Section(0x11, 0x08, "Iron Castle Left Room Purified")
    IRON_CASTLE_RIGHT_ROOM_PURIFIED = Section(0x11, 0x09, "Iron Castle Right Room Purified")
    IRON_CASTLE_ENGINE_ROOM_PURIFIED = Section(0x11, 0x0A, "Iron Castle Engine Room Purified")

    IRON_CASTLE_SOFTLOCK_5 = Section(0x11, 0x0B, "Iron Castle Softlock 5")

    VILLAGE_OF_CIVILIZATION = Section(0x12, 0x00, "Village of Civilization")
    Y_CROSSING = Section(0x12, 0x01, Regions.Y_CROSSING)
    WITCH_HUT = Section(0x12, 0x02, Regions.WITCHS_HUT)

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
    Sections.FOREST_OF_100_FLOWERS_PART_1_PURIFIED: Sections.FOREST_OF_100_FLOWERS_PART_1,
    Sections.FOREST_OF_100_FLOWERS_PART_2_PURIFIED: Sections.FOREST_OF_100_FLOWERS_PART_2,
    Sections.WOBBLY_WHARF_PURIFIED: Sections.WOBBLY_WHARF,
    Sections.WATCH_TOWER_PURIFIED: Sections.WATCH_TOWER,
    Sections.CHARITY_SQUARE_PURIFIED: Sections.CHARITY_SQUARE,
    # Phoenix Mountain
    Sections.STORMY_MOUNTAINS_PART_1_PURIFIED: Sections.STORMY_MOUNTAINS_PART_1,
    Sections.STORMY_MOUNTAINS_PART_2_PURIFIED: Sections.STORMY_MOUNTAINS_PART_2,
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
