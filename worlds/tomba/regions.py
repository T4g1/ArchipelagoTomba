from __future__ import annotations

from typing import TYPE_CHECKING, Any
from rule_builder.rules import Has, Rule
from dataclasses import dataclass

from BaseClasses import Region, CollectionRule, Entrance
from entrance_rando import EntranceType

from .constants import Regions, Items, Events
from .helpers import Started, Cleared, Rules
from .sections import Section, Sections

if TYPE_CHECKING:
    from .world import TombaWorld


@dataclass
class Entry:
    name: str
    spawn_id: int


@dataclass
class Exit:
    name: str
    spawn_id: int
    target: Section | None = None
    rule: CollectionRule | Rule[Any] | None = None


@dataclass
class Transitions:
    entries: list[Entry]
    exits: list[Exit]


region_names = [value for key, value in Regions.__dict__.items() if not key.startswith("_") and isinstance(value, str)]


def create_and_connect_regions(world: TombaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: TombaWorld) -> None:
    regions = []

    for region_name in region_names:
        regions.append(Region(region_name, world.player, world.multiworld))

    world.multiworld.regions += regions


def connect(
    world: TombaWorld,
    source_name: str,
    target_name: str,
    rule: CollectionRule | Rule[Any] | None = None,
    suffix: str = "",
    entrance_type: EntranceType = EntranceType.ONE_WAY,
) -> Entrance:
    source = world.get_region(source_name)
    target = world.get_region(target_name)
    entrance = source.connect(target, f"{source} to {target}{suffix}", rule)
    entrance.randomization_type = entrance_type
    return entrance


def get_entrance_name(section: Section, suffix: str) -> str:
    return f"{section.name} {suffix}"


def get_randomizable_transitions(player: int) -> dict[Section, Transitions]:
    return {
        Sections.VILLAGE_OF_ALL_BEGINNING: Transitions(
            [
                # Entry("Starting Pillar", 0x00),
                Entry("Garage Door", 0x01),
                # Entry("Mansion Door", 0x02),
                Entry("Witch Door", 0x03),
            ],
            [
                Exit("Garage Entrance", 0x01, Sections.GARAGE, Rules.CAN_BREAK_STUFF),
                Exit(
                    "Mizuno's Entrance",
                    0x02,
                    Sections.WITCH_HUT,
                    lambda state: state.can_reach_location(Started(Events.THE_CUTE_WITCH), player),
                ),
            ],
        ),
        Sections.FOREST_OF_ALL_BEGINNING_PART_1: Transitions(
            [
                Entry("Ol' Pond Door", 0x01),
                Entry("Underground Maze Door", 0x02),
            ],
            [
                Exit("Ol' Pond Entrance", 0x00, Sections.OL_POND),
                # Openned from the other side: connection will be a two-way on the incoming side
                Exit("Underground Maze Entrance", 0x01),
            ],
        ),
        Sections.FOREST_OF_ALL_BEGINNING_PART_2: Transitions(
            [
                Entry("100 Year Old Man Door", 0x02),
            ],
            [Exit("100 Year Old Man Entrance", 0x01, Sections.HUNDREDS_YEAR_OLD_MANS_HUT)],
        ),
        Sections.HUNDREDS_YEAR_OLD_MANS_HUT: Transitions(
            [
                Entry("Forest of All Beginning Door", 0x00),
                Entry("Forest of 100 Flower Rope", 0x01),
            ],
            [
                Exit("Forest of All Beginning Entrance", 0x00, Sections.FOREST_OF_ALL_BEGINNING_PART_2),
                Exit(
                    "Forest of 100 Flower Entrance",
                    0x01,
                    Sections.FOREST_OF_100_FLOWERS_PART_1,
                    lambda state: state.can_reach_location(Cleared(Events.INSIDE_THE_KOKKA_EGGS), player),
                ),
            ],
        ),
        Sections.GARAGE: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.VILLAGE_OF_ALL_BEGINNING),
            ],
        ),
        Sections.OL_POND: Transitions(
            [
                Entry("Entrance", 0x02),
                Entry("Trick Village Entrance", 0x01),
            ],
            [
                Exit("Hut Door", 0x00, Sections.FOREST_OF_ALL_BEGINNING_PART_1),
                Exit(
                    "Trick Village Door",
                    0x01,
                    Sections.TRICK_VILLAGE,
                    lambda state: (
                        state.can_reach_location(Cleared(Events.I_CANT_SWIM), player)
                        and state.has(Items.KEY_TO_OL_POND, player)
                    )
                    or state.has(Items.SACRED_FISH, player),
                ),
            ],
        ),
        Sections.FOREST_OF_100_FLOWERS_PART_1: Transitions(
            [
                # Entry("Spawn", 0x00),
                Entry("Chimney Entrance", 0x01),
                Entry("Big House Entrance", 0x02),
            ],
            [
                Exit("Chimney", 0x00, Sections.HUNDREDS_YEAR_OLD_MANS_HUT),
                Exit(
                    "Big House",
                    0x01,
                    Sections.WOBBLY_WHARF,
                    lambda state: state.can_reach_location(Started(Events.SAVE_THE_DWARVES), player),
                ),
            ],
        ),
        Sections.FOREST_OF_100_FLOWERS_PART_2: Transitions(
            [
                Entry("Stone Slab Entrance", 0x01),
                Entry("Big Red Arrow Entrance", 0x02),
            ],
            [
                Exit(
                    "Stone Slab",
                    0x01,
                    Sections.WATCH_TOWER,
                    lambda state: state.can_reach_location(Started(Events.SAVE_THE_DWARVES), player),
                ),
                Exit("Big Red Arrow", 0x02, Sections.DWARF_VILLAGE),
            ],
        ),
        Sections.WOBBLY_WHARF: Transitions(
            [
                Entry("Big House Entrance", 0x02),
                Entry("Stairs Entrance", 0x01),
            ],
            [
                Exit("Big House", 0x00, Sections.FOREST_OF_100_FLOWERS_PART_1),
                Exit(
                    "Stairs",
                    0x01,
                    Sections.CHARITY_SQUARE,
                    lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), player),
                ),
            ],
        ),
        Sections.WATCH_TOWER: Transitions(
            [
                Entry("Middle Entrance", 0x01),
                Entry("Rightmost Entrance", 0x02),
                Entry("Leftmost Entrance", 0x03),
                Entry("Elevator Entrance", 0x04),
            ],
            [
                Exit("Leftmost", 0x00, Sections.FOREST_OF_100_FLOWERS_PART_2),
                Exit(
                    "Middle",
                    0x01,
                    Sections.CHARITY_SQUARE,
                    lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), player),
                ),
                Exit(
                    "Rightmost",
                    0x02,
                    Sections.MUSHROOM_FOREST,
                    lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), player),
                ),
                Exit(
                    "Elevator",
                    0x03,
                    Sections.UNDERGROUND_MAZE,
                    lambda state: state.can_reach_location(Cleared(Events.WE_NEED_POWER), player),
                ),
            ],
        ),
        Sections.CHARITY_SQUARE: Transitions(
            [
                Entry("Stair Entrance", 0x01),
                Entry("Leaf Slider Entrance", 0x02),
                Entry("Rightmost Entrance", 0x03),
                Entry("Flower Tower Entrance", 0x04),
            ],
            [
                Exit("Rightmost", 0x00, Sections.WATCH_TOWER),
                Exit("Stair", 0x01, Sections.WOBBLY_WHARF),
                Exit("Leaf Slide", 0x02, Sections.LEAF_SLIDER),
                Exit("Flower Tower", 0x03, Sections.FLOWER_TOWER),
            ],
        ),
        Sections.DWARF_VILLAGE: Transitions(
            [
                Entry("Right Entrance", 0x01),
                Entry("Left Entrance", 0x02),
            ],
            [
                Exit("Left", 0x00, Sections.FOREST_OF_100_FLOWERS_PART_2),
                Exit("Right", 0x01, Sections.DWARF_ELDER_HUT),
            ],
        ),
        Sections.DWARF_ELDER_HUT: Transitions(
            [
                Entry("Left Entrance", 0x00),
                Entry("Hole Entrance", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.FOREST_OF_100_FLOWERS_PART_2),
                Exit(
                    "Hole",
                    0x01,
                    Sections.UNDERGROUND_PRISON,
                    lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), player),
                ),
            ],
        ),
        Sections.UNDERGROUND_PRISON: Transitions(
            [
                Entry("Left", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.DWARF_ELDER_HUT),
            ],
        ),
        Sections.UNDERGROUND_MAZE: Transitions(
            [
                Entry("Bottom Right Entrance", 0x01),
                Entry("Upper Right Entrance", 0x02),
                Entry("Million Year Old Man Entrance", 0x03),
                Entry("Upper Left Entrance", 0x04),
                Entry("Bottom Left Entrance", 0x05),
            ],
            [
                Exit(
                    "Million Year Old Man",
                    0x00,
                    Sections.MILLION_YEAR_OLD_MANS_ROOM,
                    lambda state: state.has(Items.MILLION_YEAR_OLD_BELL, player)
                    or state.can_reach_location(Cleared(Events.UNBREAKABLE_WIRE), player),
                ),
                Exit(
                    "Upper Left",
                    0x01,
                    Sections.THE_STRANGE_SMALL_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.THE_THIEFS_DOOR), player),
                ),
                Exit(
                    "Bottom Left",
                    0x02,
                    Sections.FOREST_OF_ALL_BEGINNING_PART_1,
                    lambda state: state.can_reach_location(Cleared(Events.THE_THIEFS_DOOR), player),
                ),
                Exit("Bottom Right", 0x03, Sections.WATCH_TOWER),
                Exit("Upper Right", 0x04, Sections.CIVILIZATION_ROOM),
            ],
        ),
        Sections.MILLION_YEAR_OLD_MANS_ROOM: Transitions(
            [
                Entry("Left", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.UNDERGROUND_MAZE),
            ],
        ),
        Sections.THE_STRANGE_SMALL_ROOM: Transitions(
            [
                Entry("Right", 0x02),
            ],
            [
                Exit("Right", 0x00, Sections.UNDERGROUND_MAZE),
            ],
        ),
        Sections.STORMY_MOUNTAINS_PART_1: Transitions(
            [
                Entry("Left Entrance", 0x01),
                # Entry("Middle Entrance", 0x02),
                Entry("Right Entrance", 0x03),
                Entry("Pipe Entrance", 0x04),
            ],
            [
                Exit("Left", 0x00, Sections.BACCUS_VILLAGE),
                Exit("Middle", 0x01, Sections.MUSHROOM_FOREST),
                Exit("Right", 0x02, Sections.STORMY_MOUNTAINS_PART_2),
            ],
        ),
        Sections.STORMY_MOUNTAINS_PART_2: Transitions(
            [
                Entry("Left Entrance", 0x00),
                Entry("Lava Caves Entrance", 0x0),
                Entry("Bottom Right Entrance", 0x0),
            ],
            [
                Exit("Left", 0x00, Sections.STORMY_MOUNTAINS_PART_1),
                Exit("Lava Caves", 0x01, Sections.LAVA_CAVES),
                Exit("Bottom Right", 0x02, Sections.STORMY_MOUNTAINS_PART_1),
                # Exit("Phoenix", 0x03, Sections.BACCUS_VILLAGE),
            ],
        ),
        Sections.LAVA_CAVES: Transitions(
            [
                Entry("Left Entrance", 0x01),
                Entry("Right Entrance", 0x02),
                Entry("Top Entrance", 0x03),
            ],
            [
                Exit("Left", 0x00, Sections.STORMY_MOUNTAINS_PART_2),
                Exit(
                    "Right",
                    0x01,
                    Sections.PHOENIXS_NEST,
                    lambda state: state.can_reach_location(Cleared(Events.LAVA_CAVES), player),
                ),
                Exit(
                    "Top",
                    0x02,
                    Sections.HIDDEN_VILLAGE,
                    lambda state: state.can_reach_location(Cleared(Events.LAVA_CAVES), player),
                    # and (state.has(Items.GRAPPLE, player) or state.has(Items.GRAPPLEJACK, player)),
                ),
            ],
        ),
        Sections.PHOENIXS_NEST: Transitions(
            [
                Entry("Left", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.LAVA_CAVES),
            ],
        ),
        Sections.HAUNTED_MANSION_NORTH: Transitions(
            [
                Entry("Shadow Room Entrance", 0x01),
                Entry("Civilization Room Entrance", 0x02),
                Entry("Trick Room Entrance", 0x03),
                Entry("Thief Room Three Entrance", 0x04),
                Entry("Keyhole Room Entrance", 0x05),
                Entry("Laughing Room Entrance", 0x06),
                Entry("Thief Room One Entrance", 0x07),
                # Entry("Sun Torch Stand Entrance", 0x0A),
            ],
            [
                Exit("Shadow Room", 0x01, Sections.SHADOW_ROOM),
                Exit("Civilization Room", 0x02, Sections.CIVILIZATION_ROOM),
                Exit("Trick Room", 0x03, Sections.TRICK_ROOM),
                Exit("Thief Room Three", 0x04, Sections.THIEFS_ROOM_THREE),
                Exit("Keyhole Room", 0x05, Sections.KEYHOLE_ROOM),
                Exit("Laughing Room", 0x06, Sections.LAUGHING_ROOM),
                Exit("Thief Room One", 0x07, Sections.THIEFS_ROOM_ONE),
                # Exit("Sun Torch Stand", 0x0B, Sections.SUN_TORCH_STAND),
            ],
        ),
        Sections.HAUNTED_MANSION_WEST: Transitions(
            [
                Entry("Pier Entrance", 0x00),
                Entry("Crying Room Entrance", 0x01),
                Entry("Stairs Entrance", 0x05),
            ],
            [
                Exit("Pier", 0x00, Sections.BACCUS_LAKE),
                Exit(
                    "Crying Room",
                    0x01,
                    Sections.CRY_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit(
                    "Stairs",
                    0x05,
                    Sections.MUSHROOM_FOREST,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
            ],
        ),
        Sections.HAUNTED_MANSION_SOUTH: Transitions(
            [
                Entry("Swimming Room Entrance", 0x01),
                Entry("Thief's Room Two Entrance", 0x02),
                Entry("Tribulation Room Entrance", 0x03),
                Entry("1,000 Year Old Man Room Entrance", 0x04),
                Entry("Trick Room Entrance", 0x05),
                Entry("Hidding Room Entrance", 0x06),
                Entry("Baccus Village Entrance", 0x07),
                # Entry("Sun Torch Stand Entrance", 0x0A),
            ],
            [
                Exit("Baccus Village", 0x00, Sections.BACCUS_VILLAGE),
                Exit(
                    "Swimming Room",
                    0x01,
                    Sections.SWIMMING_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit(
                    "Thief's Room Two",
                    0x02,
                    Sections.THIEFS_ROOM_TWO,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit(
                    "Tribulation Room",
                    0x03,
                    Sections.TRIBULATION_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit(
                    "1,000 Year Old Man Room",
                    0x04,
                    Sections.THOUSAND_YEAR_OLD_MANS_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit(
                    "Trick Room",
                    0x05,
                    Sections.TRICK_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit(
                    "Hidding Room",
                    0x06,
                    Sections.HIDING_ROOM,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                # Exit("Sun Torch Stand", 0x0A,
                # Sections.SUN_TORCH_STAND,
                # lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player)),
            ],
        ),
        Sections.HAUNTED_MANSION_EAST: Transitions(
            [
                Entry("Sunny Room Entrance", 0x01),
                Entry("Trap Room Entrance", 0x02),
            ],
            [
                Exit("Sunny Room", 0x01, Sections.SUNNY_ROOM),
                Exit("Trap Room", 0x02, Sections.TRAP_ROOM),
            ],
        ),
        Sections.SUNNY_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_EAST),
            ],
        ),
        Sections.THIEFS_ROOM_ONE: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_NORTH),
            ],
        ),
        Sections.SWIMMING_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_SOUTH),
            ],
        ),
        Sections.KEYHOLE_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_NORTH),
            ],
        ),
        Sections.HIDING_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_SOUTH),
            ],
        ),
        Sections.TRIBULATION_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_SOUTH),
            ],
        ),
        Sections.LAUGHING_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_NORTH),
            ],
        ),
        Sections.CIVILIZATION_ROOM: Transitions(
            [
                Entry("Top Entrance", 0x00),
                Entry("Bottom Entrance", 0x01),
            ],
            [
                Exit("Top", 0x00, Sections.HAUNTED_MANSION_NORTH),
                Exit("Bottom", 0x01, Sections.UNDERGROUND_MAZE),
            ],
        ),
        Sections.TRAP_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_EAST),
            ],
        ),
        Sections.TRICK_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
                Entry("Right Entrance", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_SOUTH),
                Exit("Right", 0x01, Sections.HAUNTED_MANSION_NORTH),
            ],
        ),
        # Sections.SUN_TORCH_STAND: Transitions([
        #         Entry("Rope Entrance", 0x01),
        #     ], [
        #         Exit("Rope", 0x00, Sections.HAUNTED_MANSION_SOUTH),
        #         Exit("Rope", 0x01, Sections.HAUNTED_MANSION_NORTH),
        #     ]
        # ),
        Sections.THOUSAND_YEAR_OLD_MANS_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_SOUTH),
            ],
        ),
        Sections.SHADOW_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_NORTH),
            ],
        ),
        Sections.THIEFS_ROOM_TWO: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_SOUTH),
            ],
        ),
        Sections.THIEFS_ROOM_THREE: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_NORTH),
            ],
        ),
        Sections.CRY_ROOM: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.HAUNTED_MANSION_WEST),
            ],
        ),
        Sections.BACCUS_VILLAGE: Transitions(
            [
                Entry("South Entrance", 0x01),
                Entry("Left Entrance", 0x02),
                Entry("Parc Entrance", 0x03),
            ],
            [
                Exit("South", 0x00, Sections.STORMY_MOUNTAINS_PART_1),
                Exit(
                    "Left",
                    0x01,
                    Sections.HAUNTED_MANSION_SOUTH,
                    lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), player),
                ),
                Exit("Parc", 0x02, Sections.CENTRAL_PARK),
            ],
        ),
        Sections.CENTRAL_PARK: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.BACCUS_VILLAGE),
            ],
        ),
        Sections.MOTOCROSS_COURSE: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Right", 0x00, Sections.THE_MERMAIDS_SINGING_BEACH),
            ],
        ),
        Sections.THE_MERMAIDS_SINGING_BEACH: Transitions(
            [
                Entry("Left Entrance", 0x00),
                Entry("Top Right Entrance", 0x01),
            ],
            [
                Exit("Top Right", 0x00, Sections.THE_MERMAIDS_SINGING_ROCK),
                Exit(
                    "Right",
                    0x01,
                    Sections.MASAKARI_RIVER,
                    lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), player),
                ),
            ],
        ),
        Sections.THE_MERMAIDS_SINGING_ROCK: Transitions(
            [
                Entry("Left Entrance", 0x00),
            ],
            [
                Exit("Left", 0x00, Sections.THE_MERMAIDS_SINGING_BEACH),
            ],
        ),
        Sections.BACCUS_LAKE: Transitions(
            [
                Entry("South Entrance", 0x00),
                Entry("North Entrance", 0x01),
            ],
            [
                Exit("South", 0x00, Sections.HAUNTED_MANSION_WEST),
                Exit("North", 0x01, Sections.BACCUS_LAKE_PIER),
            ],
        ),
        Sections.BACCUS_LAKE_PIER: Transitions(
            [
                Entry("South Entrance", 0x00),
            ],
            [
                Exit("South", 0x00, Sections.BACCUS_LAKE),
            ],
        ),
        Sections.MUSHROOM_FOREST: Transitions(
            [
                Entry("Watch Tower Entrance", 0x01),
                # Entry("Leaf Slider Entrance", 0x02),
                Entry("Stormy Mountain Entrance", 0x03),
                Entry("Lake Entrance", 0x04),
                Entry("Haunted Mansion", 0x05),
            ],
            [
                Exit("Lake", 0x00, Sections.LAKE),
                Exit("Watch Tower", 0x01, Sections.WATCH_TOWER),
                Exit(
                    "Stormy Mountain",
                    0x02,
                    Sections.STORMY_MOUNTAINS_PART_1,
                    lambda state: state.can_reach_location(Cleared(Events.THE_WORLDS_GREATEST_POUT), player),
                ),
                Exit("Haunted Mansion", 0x03, Sections.HAUNTED_MANSION_WEST),
            ],
        ),
        Sections.LAKE: Transitions(
            [
                Entry("Right Entrance", 0x00),
                Entry("Right Door Entrance", 0x01),
                Entry("Left Door Entrance", 0x02),
            ],
            [
                Exit("Right", 0x00, Sections.MUSHROOM_FOREST),
                Exit("Left Door", 0x01, Sections.MANSION_STAIRS_DOWN),
                Exit("Right Door", 0x02, Sections.MANSION_STAIRS_UP),
            ],
        ),
        Sections.MANSION_JUNGLE_PIG_ROOM: Transitions(
            [
                Entry("Right Entrance", 0x0),
            ],
            [
                Exit("Right", 0x00, Sections.MANSION_STAIRS_DOWN),
            ],
        ),
        Sections.MANSION: Transitions(
            [
                Entry("Left Entrance", 0x00),
                Entry("Right Entrance", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.VILLAGE_OF_ALL_BEGINNING),
                Exit("Right", 0x01, Sections.MANSION_STAIRS_UP),
            ],
        ),
        Sections.MANSION_STAIRS_UP: Transitions(
            [
                Entry("Right Entrance", 0x00),
                Entry("Left Entrance", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.MANSION),
                Exit("Right", 0x01, Sections.LAKE),
            ],
        ),
        Sections.MANSION_STAIRS_DOWN: Transitions(
            [
                Entry("Right Entrance", 0x00),
                Entry("Left Entrance", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.MANSION_JUNGLE_PIG_ROOM),
                Exit("Right", 0x01, Sections.LAKE),
            ],
        ),
        Sections.LEAF_SLIDER: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x01, Sections.MUSHROOM_FOREST),
            ],
        ),
        Sections.MASAKARI_JUNGLE: Transitions(
            [
                # Entry("Left Entrance", 0x01),
                Entry("Civilization Entrance", 0x02),
                Entry("River Entrance", 0x03),
            ],
            [
                Exit(
                    "Civilization",
                    0x00,
                    Sections.Y_CROSSING,
                    # Has(Items.MINERS_HAT)
                ),
                Exit(
                    "River",
                    0x01,
                    Sections.MASAKARI_RIVER,
                    lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), player),
                ),
            ],
        ),
        Sections.MASAKARI_RIVER: Transitions(
            [
                Entry("Jungle Entrance", 0x01),
                Entry("Old Tree Hill Entrance", 0x02),
                Entry("Trick Entrance", 0x03),
            ],
            [
                Exit(
                    "Jungle",
                    0x00,
                    Sections.MASAKARI_JUNGLE,
                    lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), player),
                ),
                Exit(
                    "Old Tree Hill",
                    0x01,
                    Sections.OLD_TREE_HILL,
                    lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), player),
                ),
                Exit("Trick Village", 0x02, Sections.TRICK_VILLAGE),
            ],
        ),
        Sections.OLD_TREE_HILL: Transitions(
            [
                Entry("Left Entrance", 0x01),
            ],
            [
                Exit(
                    "River",
                    0x00,
                    Sections.MASAKARI_RIVER,
                    lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), player),
                ),
                # Exit("Jungle", 0x01, Sections.MASAKARI_JUNGLE),
                # Exit("Old Tree Hill", 0x02, Sections.OLD_TREE_HILL),
            ],
        ),
        Sections.TRICK_VILLAGE: Transitions(
            [
                Entry("Pond Entrance", 0x01),
                Entry("Chimney Entrance", 0x02),
                # Entry("Under Hut Entrance", 0x03),
                Entry("River Entrance", 0x04),
            ],
            [
                Exit("Ol' Pond", 0x00, Sections.OL_POND),
                Exit("10,000 Year Old Man's Room", 0x01, Sections.TEN_THOUSAND_YEAR_OLD_MANS_ROOM),
                Exit("River Top", 0x02, Sections.MASAKARI_RIVER),
                # Exit("River Botoom", 0x03, Sections.MASAKARI_RIVER),
            ],
        ),
        Sections.TEN_THOUSAND_YEAR_OLD_MANS_ROOM: Transitions(
            [
                Entry("Chimney Entrance", 0x01),
            ],
            [
                Exit("Chimney", 0x00, Sections.TRICK_VILLAGE),
                # Exit("Bottom", 0x01, Sections.TRICK_VILLAGE),
            ],
        ),
        Sections.LUMBERJACK_FACTORY: Transitions(
            [
                Entry("Left Entrance", 0x00),
                Entry("Broken Door Entrance", 0x01),
            ],
            [
                Exit("Left", 0x00, Sections.Y_CROSSING),
                Exit("Broken Door", 0x01, Sections.DRIED_WISHING_WELL),
            ],
        ),
        Sections.DRIED_WISHING_WELL: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.LUMBERJACK_FACTORY),
            ],
        ),
        Sections.FLOWER_TOWER: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.CHARITY_SQUARE),
            ],
        ),
        Sections.CLOCK_TOWER_ENTRANCE: Transitions(
            [
                Entry("Bottom", 0x00),
                Entry("Top", 0x01),
            ],
            [
                Exit("Up", 0x00, Sections.CLOCK_TOWER_HALFWAY_UP),
                Exit("Y-crossing", 0x01, Sections.Y_CROSSING),
            ],
        ),
        Sections.CLOCK_TOWER_HALFWAY_UP: Transitions(
            [
                Entry("Down Entrance", 0x00),
                Entry("Up Entrance", 0x01),
            ],
            [
                Exit("Down", 0x00, Sections.CLOCK_TOWER_ENTRANCE),
                Exit("Up", 0x01, Sections.CLOCK_TOWER_ENGINE_ROOM),
            ],
        ),
        Sections.CLOCK_TOWER_ENGINE_ROOM: Transitions(
            [
                Entry("Down Entrance", 0x00),
            ],
            [
                Exit("Down", 0x00, Sections.CLOCK_TOWER_HALFWAY_UP),
            ],
        ),
        Sections.IRON_CASTLE_ENTRANCE: Transitions(
            [
                Entry("Bottom Entrance", 0x00),
                Entry("Top Entrance", 0x01),
            ],
            [
                Exit("Down", 0x00, Sections.Y_CROSSING),
                Exit("Top", 0x01, Sections.IRON_CASTLE_MAIN_ROOM),
            ],
        ),
        Sections.IRON_CASTLE_MAIN_ROOM: Transitions(
            [
                Entry("Bottom Entrance", 0x00),
                Entry("Left Entrance", 0x01),
                Entry("Middle Entrance", 0x02),
                Entry("Right Entrance", 0x03),
            ],
            [
                Exit("Bottom", 0x00, Sections.IRON_CASTLE_ENTRANCE),
                Exit("Left", 0x01, Sections.IRON_CASTLE_LEFT_ROOM),
                Exit("Middle", 0x02, Sections.IRON_CASTLE_ENGINE_ROOM),
                Exit("Right", 0x03, Sections.IRON_CASTLE_RIGHT_ROOM),
            ],
        ),
        Sections.IRON_CASTLE_LEFT_ROOM: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.IRON_CASTLE_MAIN_ROOM),
            ],
        ),
        Sections.IRON_CASTLE_RIGHT_ROOM: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.IRON_CASTLE_MAIN_ROOM),
            ],
        ),
        Sections.IRON_CASTLE_ENGINE_ROOM: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.IRON_CASTLE_MAIN_ROOM),
            ],
        ),
        Sections.Y_CROSSING: Transitions(
            [
                Entry("Factory Entrance", 0x01),
                Entry("Iron Castle Entrance", 0x02),
                Entry("Clock Tower Entrance", 0x03),
                Entry("Jungle Entrance", 0x04),
            ],
            [
                Exit(
                    "Factory",
                    0x00,
                    Sections.LUMBERJACK_FACTORY,
                    lambda state: state.can_reach_location(Started(Events.WE_NEED_POWER), player),
                ),
                Exit(
                    "Iron Castle",
                    0x01,
                    Sections.IRON_CASTLE_ENTRANCE,
                    lambda state: state.can_reach_location(Started(Events.WE_NEED_POWER), player),
                ),
                Exit("Clock Tower", 0x02, Sections.CLOCK_TOWER_ENTRANCE),
                Exit("Jungle", 0x03, Sections.MASAKARI_JUNGLE),
            ],
        ),
        Sections.WITCH_HUT: Transitions(
            [
                Entry("Entrance", 0x00),
            ],
            [
                Exit("Exit", 0x00, Sections.VILLAGE_OF_ALL_BEGINNING),
            ],
        ),
        Sections.HIDDEN_VILLAGE: Transitions(
            [
                # Entry("Leaf Butterfly Entrance", 0x01),
                Entry("Ladder Entrance", 0x02),
            ],
            [
                Exit(
                    "Ladder",
                    0x00,
                    Sections.LAVA_CAVES,
                    # Has(Cleared(Events.LAVA_CAVES))
                ),
            ],
        ),
    }


def get_entrance_info(player: int, entrance: str) -> tuple[Section, int]:
    """Given an entrance name, gives the corresponding section and spawn ID"""
    er_transitions = get_randomizable_transitions(player)
    for source, transitions in er_transitions.items():
        for entry in transitions.entries:
            if get_entrance_name(source, entry.name) == entrance:
                return (source, entry.spawn_id)

        for exit in transitions.exits:
            if get_entrance_name(source, exit.name) == entrance:
                return (source, exit.spawn_id)

    raise ValueError(f"Critical error: No entrance found matching {entrance} for entrance randomization")


def connect_regions(world: TombaWorld) -> None:
    for section, transitions in get_randomizable_transitions(world.player).items():
        source = world.get_region(section.name)

        if len(transitions.entries) != len(transitions.exits):
            raise Exception(
                f"Number of entries ({len(transitions.entries)}) and exits ({len(transitions.exits)}) differs for {source}"
            )

        for entry in transitions.entries:
            source.create_er_target(get_entrance_name(section, entry.name))

        for exit in transitions.exits:
            exit_ = source.create_exit(get_entrance_name(section, exit.name))

            if exit.rule is not None:
                world.set_rule(exit_, exit.rule)

            # Connect the correct section if the randomization is disabled
            if not world.options.entrance_randomization and exit.target is not None:
                target = world.get_region(exit.target.name)
                exit_.connect(target)

    connect(
        world,
        Sections.VILLAGE_OF_ALL_BEGINNING.name,
        Sections.FOREST_OF_ALL_BEGINNING_PART_1.name,
        lambda state: state.can_reach_location(Cleared(Events.CLEAR_THE_FOG), world.player),
        entrance_type=EntranceType.TWO_WAY,
    )
    connect(
        world,
        Sections.FOREST_OF_ALL_BEGINNING_PART_1.name,
        Sections.FOREST_OF_ALL_BEGINNING_PART_2.name,
        entrance_type=EntranceType.TWO_WAY,
    )
    connect(world, Sections.GARAGE.name, Sections.MOTOCROSS_COURSE.name, Has(Items.FUEL_BAR))
    connect(
        world,
        Sections.FOREST_OF_100_FLOWERS_PART_1.name,
        Sections.FOREST_OF_100_FLOWERS_PART_2.name,
        entrance_type=EntranceType.TWO_WAY,
    )
    connect(world, Sections.CHARITY_SQUARE.name, Sections.HIDDEN_VILLAGE.name, Has(Items.LEAF_BUTTERFLY, 29))
    connect(
        world,
        Sections.LAVA_CAVES.name,
        Regions.LAVA_CAVES_PURIFIED,
        lambda state: state.can_reach_location(Cleared(Events.LAVA_CAVES), world.player),
    )
    connect(
        world,
        Sections.HAUNTED_MANSION_NORTH.name,
        Sections.HAUNTED_MANSION_EAST.name,
    )
    connect(
        world,
        Sections.HAUNTED_MANSION_NORTH.name,
        Sections.HAUNTED_MANSION_WEST.name,
    )
    connect(
        world,
        Sections.HAUNTED_MANSION_EAST.name,
        Sections.HAUNTED_MANSION_NORTH.name,
    )
    connect(
        world,
        Sections.HAUNTED_MANSION_EAST.name,
        Sections.HAUNTED_MANSION_SOUTH.name,
    )
    connect(
        world,
        Sections.HAUNTED_MANSION_SOUTH.name,
        Sections.HAUNTED_MANSION_EAST.name,
        lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), world.player),
    )
    connect(world, Sections.HAUNTED_MANSION_SOUTH.name, Sections.HAUNTED_MANSION_WEST.name)
    connect(
        world,
        Sections.HAUNTED_MANSION_WEST.name,
        Sections.HAUNTED_MANSION_NORTH.name,
        lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), world.player),
    )
    connect(world, Sections.HAUNTED_MANSION_WEST.name, Sections.HAUNTED_MANSION_SOUTH.name)
    connect(
        world, Sections.HAUNTED_MANSION_NORTH.name, Sections.SUN_TORCH_STAND.name, entrance_type=EntranceType.TWO_WAY
    )
    connect(
        world,
        Sections.HAUNTED_MANSION_SOUTH.name,
        Sections.SUN_TORCH_STAND.name,
        lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), world.player),
        entrance_type=EntranceType.TWO_WAY,
    )
    connect(world, Sections.STORMY_MOUNTAINS_PART_2.name, Sections.BACCUS_VILLAGE.name)
    connect(
        world,
        Sections.STORMY_MOUNTAINS_PART_2.name,
        Sections.MASAKARI_JUNGLE.name,
        lambda state: state.can_reach_location(Cleared(Events.THE_MASTER_OF_THE_SKIES), world.player),
    )
    connect(
        world,
        Sections.UNDERGROUND_MAZE.name,
        Regions.UNDERGROUND_MAZE_INNER,
        Has(Items.THIEFS_WIRE),
    )

    connect(
        world,
        Sections.VILLAGE_OF_ALL_BEGINNING.name,
        Sections.HUNDREDS_YEAR_OLD_MANS_HUT.name,
        Has(Items.HUNDRED_YEAR_OLD_BELL),
        suffix=" with Bell",
    )
    connect(
        world,
        Sections.VILLAGE_OF_ALL_BEGINNING.name,
        Sections.THOUSAND_YEAR_OLD_MANS_ROOM.name,
        Has(Items.THOUSAND_YEAR_OLD_BELL),
        suffix=" with Bell",
    )
    connect(
        world,
        Sections.VILLAGE_OF_ALL_BEGINNING.name,
        Sections.TEN_THOUSAND_YEAR_OLD_MANS_ROOM.name,
        Has(Items.TEN_THOUSAND_YEAR_OLD_BELL),
        suffix=" with Bell",
    )
    connect(
        world,
        Sections.VILLAGE_OF_ALL_BEGINNING.name,
        Sections.MILLION_YEAR_OLD_MANS_ROOM.name,
        Has(Items.MILLION_YEAR_OLD_BELL),
        suffix=" with Bell",
    )
