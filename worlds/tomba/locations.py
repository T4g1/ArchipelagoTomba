from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self
from enum import IntEnum

from collections import defaultdict
from dataclasses import dataclass
from BaseClasses import Location, LocationProgressType
from rule_builder.rules import Has, Rule

from . import constants
from .constants import Regions, Items, Locations, Events
from .items import ItemHandler, ItemData, TombaItem, PANTS
from .sections import Section, Sections
from .helpers import HasStarted, HasCleared, Started, Cleared, Rules
from .events import EventHandler
from .bitutils import Bitmask

if TYPE_CHECKING:
    from .world import TombaWorld


def get_name(name: str, region: str):
    return f"{name} ({region})"


class LocationType(IntEnum):
    PICKUP = 0
    REWARD = 1
    CHEST = 2


@dataclass
class LocationData:
    _id_counter: ClassVar[int] = 1  # ID 0 is reserved

    id: int
    name: str
    region: str
    item: ItemData | None
    progress_type: LocationProgressType
    sections: Section | None
    rule: Rule | None
    at: Bitmask | None
    type: LocationType

    def __init__(
        self,
        name: str,
        region: str,
        item: ItemData | None = None,
        section: Section | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
        at: Bitmask | None = None,
        type: LocationType = LocationType.PICKUP,
    ):
        self.id = LocationData._id_counter
        LocationData._id_counter += 1

        self.name = name
        self.region = region
        self.progress_type = progress_type
        self.item = item
        self.section = section
        self.rule = rule
        self.at = at
        self.type = type

    def with_section(self, section: Section) -> Self:
        self.section = section
        return self

    def is_bonus(self) -> bool:
        return self.item is not None and self.item.is_bonus()

    def is_chest(self) -> bool:
        return self.type is LocationType.CHEST

    def __repr__(self) -> str:
        return self.name


@dataclass
class ItemLocData(LocationData):
    x: int | None
    y: int | None
    related_event: str

    # Kept for Poptracker
    base_name: str

    def __init__(
        self,
        name: str,
        region: str,
        item_name: str,
        section: Section | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
        at: Bitmask | None = None,
        event: str | None = None,
        type: LocationType = LocationType.PICKUP,
    ):
        self.base_name = name

        name = get_name(name, region)

        item = ItemHandler.by_name.get(item_name, None)
        if item is None:
            raise Exception(f"Trying to create a location {name} with an unknown item: {item_name}")

        super().__init__(name, region, item, section, progress_type, rule, at, type)

        self.event = event


@dataclass
class ChestLocData(ItemLocData):
    def __init__(
        self,
        name: str,
        region: str,
        item_name: str,
        section: Section | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
        at: Bitmask | None = None,
    ):
        super().__init__(name, region, item_name, section, progress_type, rule, at, type=LocationType.CHEST)


class LocationHandler:
    location_table: list[LocationData] = [
        # Village of all Beginnings
        # TODO: Find where this is called in game (reverse)
        # Not yet working. This Max Vit+1 is given by the Witch after giving her the Cold Medicine which clears the event Take Two of These
        # ItemLocData(
        # Locations.VITALITY_INCREASE,
        # Regions.VILLAGE_OF_ALL_BEGINNINGS,
        # Items.MAX_VITALITY_1,
        # Section(0x12, 0x02),
        # rule=HasStarted(Events.THE_CUTE_WITCH) & Has(Items.COLD_MEDICINE),
        # ),
        ItemLocData(
            "What the Witch Lost",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.MAGIC_MIRROR,
            rule=HasStarted(Events.THE_CUTE_WITCH) & Has(Items.DIRTY_MIRROR) & Has(Items.THREE_CRYSTAL_BALLS),
        ),
        ItemLocData(
            "Magic Mirror",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.GRAPPLEJACK,
            rule=HasStarted(Events.THE_CUTE_WITCH)
            & Has(Items.DIRTY_MIRROR)
            & Has(Items.THREE_CRYSTAL_BALLS)
            & Has(Items.GRAPPLE)
            & Has(Items.BLACKJACK),  # Clean Mirror is no use
        ),
        ItemLocData(
            "Make Candy",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.GOLD_CANDY,
            rule=HasStarted(Events.THE_CUTE_WITCH)
            & Has(Items.BITING_PLANT_FLOWER)
            & Has(Items.BUTAMUSHI_THORN)
            & Has(Items.KOKKA_CLAW)
            & Has(Items.MOLASSES)
            & Has(Items.NEEDLEGATOR_TEETH)
            & Has(Items.SILVER_POWDER),
        ),
        ItemLocData(
            Locations.MAILBOX,
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.FURIOUS_TORNADO,
            at=Bitmask(0x09BCEC, 0x01),
        ),
        ItemLocData("Peach Flower Gas", Regions.VILLAGE_OF_ALL_BEGINNINGS, Items.BABY_PIG),
        ItemLocData(
            Locations.KOKKA_EGG_1,
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.VILLAGE_OF_ALL_BEGINNING,
            at=Bitmask(0x09BCFD, 0x08),
        ),
        ChestLocData(
            "100 Year Old Bell",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.HUNDRED_YEAR_OLD_BELL,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BCFC, 0x02),
        ),
        # Forest of all Beginnings
        ItemLocData(
            Locations.VITALITY_INCREASE,
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.MAX_VITALITY_1,
            Sections.FOREST_OF_ALL_BEGINNING_PART_1,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BCFE, 0x40),
        ),
        ItemLocData(
            Locations.BITING_PLANT_FLOWER,
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.BITING_PLANT_FLOWER,
            Sections.FOREST_OF_ALL_BEGINNING_PART_1,
        ),
        ChestLocData(
            "10,000 Year Chest",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.LUNCH_BOX,
            Sections.FOREST_OF_ALL_BEGINNING_PART_1,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BCFE, 0x80),
        ),
        ItemLocData(
            Locations.KOKKA_EGG_2,
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.FOREST_OF_ALL_BEGINNING_PART_1,
            at=Bitmask(0x09BCFF, 0x08),
        ),
        ItemLocData(
            Locations.KOKKA_EGG_3,
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.FOREST_OF_ALL_BEGINNING_PART_2,
            at=Bitmask(0x09BCFF, 0x10),
        ),
        ItemLocData(
            Locations.KOKKA_EGG_4,
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.FOREST_OF_ALL_BEGINNING_PART_2,
            at=Bitmask(0x09BD01, 0x01),
        ),
        ChestLocData(
            "100 Year Chest near the Hut",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHARITY_WINGS,
            Sections.FOREST_OF_ALL_BEGINNING_PART_2,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD02, 0x20),
        ),
        ItemLocData(
            "1Up",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.ONE_UP,
            Sections.FOREST_OF_ALL_BEGINNING_PART_2,
            at=Bitmask(0x09BD01, 0x10),
        ),
        ItemLocData(
            "100 Year Old Reward",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.HUNDRED_YEAR_OLD_KEY,
            rule=HasCleared(Events.INSIDE_THE_KOKKA_EGGS),
        ),
        # Ol' Pond
        ItemLocData("Drown", Regions.OL_POND, Items.BANANAS, Sections.OL_POND),
        ItemLocData("AP Box", Regions.OL_POND, Items.CHEESE, Sections.OL_POND),
        ItemLocData("1Up 1", Regions.OL_POND, Items.ONE_UP, Sections.OL_POND, event=Events.TAKE_ME_HOME),
        ItemLocData("1Up 2", Regions.OL_POND, Items.ONE_UP, Sections.OL_POND, event=Events.TAKE_ME_HOME),
        ChestLocData(
            "10,000 Year Old Chest",
            Regions.OL_POND,
            Items.TEN_THOUSAND_YEAR_OLD_BELL,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY)
            & (
                Rules.CAN_SWIM
                | Has(Items.FUNKY_PARASOL)
                | Has(Items.SACRED_FISH)
                | Has(Items.PSYCHIC_FISH)
                | (Has(Items.BLUE_POWDER) & Rules.CAN_REACH_MUSHROOM_FOREST)
            ),
            at=Bitmask(0x09BD02, 0x40),
        ),
        # Forest of 100 Flowers
        *[
            ItemLocData(
                f"Leaf Butterfly {index}",
                Regions.FOREST_OF_100_FLOWERS,
                Items.LEAF_BUTTERFLY,
                Sections.FOREST_OF_100_FLOWERS,
            )
            for index in range(1, 26)
        ],
        ChestLocData(
            Locations.VITALITY_INCREASE,
            Regions.FOREST_OF_100_FLOWERS,
            Items.MAX_VITALITY_1,
            Sections.FOREST_OF_100_FLOWERS,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD1C, 0x01),
        ),
        ItemLocData(
            Locations.CAMPFIRE, Regions.FOREST_OF_100_FLOWERS, Items.BAKED_YAM, rule=Has(Items.BUCKET_OF_WATER)
        ),
        ChestLocData(
            Locations.HIDDEN_CHEST_FOREST_100_FLOWER_1,
            Regions.FOREST_OF_100_FLOWERS,
            Items.CHARITY_WINGS,
            Sections.FOREST_OF_100_FLOWERS,
            at=Bitmask(0x09BD1D, 0x01),
        ),
        ChestLocData(
            Locations.HIDDEN_CHEST_FOREST_100_FLOWER_2,
            Regions.FOREST_OF_100_FLOWERS,
            Items.CHARITY_WINGS,
            Sections.FOREST_OF_100_FLOWERS,
            at=Bitmask(0x09BD1D, 0x01),
        ),
        ChestLocData(
            "On Top of the Spikes",
            Regions.FOREST_OF_100_FLOWERS,
            Items.WOOD_BOOMERANG,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD1C, 0x20),
        ),
        # Watch Tower
        ChestLocData(
            "1Up 1",
            Regions.WATCH_TOWER,
            Items.ONE_UP,
            Sections.WATCH_TOWER,
            at=Bitmask(0x09BD1F, 0x08),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ChestLocData(
            "1Up 2",
            Regions.WATCH_TOWER,
            Items.ONE_UP,
            Sections.WATCH_TOWER,
            at=Bitmask(0x09BD1F, 0x08),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(Locations.TELESCOPE, Regions.WATCH_TOWER, Items.TELESCOPE),
        ItemLocData("Push the Boulder", Regions.WATCH_TOWER, Items.DIRTY_MIRROR),
        ItemLocData(
            "Find the seeds",
            Regions.WATCH_TOWER,
            Items.FLOWER_SEEDS,
            rule=HasCleared(Events.A_LOST_CHILD) & HasCleared(Events.THE_100_FLOWER_FOREST),
        ),
        ChestLocData(
            Locations.WATCH_TOWER_PANTS,
            Regions.WATCH_TOWER,
            Items.JUMPING_PANTS,
            Sections.WATCH_TOWER,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD20, 0x02),
        ),
        ChestLocData(
            "10,000 Year Chest",
            Regions.WATCH_TOWER,
            Items.LARGE_LUNCH_BOX,
            Sections.WATCH_TOWER,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD1D, 0x08),
        ),
        ChestLocData(
            "Million Year Chest",
            Regions.WATCH_TOWER,
            Items.MILLION_YEAR_OLD_BELL,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BD20, 0x01),
        ),
        ItemLocData(Locations.FILL_THE_BUCKET, Regions.WATCH_TOWER, Items.BUCKET_OF_WATER, rule=Has(Items.BUCKET)),
        ItemLocData(
            "Win the Race", Regions.WATCH_TOWER, Items.SILVER_POWDER, rule=HasCleared(Events.THE_WORLDS_GREATEST_POUT)
        ),
        # Wobbly Wharf
        ChestLocData(
            "100 Year Old Apples",
            Regions.WOBBLY_WHARF,
            Items.APPLE,
            Sections.WOBBLY_WHARF,
            # rule=Has(Items.HUNDRED_YEAR_OLD_KEY), # This chest does not require a key
            at=Bitmask(0x09BD23, 0x01),
        ),
        # This one can also be found by using the bucket of water in forest of 100 flowers
        ItemLocData("Find a bucket", Regions.WOBBLY_WHARF, Items.BUCKET, rule=Rules.CAN_BIG_JUMP),
        # Dwarf Village
        # TODO: Find where this is called in game (reverse)
        # Not yet working. This Max Vit+1 is given by the lady after giving her the Baked Yam which clears the event Something's Cooking
        # ItemLocData(
        # Locations.VITALITY_INCREASE,
        # Regions.DWARF_VILLAGE,
        # Items.MAX_VITALITY_1,
        # Sections.DWARF_VILLAGE,
        # rule=HasCleared(Events.SOMETHINGS_COOKIN),
        # ),
        ItemLocData(
            Locations.BARON,
            Regions.DWARF_VILLAGE,
            Items.BARON,
            rule=Has(Items.SEAWEED) & HasCleared(Events.DELICIOUS_KNOWLEDGE_FRUIT),
        ),
        ItemLocData("Rescue the Child", Regions.DWARF_VILLAGE, Items.CHEESE, Sections.DWARF_VILLAGE),
        ItemLocData("Meet the Dwarf Elder", Regions.DWARF_VILLAGE, Items.BLUE_EVIL_PIG_BAG),
        ItemLocData("Plant a Garden", Regions.DWARF_VILLAGE, Items.GOLD_FLOWER, rule=HasCleared(Events.FLOWER_SEEDS)),
        ChestLocData(
            "1,000 Year Chest",
            Regions.DWARF_VILLAGE,
            Items.CHARITY_WINGS,
            Sections.DWARF_VILLAGE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            # TODO: Can't find the bitmask for that one
        ),
        ItemLocData(
            Locations.FIRE_STARTER, Regions.DWARF_VILLAGE, Items.TORCH, rule=HasStarted(Events.WHERED_THE_LIGHTS_GO)
        ),
        ItemLocData(Locations.JAIL, Regions.DWARF_VILLAGE, Items.BROKEN_VASE, rule=Has(Items.TORCH)),
        # Mushroom Forest
        ChestLocData(
            "100 Year Old AP Crystal",
            Regions.MUSHROOM_FOREST,
            Items.AP_CRYSTAL,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1E, 0x80),
        ),
        ItemLocData("AP Box", Regions.MUSHROOM_FOREST, Items.ORDINARY_MUSHROOM, rule=Has(Locations.AP_150_000)),
        ItemLocData("Tear Jar", Regions.MUSHROOM_FOREST, Items.TEAR_JAR, rule=HasCleared(Events.THE_100_FLOWER_FOREST)),
        ChestLocData(
            "Mysterious Mushroom",
            Regions.MUSHROOM_FOREST,
            Items.MYSTERIOUS_MUSHROOM,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1C, 0x10),
        ),
        ChestLocData(
            "1,000 Year Old Bell",
            Regions.MUSHROOM_FOREST,
            Items.THOUSAND_YEAR_OLD_BELL,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1C, 0x08),
        ),
        ChestLocData(
            "1,000 Year Chest near the Stairs",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x10),
        ),
        ChestLocData(
            "1,000 Year Chest in the Pit",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x01),
        ),
        ChestLocData(
            "10,000 Year Chest",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x04),
        ),
        ChestLocData(
            "Chest near the Spikes",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1C, 0x01),
        ),
        ChestLocData(
            "1Up",
            Regions.MUSHROOM_FOREST,
            Items.ONE_UP,
            Sections.MUSHROOM_FOREST,
            at=Bitmask(0x09BE1C, 0x20),
        ),
        ChestLocData(
            "1Up 1,000 Year Old 1",
            Regions.MUSHROOM_FOREST,
            Items.ONE_UP,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x40),
        ),
        ChestLocData(
            "1Up 1,000 Year Old 2",
            Regions.MUSHROOM_FOREST,
            Items.ONE_UP,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x20),
        ),
        ChestLocData(
            "1Up Million Year Old 1",
            Regions.MUSHROOM_FOREST,
            Items.ONE_UP,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x08),
        ),
        ChestLocData(
            "1Up Million Year Old 2",
            Regions.MUSHROOM_FOREST,
            Items.ONE_UP,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x08),
        ),
        ChestLocData(
            "1Up 10,000 Year Old",
            Regions.MUSHROOM_FOREST,
            Items.ONE_UP,
            Sections.MUSHROOM_FOREST,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1F, 0x02),
        ),
        ItemLocData(Locations.MONSTER_HUNT, Regions.MUSHROOM_FOREST, Items.RISE_AND_SHINE_POWDER),
        # Charity Square
        ChestLocData(
            "10,000 Year Old AP Crystal",
            Regions.CHARITY_SQUARE,
            Items.AP_CRYSTAL,
            Sections.CHARITY_SQUARE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD1F, 0x02),
        ),
        ChestLocData(
            "1,000 Year Old AP Crystal",
            Regions.CHARITY_SQUARE,
            Items.AP_CRYSTAL,
            at=Bitmask(0x09BD1F, 0x01),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData("Sacred Fish", Regions.CHARITY_SQUARE, Items.SACRED_FISH, rule=HasCleared(Events.THE_FLOWER_TOWER)),
        ItemLocData(
            "Crystal Balls",
            Regions.CHARITY_SQUARE,
            Items.THREE_CRYSTAL_BALLS,
            rule=Rules.CAN_BIG_JUMP
            | Has(Items.WOOD_BOOMERANG)
            | Has(Items.STONE_BOOMERANG)
            | Has(Items.IRON_BOOMERANG)
            | Has(Items.FUNKY_PARASOL)
            | Has(Items.JEWEL_OF_FIRE)
            | Has(Items.JEWEL_OF_WATER)
            | Has(Items.JEWEL_OF_WIND),
        ),
        ChestLocData(
            "1Up 1",
            Regions.CHARITY_SQUARE,
            Items.ONE_UP,
            Sections.CHARITY_SQUARE,
            rule=Has(Items.MILLION_YEAR_OLD_KEY) & (Rules.CAN_GRAPPLE | Has(Items.FUNKY_PARASOL)),
            at=Bitmask(0x09BD1F, 0x04),
        ),
        ChestLocData(
            "1Up 2",
            Regions.CHARITY_SQUARE,
            Items.ONE_UP,
            Sections.CHARITY_SQUARE,
            rule=Has(Items.MILLION_YEAR_OLD_KEY) & (Rules.CAN_GRAPPLE | Has(Items.FUNKY_PARASOL)),
            at=Bitmask(0x09BD1F, 0x04),
        ),
        ItemLocData(
            "Charity Entrance Left",
            Regions.CHARITY_SQUARE,
            Items.CHARITY_WINGS,
            Sections.CHARITY_SQUARE,
            at=Bitmask(0x09BD20, 0x10),
        ),
        ItemLocData(
            "Charity Entrance Right",
            Regions.CHARITY_SQUARE,
            Items.CHARITY_WINGS,
            Sections.CHARITY_SQUARE,
            at=Bitmask(0x09BD20, 0x20),
        ),
        # Mansion
        ChestLocData(
            "100 Year Old Chest",
            Regions.MANSION,
            Items.AP_CRYSTAL,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1C, 0x40),
        ),
        ChestLocData(
            "1,000 Year Old Chest",
            Regions.MANSION,
            Items.AP_CRYSTAL,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1C, 0x80),
        ),
        ChestLocData(
            "10,000 Year Old AP Crystals",
            Regions.MANSION,
            Items.AP_CRYSTAL,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1D, 0x01),
        ),
        ChestLocData(
            "1Up 1",
            Regions.MANSION,
            Items.ONE_UP,
            Sections.MANSION,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1D, 0x02),
        ),
        ChestLocData(
            "1Up 2",
            Regions.MANSION,
            Items.ONE_UP,
            Sections.MANSION,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1D, 0x02),
        ),
        ChestLocData(
            "1Up 3",
            Regions.MANSION,
            Items.ONE_UP,
            Sections.MANSION,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE1D, 0x02),
        ),
        ItemLocData("Familiar Beach", Regions.MANSION, Items.SEAWEED, rule=HasStarted(Events.SEAWEED_FOR_YOUR_HEALTH)),
        # Stormy Mountain
        ChestLocData(
            "100 Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.LUNCH_BOX,
            Sections.STORMY_MOUNTAINS,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD5C, 0x10),
        ),
        ChestLocData(
            "1,000 Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.LARGE_LUNCH_BOX,
            Sections.STORMY_MOUNTAINS,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY) & Rules.CAN_GRAPPLE,
            at=Bitmask(0x09BD5C, 0x01),
        ),
        ChestLocData(
            "Million Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.IRON_BOOMERANG,
            rule=Has(Items.MILLION_YEAR_OLD_KEY)
            & (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                | (HasCleared(Events.A_HUNGRY_MONKEY) & (Has(Items.DASHING_PANTS) | Has(Items.FLASH_PANTS)))
                | Rules.HAS_ANY_FISH
                | Rules.HAS_ANY_JEWEL
                | Rules.HAS_BLUE_POWDER
            ),
            at=Bitmask(0x09BD5C, 0x08),
        ),
        ChestLocData(
            "1Up 1,000 Year Old 1",
            Regions.STORMY_MOUNTAIN,
            Items.ONE_UP,
            Sections.STORMY_MOUNTAINS,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
            & Rules.CAN_GRAPPLE
            & (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                | (Rules.CAN_DASH & Rules.HAS_PANTS_LEVEL_2)
                | Rules.HAS_ANY_FISH
                | Rules.HAS_ANY_JEWEL
                | Rules.HAS_BLUE_POWDER
            ),
            at=Bitmask(0x09BD5C, 0x02),
        ),
        ChestLocData(
            "1Up 1,000 Year Old 2",
            Regions.STORMY_MOUNTAIN,
            Items.ONE_UP,
            Sections.STORMY_MOUNTAINS,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
            & Rules.CAN_GRAPPLE
            & (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                | (Rules.CAN_DASH & Rules.HAS_PANTS_LEVEL_2)
                | Rules.HAS_ANY_FISH
                | Rules.HAS_ANY_JEWEL
                | Rules.HAS_BLUE_POWDER
            ),
            at=Bitmask(0x09BD5C, 0x02),
        ),
        ChestLocData(
            "1Up 10,000 Year Old 1",
            Regions.STORMY_MOUNTAIN,
            Items.ONE_UP,
            Sections.STORMY_MOUNTAINS,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY)
            & Rules.CAN_GRAPPLE
            & ((HasCleared(Events.PHOENIX_MOUNTAIN) & Rules.CAN_BIG_JUMP) | Rules.CAN_BIGGEST_JUMP),
            at=Bitmask(0x09BD5C, 0x04),
        ),
        ChestLocData(
            "1Up 10,000 Year Old 2",
            Regions.STORMY_MOUNTAIN,
            Items.ONE_UP,
            Sections.STORMY_MOUNTAINS,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY)
            & Rules.CAN_GRAPPLE
            & ((HasCleared(Events.PHOENIX_MOUNTAIN) & Rules.CAN_BIG_JUMP) | Rules.CAN_BIGGEST_JUMP),
            at=Bitmask(0x09BD5C, 0x04),
        ),
        ItemLocData(
            "Smile Wing",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            Sections.STORMY_MOUNTAINS_SECOND,
            at=Bitmask(0x09C3E4, 0x01),
        ),
        ItemLocData(
            "Funga",
            Regions.STORMY_MOUNTAIN,
            Items.MOLASSES,
            rule=Has(Items.FUNGA_DRUM)
            & (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                | (Rules.CAN_DASH & Rules.HAS_PANTS_LEVEL_2)
                | Rules.HAS_ANY_FISH
                | Rules.HAS_ANY_JEWEL
                | Rules.HAS_BLUE_POWDER
            ),
        ),
        ItemLocData(
            "Dig",
            Regions.STORMY_MOUNTAIN,
            Items.CHEESE,
            Sections.STORMY_MOUNTAINS_SECOND,
            rule=HasCleared(Events.PHOENIX_MOUNTAIN),
            at=Bitmask(0x09C365, 0x01),
        ),
        ItemLocData(
            "When the Wind Dies Down",
            Regions.STORMY_MOUNTAIN,
            Items.LARGE_LUNCH_BOX,
            Sections.STORMY_MOUNTAINS_SECOND,
            rule=HasCleared(Events.PHOENIX_MOUNTAIN),
            at=Bitmask(0x09C3E5, 0x01),
            event=Events.WHEN_THE_WIND_DIES_DOWN,
        ),
        ChestLocData(
            Locations.VITALITY_INCREASE,
            Regions.STORMY_MOUNTAIN,
            Items.MAX_VITALITY_1,
            Sections.STORMY_MOUNTAINS_SECOND,
            rule=Has(Items.MILLION_YEAR_OLD_KEY)
            & (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                | Rules.CAN_BIG_JUMP
                | Rules.CAN_GRAPPLE
                | Rules.HAS_ANY_JEWEL
                | Rules.HAS_BLUE_POWDER
            ),
            at=Bitmask(0x09BD5D, 0x08),
        ),
        ItemLocData("Big Keyhole", Regions.STORMY_MOUNTAIN, Items.RED_EVIL_PIG_BAG, rule=Has(Items.BIG_KEY)),
        ItemLocData(
            "Herbs",
            Regions.STORMY_MOUNTAIN,
            Items.HEALING_HERBS,
            at=Bitmask(0x09BD5E, 0x08),
        ),
        ItemLocData(
            "Give back the Pants",
            Regions.STORMY_MOUNTAIN,
            Items.FUNKY_PARASOL,
            rule=Has(Items.CHARLES_PANTS)
            & (Rules.CAN_BIG_JUMP | Rules.CAN_GRAPPLE | Rules.HAS_ANY_JEWEL | HasCleared(Events.PHOENIX_MOUNTAIN)),
            event=Events.CHARLES_PANTS,
        ),
        ChestLocData(
            Locations.STORMY_MOUNTAIN_PANTS,
            Regions.STORMY_MOUNTAIN,
            Items.DASHING_PANTS,
            Sections.STORMY_MOUNTAINS_SECOND,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD5D, 0x80),
        ),
        ChestLocData(
            "100 Year Old Chest Wing 1",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            Sections.STORMY_MOUNTAINS_SECOND,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY) & Rules.CAN_GRAPPLE
            | (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                & (
                    HasCleared(Events.A_HUNGRY_MONKEY)
                    & (Rules.HAS_PANTS_LEVEL_1 | Has(Items.JEWEL_OF_FIRE) | Has(Items.JEWEL_OF_WATER))
                    | Has(Items.JEWEL_OF_WIND)
                    | Rules.HAS_ANY_FISH
                    | Rules.HAS_BLUE_POWDER
                )
            ),
            at=Bitmask(0x09BD5D, 0x20),
        ),
        ChestLocData(
            "100 Year Old Chest Wing 2",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            Sections.STORMY_MOUNTAINS_SECOND,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY) & Rules.CAN_GRAPPLE
            | (
                HasCleared(Events.PHOENIX_MOUNTAIN)
                & (
                    HasCleared(Events.A_HUNGRY_MONKEY)
                    & (Rules.HAS_PANTS_LEVEL_1 | Has(Items.JEWEL_OF_FIRE) | Has(Items.JEWEL_OF_WATER))
                    | Has(Items.JEWEL_OF_WIND)
                    | Rules.HAS_ANY_FISH
                    | Rules.HAS_BLUE_POWDER
                )
            ),
            at=Bitmask(0x09BD5D, 0x20),
        ),
        ChestLocData(
            "Grapple",
            Regions.STORMY_MOUNTAIN,
            Items.GRAPPLE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD5D, 0x40),
        ),
        # Lava Caves
        ItemLocData(Locations.CHARLES_PANTS, Regions.LAVA_CAVES, Items.CHARLES_PANTS),
        ChestLocData(
            "Green Evil Pig Bag Chest",
            Regions.LAVA_CAVES,
            Items.GREEN_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x01),
        ),
        ItemLocData(
            "Bunk Flower 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD5F, 0x08),
        ),
        ItemLocData(
            "Bunk Flower 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD5F, 0x10),
        ),
        ItemLocData(
            "Bunk Flower 3",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD5F, 0x20),
        ),
        ItemLocData(
            "Bunk Flower 4",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD5F, 0x80),
        ),
        ItemLocData(
            "Bunk Flower 5",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD5F, 0x40),
        ),
        ItemLocData(
            "Bunk Flower 6",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD60, 0x02),
        ),
        ItemLocData(
            "Bunk Flower 7",
            Regions.LAVA_CAVES_PURIFIED,
            Items.BUNK_FLOWER,
            Sections.LAVA_CAVES,
            at=Bitmask(0x09BD60, 0x01),
        ),
        ItemLocData(
            "Leave Hidden Village",
            Regions.LAVA_CAVES_PURIFIED,
            Items.WHAT_THE_THIEF_LOST,
            rule=Rules.CAN_GRAPPLE | Has(Items.LEAF_BUTTERFLY, 29),
            at=Bitmask(0x09BD62, 0x20),
        ),
        ChestLocData(
            Locations.VITALITY_INCREASE,
            Regions.LAVA_CAVES_PURIFIED,
            Items.MAX_VITALITY_1,
            Sections.LAVA_CAVES,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x01),
        ),
        ChestLocData(
            "1Up 100 Year 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x08),
        ),
        ChestLocData(
            "1Up 1,000 Year Down",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x20),
        ),
        ChestLocData(
            "1Up 1,000 Year 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x04),
        ),
        ChestLocData(
            "1Up 1,000 Year 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x04),
        ),
        ChestLocData(
            "1Up 10,000 Year Up",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x08),
        ),
        ChestLocData(
            "1Up 10,000 Year Down",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x40),
        ),
        ChestLocData(
            "1Up Million Year 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x80),
        ),
        ChestLocData(
            "1Up Million Year 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.ONE_UP,
            Sections.LAVA_CAVES,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x80),
        ),
        ItemLocData(
            "In Lava Caves Alcove",
            Regions.LAVA_CAVES_PURIFIED,
            Items.WHAT_THE_THIEF_FORGOT,
            rule=HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ChestLocData(
            "10,000 Year Charity Wing 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x10),
        ),
        ChestLocData(
            "10,000 Year Charity Wing 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x10),
        ),
        ChestLocData(
            "1,000 Year Charity Wing 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x02),
        ),
        ChestLocData(
            "1,000 Year Charity Wing 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x02),
        ),
        ChestLocData(
            "Million Year Large Lunch",
            Regions.LAVA_CAVES_PURIFIED,
            Items.LARGE_LUNCH_BOX,
            Sections.LAVA_CAVES,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x02),
        ),
        ChestLocData(
            "Lunch Box",
            Regions.LAVA_CAVES_PURIFIED,
            Items.LUNCH_BOX,
            Sections.LAVA_CAVES,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD61, 0x04),
        ),
        # Baccus Village
        ItemLocData(
            Locations.VITALITY_INCREASE,
            Regions.BACCUS_VILLAGE,
            Items.MAX_VITALITY_1,
            Sections.BACCUS_VILLAGE,
            rule=Has(Items.WEED_KILLER),
            event=Events.DEATH_FRUIT_JUICE,
        ),
        ItemLocData(
            Locations.SOME_CHEESE_PLEASE_1,
            Regions.BACCUS_VILLAGE,
            Items.LARGE_LUNCH_BOX,
            Sections.BACCUS_VILLAGE,
            rule=Has(Items.CHEESE, 10),
            event=Events.SOME_CHEESE_PLEASE,
        ),
        ItemLocData(
            Locations.SOME_CHEESE_PLEASE_2,
            Regions.BACCUS_VILLAGE,
            Items.LARGE_LUNCH_BOX,
            Sections.BACCUS_VILLAGE,
            rule=Has(Items.CHEESE, 10),
            event=Events.SOME_CHEESE_PLEASE,
        ),
        ItemLocData(Locations.GOLDEN_FRUIT, Regions.BACCUS_VILLAGE, Items.GOLDEN_FRUIT, rule=Has(Items.CHEESE, 15)),
        ItemLocData(
            Locations.GROWNUPS, Regions.BACCUS_VILLAGE, Items.WEED_KILLER, rule=HasCleared(Events.MONSTER_HUNT)
        ),
        ItemLocData(
            "Give the Baby Pig",
            Regions.BACCUS_VILLAGE,
            Items.KOKKA_CLAW,
            Sections.BACCUS_VILLAGE,
            rule=Has(Items.BABY_PIG) & HasCleared(Events.CANT_STOP_CRYING),
        ),
        ItemLocData(
            "Weed Killer",
            Regions.BACCUS_VILLAGE,
            Items.CHARITY_WINGS,
            Sections.BACCUS_VILLAGE,
            rule=HasStarted(Events.DEATH_FRUIT_JUICE),
        ),
        # Central Park
        ChestLocData(
            Locations.CENTRAL_PARK_CHEST,
            Regions.CENTRAL_PARK,
            Items.ORANGE_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
            & HasCleared(Events.WHERES_THE_BABY_MOUSE)
            & HasCleared(Events.A_DRINK_FOR_GROWNUPS),
            at=Bitmask(0x09BD9C, 0x01),
        ),
        ItemLocData("Baccus Wine", Regions.CENTRAL_PARK, Items.WINE, rule=HasStarted(Events.FOOD_FOR_FUEL)),
        # Haunted Mansion
        ChestLocData(
            "100 Year Old Apples",
            Regions.HAUNTED_MANSION,
            Items.APPLE,
            Section(0x04, 0x0C),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x10),
        ),
        ChestLocData(
            Locations.VITALITY_INCREASE,
            Regions.HAUNTED_MANSION,
            Items.MAX_VITALITY_1,
            Sections.CIVILIZATION_ROOM,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7E, 0x40),
        ),
        ItemLocData(
            "Unbreakable Wire", Regions.HAUNTED_MANSION, Items.STRONG_WIRE, rule=HasStarted(Events.UNBREAKABLE_WIRE)
        ),
        ChestLocData(
            "100 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x0C),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x20),
        ),
        ChestLocData(
            "100 Year Old Chest 2",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x0C),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x20),
        ),
        ItemLocData(
            "What's Underwater ?",
            Regions.HAUNTED_MANSION,
            Items.MIGHTY_FISH_FOOD,
            rule=Has(Items.SEASHELL_NECKLACE) & HasCleared(Events.THE_10000_YEAR_OLD_MAN),
        ),
        ChestLocData(
            "1,000 Year Old Chest near Yan",
            Regions.HAUNTED_MANSION,
            Items.LUNCH_BOX,
            Section(0x04, 0x0C),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x40),
        ),
        ChestLocData(
            "1,000 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            Section(0x04, 0x06),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x02),
        ),
        ChestLocData(
            "10,000 Year Old Chest",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            Section(0x04, 0x10),
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x80),
        ),
        ChestLocData(
            "Million Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            Section(0x04, 0x04),
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x01),
        ),
        ItemLocData(
            Locations.CRY_CHEESE_LEFT,
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Sections.CRY_ROOM,
            at=Bitmask(0x09BD7E, 0x20),
        ),
        ItemLocData(
            Locations.CRY_CHEESE_RIGHT,
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Sections.CRY_ROOM,
            at=Bitmask(0x09BD7E, 0x10),
        ),
        ChestLocData(
            "Pink Evil Bag",
            Regions.HAUNTED_MANSION,
            Items.PINK_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY) & Has(Items.BIG_KEY),
            at=Bitmask(0x09BD7C, 0x04),
        ),
        ItemLocData(
            "Use Small Key",
            Regions.HAUNTED_MANSION,
            Items.ONE_UP,
            Sections.HAUNTED_MANSION_NORTH,
            rule=Has(Items.SMALL_KEY),
            event=Events.A_SMALL_KEY_HOLE,
        ),
        ChestLocData(
            "Near the Magic Egg",
            Regions.HAUNTED_MANSION,
            Items.BOSS_JEWEL,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY) & Has(Items.SMALL_KEY) & HasCleared(Events.THE_HAUNTED_MANSION),
            at=Bitmask(0x09BD7E, 0x80),
        ),
        ItemLocData("Save the Villager", Regions.HAUNTED_MANSION, Items.SMALL_KEY),
        ItemLocData(
            "Near the Million Year Old Chest",
            Regions.HAUNTED_MANSION,
            Items.LARGE_KEY_PANEL_1,
            at=Bitmask(0x09BD7D, 0x01),
        ),
        ItemLocData("Near the Healing Fountain", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_2),
        ItemLocData("Near the Siren", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_3),
        ItemLocData("On the Elevator", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_4),
        ItemLocData(
            "Near the Forest Pig Entrance",
            Regions.HAUNTED_MANSION,
            Items.LARGE_KEY_PANEL_5,
            at=Bitmask(0x09BD7D, 0x10),
        ),
        ItemLocData("In the Chimney", Regions.HAUNTED_MANSION, Items.JEWEL_OF_FIRE),
        ItemLocData(
            "Save the Old Man",
            Regions.HAUNTED_MANSION,
            Items.THOUSAND_YEAR_OLD_KEY,
            rule=HasCleared(Events.BREAK_THE_MAGIC_EGG),
            event=Events.THE_1000_YEAR_OLD_MAN,
        ),
        ItemLocData(
            "Thief in the Chimney 1",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x02),
            rule=Has(Items.WHAT_THE_THIEF_FORGOT) & HasCleared(Events.THE_HAUNTED_MANSION),
            event=Events.WHAT_THE_THIEF_FORGOT,
        ),
        ItemLocData(
            "Thief in the Chimney 2",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x02),
            rule=Has(Items.WHAT_THE_THIEF_FORGOT) & HasCleared(Events.THE_HAUNTED_MANSION),
            event=Events.WHAT_THE_THIEF_FORGOT,
        ),
        ChestLocData(
            "Stone Boomerang",
            Regions.HAUNTED_MANSION,
            Items.STONE_BOOMERANG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x08),
        ),
        ItemLocData(
            Locations.PAINTING_OF_A_BIG_KEY,
            Regions.HAUNTED_MANSION,
            Items.BIG_KEY,
            rule=Has(Items.LARGE_KEY_PANEL_1)
            & Has(Items.LARGE_KEY_PANEL_2)
            & Has(Items.LARGE_KEY_PANEL_3)
            & Has(Items.LARGE_KEY_PANEL_4)
            & Has(Items.LARGE_KEY_PANEL_5),
        ),
        # Baccus Lake
        ItemLocData(
            Locations.PIPE,
            Regions.BACCUS_LAKE,
            Items.PIPE,
        ),
        # Phoenix's Nest
        ItemLocData(
            "Green Jewel", Regions.PHOENIXS_NEST, Items.JEWEL_OF_WIND, rule=HasCleared(Events.THE_PHOENIXS_FAVORITE)
        ),
        # Masakari Jungle
        ChestLocData(
            Locations.VITALITY_INCREASE,
            Regions.MASAKARI_JUNGLE,
            Items.MAX_VITALITY_1,
            Sections.MASAKARI_JUNGLE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE3E, 0x02),
        ),
        ChestLocData(
            "Get the Drum",
            Regions.MASAKARI_JUNGLE,
            Items.FUNGA_DRUM,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BE3D, 0x80),
        ),
        *[
            ItemLocData(
                f"Leaf Butterfly {index}", Regions.MASAKARI_JUNGLE, Items.LEAF_BUTTERFLY, Sections.MASAKARI_JUNGLE
            )
            for index in range(1, 5)
        ],
        ItemLocData("Bananas", Regions.MASAKARI_JUNGLE, Items.BANANAS, Section(0x0A, 0x00)),
        ItemLocData(
            "Coconut Tree",
            Regions.MASAKARI_JUNGLE,
            Items.BOMB,
            rule=HasStarted(Events.I_NEED_A_BOMB),
            event=Events.I_NEED_A_BOMB,
        ),
        ChestLocData(
            Locations.MASAKARI_JUNGLE_PANTS,
            Regions.MASAKARI_JUNGLE,
            Items.FLASH_PANTS,
            Sections.MASAKARI_JUNGLE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE3E, 0x01),
        ),
        ChestLocData(
            "100 Year Old Chest",
            Regions.MASAKARI_JUNGLE,
            Items.LARGE_LUNCH_BOX,
            Section(0x0A, 0x00),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY)
            & (
                Rules.CAN_GRAPPLE
                | Has(Items.FUNKY_PARASOL)
                | Has(Items.JEWEL_OF_WIND)
                | Rules.HAS_ANY_FISH
                | Rules.HAS_BLUE_POWDER
                | (
                    HasCleared(Events.A_HUNGRY_MONKEY) & Has(Items.FLASH_PANTS)
                    | Has(Items.JEWEL_OF_FIRE)
                    | Has(Items.JEWEL_OF_WATER)
                )
            ),
            at=Bitmask(0x09BE3E, 0x04),
        ),
        ItemLocData("Drown a Second Time", Regions.MASAKARI_JUNGLE, Items.MINERS_HAT),
        # Old Tree Hill
        ChestLocData(
            "Million Year Old AP Crystal",
            Regions.OLD_TREE_HILL,
            Items.AP_CRYSTAL,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE3E, 0x08),
        ),
        ItemLocData("Old Tree", Regions.OLD_TREE_HILL, Items.KNOWLEDGE_FRUIT),
        ChestLocData(
            "Navy Evil Pig Bag",
            Regions.OLD_TREE_HILL,
            Items.NAVY_EVIL_PIG_BAG,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE3E, 0x10),
        ),
        # Clock Tower
        ItemLocData(Locations.MIXER, Regions.CLOCK_TOWER, Items.BANANA_JUICE, rule=Has(Items.BANANAS)),
        # Lumberjack Factory
        ItemLocData("Bassement", Regions.LUMBERJACK_FACTORY, Items.CHARITY_WINGS, Section(0x0B, 0x02)),
        ItemLocData(
            Locations.BUILD_A_RAFT, Regions.LUMBERJACK_FACTORY, Items.RAFT, rule=HasStarted(Events.LETS_RIDE_THE_RAFT)
        ),
        ItemLocData(
            "Fuel Bar",
            Regions.LUMBERJACK_FACTORY,
            Items.FUEL_BAR,
            rule=Has(Items.WINE) & HasStarted(Events.FOOD_FOR_FUEL),
        ),
        # Iron Castle
        ItemLocData("Need Power", Regions.IRON_CASTLE, Items.KEY_TO_OL_POND, rule=Has(Items.BOMB)),
        # Hidden Village
        ItemLocData(Locations.FIND_MY_SON, Regions.HIDDEN_VILLAGE, Items.YANS_LUNCH_BOX, event=Events.TAKE_OUT),
        ItemLocData(
            "Golden Butterfly", Regions.HIDDEN_VILLAGE, Items.GOLDEN_LEAF_BUTTERFLY, rule=Has(Items.LEAF_BUTTERFLY, 29)
        ),
        ItemLocData(
            "Hungry but not for Cheese 1",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Sections.HIDDEN_VILLAGE,
            rule=Has(Items.LUNCH_BOX) | Has(Items.LARGE_LUNCH_BOX),
            event=Events.IM_SO_HUNGRY,
        ),
        ItemLocData(
            "Hungry but not for Cheese 2",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Sections.HIDDEN_VILLAGE,
            rule=Has(Items.LUNCH_BOX) | Has(Items.LARGE_LUNCH_BOX),
            event=Events.IM_SO_HUNGRY,
        ),
        # Trick Village
        ChestLocData(
            "10,000 Year Old AP Crystal",
            Regions.TRICK_VILLAGE,
            Items.AP_CRYSTAL,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE41, 0x10),
        ),
        ChestLocData(
            Locations.VITALITY_INCREASE,
            Regions.TRICK_VILLAGE,
            Items.MAX_VITALITY_1,
            Sections.TRICK_VILLAGE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY)
            & (HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE)),
            at=Bitmask(0x09BE41, 0x20),
        ),
        ChestLocData(
            "1Up 1",
            Regions.TRICK_VILLAGE,
            Items.ONE_UP,
            Sections.TRICK_VILLAGE,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE42, 0x02),
        ),
        ChestLocData(
            "1Up 2",
            Regions.TRICK_VILLAGE,
            Items.ONE_UP,
            Sections.TRICK_VILLAGE,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BE42, 0x02),
        ),
        ItemLocData(
            "On Top of Water",
            Regions.TRICK_VILLAGE,
            Items.SEASHELL_NECKLACE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE42, 0x08),
        ),
        ChestLocData(
            "Left 1,000 Wing",
            Regions.TRICK_VILLAGE,
            Items.CHARITY_WINGS,
            Sections.TRICK_VILLAGE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
            & (HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE)),
            at=Bitmask(0x09BE41, 0x40),
        ),
        ChestLocData(
            "Right 1,000 Wing",
            Regions.TRICK_VILLAGE,
            Items.CHARITY_WINGS,
            Sections.TRICK_VILLAGE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
            & (HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE)),
            at=Bitmask(0x09BE41, 0x80),
        ),
        ChestLocData(
            "Rock Bottom",
            Regions.TRICK_VILLAGE,
            Items.LARGE_LUNCH_BOX,
            Sections.TRICK_VILLAGE,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BE42, 0x01),
        ),
        ChestLocData(
            "Yellow Pig Bag",
            Regions.TRICK_VILLAGE,
            Items.YELLOW_EVIL_PIG_BAG,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY)
            & (HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE)),
            at=Bitmask(0x09BE42, 0x04),
        ),
        ItemLocData("Math Bead 1", Regions.TRICK_VILLAGE, Items.MATH_BEAD_1, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData(
            "Math Bead 2",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_2,
            rule=HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE),
        ),
        ItemLocData("Math Bead 3", Regions.TRICK_VILLAGE, Items.MATH_BEAD_3, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData(
            "Math Bead 4",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_4,
            rule=HasCleared(Events.WHATS_UNDERWATER) | (HasCleared(Events.TRICK_VILLAGE) & Rules.CAN_SWIM),
        ),
        ItemLocData(
            "Math Bead 5",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_5,
            rule=HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE),
        ),
        ItemLocData(
            "Math Bead 6",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_6,
            rule=HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE),
        ),
        ItemLocData("Math Bead 7", Regions.TRICK_VILLAGE, Items.MATH_BEAD_7, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData(
            "Math Bead 8",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_8,
            rule=HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE),
        ),
        ItemLocData(
            "Math Bead 9",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_9,
            rule=HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE),
        ),
        ItemLocData(
            "Math Bead 10",
            Regions.TRICK_VILLAGE,
            Items.MATH_BEAD_10,
            rule=HasCleared(Events.WHATS_UNDERWATER) | HasCleared(Events.TRICK_VILLAGE),
        ),
        ItemLocData(
            "Blue Jewel", Regions.TRICK_VILLAGE, Items.JEWEL_OF_WATER, rule=HasCleared(Events.WHATS_UNDERWATER)
        ),
        ItemLocData(
            "Collect the Beads Key",
            Regions.TRICK_VILLAGE,
            Items.TEN_THOUSAND_YEAR_OLD_KEY,
            rule=Has(Items.MATH_BEAD_1)
            & Has(Items.MATH_BEAD_2)
            & Has(Items.MATH_BEAD_3)
            & Has(Items.MATH_BEAD_4)
            & Has(Items.MATH_BEAD_5)
            & Has(Items.MATH_BEAD_6)
            & Has(Items.MATH_BEAD_7)
            & Has(Items.MATH_BEAD_8)
            & Has(Items.MATH_BEAD_9)
            & Has(Items.MATH_BEAD_10),
        ),
        ItemLocData(
            "Collect the Beads Wire",
            Regions.TRICK_VILLAGE,
            Items.THIEFS_WIRE,
            rule=Has(Items.MATH_BEAD_1)
            & Has(Items.MATH_BEAD_2)
            & Has(Items.MATH_BEAD_3)
            & Has(Items.MATH_BEAD_4)
            & Has(Items.MATH_BEAD_5)
            & Has(Items.MATH_BEAD_6)
            & Has(Items.MATH_BEAD_7)
            & Has(Items.MATH_BEAD_8)
            & Has(Items.MATH_BEAD_9)
            & Has(Items.MATH_BEAD_10),
        ),
        ItemLocData(
            "5 Golden Items",
            Regions.TRICK_VILLAGE,
            Items.PSYCHIC_FISH,
            rule=HasCleared(Events.THE_10_MATH_BEADS)
            & Has(Items.GOLD_CANDY)
            & Has(Items.GOLD_FLOWER)
            & Has(Items.GOLD_MEDAL)
            & Has(Items.GOLDEN_LEAF_BUTTERFLY)
            & Has(Items.GOLDEN_FRUIT),
        ),
        # Underground Maze Entrance
        ChestLocData(
            "100 Year Old Cheese",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x20),
        ),
        ChestLocData(
            "Needlegator Teeth",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.NEEDLEGATOR_TEETH,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x40),
        ),
        ChestLocData(
            "Medicine",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.COLD_MEDICINE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x80),
        ),
        ChestLocData(
            "10,000 Year Old Cheese",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x02),
        ),
        ChestLocData(
            "Million Year Old AP Crystal",
            Regions.UNDERGROUND_MAZE,
            Items.AP_CRYSTAL,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x01),
        ),
        # Underground Maze
        # # TODO: Find where this is called in game (reverse)
        # ItemLocData(
        #   Locations.VITALITY_INCREASE,
        #   Regions.UNDERGROUND_MAZE,
        #   Items.MAX_VITALITY_1,
        #   Sections.UNDERGROUND_MAZE,
        #   rule=Has(Locations.AP_500_000)
        # ),
        ChestLocData(
            "100 Year Old Cheese 1",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x04),
        ),
        ChestLocData(
            "100 Year Old Cheese 2",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x04),
        ),
        ChestLocData(
            "1,000 Year Old Lunch",
            Regions.UNDERGROUND_MAZE,
            Items.LUNCH_BOX,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x08),
        ),
        ChestLocData(
            "10,000 Year Old Claw",
            Regions.UNDERGROUND_MAZE,
            Items.KOKKA_CLAW,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3D, 0x10),
        ),
        ChestLocData(
            "Butamashi Thorn",
            Regions.UNDERGROUND_MAZE,
            Items.BUTAMUSHI_THORN,
            Sections.UNDERGROUND_MAZE,
            rule=HasCleared(Events.SOURCE_OF_EVIL_MAGIC) & Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x04),
        ),
        ChestLocData(
            "100 Year Old Wing 1",
            Regions.UNDERGROUND_MAZE,
            Items.CHARITY_WINGS,
            Sections.UNDERGROUND_MAZE,
            rule=HasCleared(Events.SOURCE_OF_EVIL_MAGIC) & Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x80),
        ),
        ChestLocData(
            "100 Year Old Wing 2",
            Regions.UNDERGROUND_MAZE,
            Items.CHARITY_WINGS,
            Sections.UNDERGROUND_MAZE,
            rule=HasCleared(Events.SOURCE_OF_EVIL_MAGIC) & Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x80),
        ),
        ChestLocData(
            "1,000 Year Old Cheese 1",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x40),
        ),
        ChestLocData(
            "1,000 Year Old Cheese 2",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x40),
        ),
        ChestLocData(
            "10,000 Year Old Wing 1",
            Regions.UNDERGROUND_MAZE,
            Items.CHARITY_WINGS,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x20),
        ),
        ChestLocData(
            "10,000 Year Old Wing 2",
            Regions.UNDERGROUND_MAZE,
            Items.CHARITY_WINGS,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x20),
        ),
        ChestLocData(
            "100 Year Old Lunch",
            Regions.UNDERGROUND_MAZE,
            Items.LUNCH_BOX,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x08),
        ),
        ChestLocData(
            "Biting Plant Flower",
            Regions.UNDERGROUND_MAZE,
            Items.BITING_PLANT_FLOWER,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x10),
        ),
        ChestLocData(
            "Near the Small Strange Room 1",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Sections.UNDERGROUND_MAZE,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD3C, 0x02),
        ),
        ItemLocData("Million Year Old Key", Regions.MILLION_YEAR_OLD_MANS_ROOM, Items.MILLION_YEAR_OLD_KEY),
        # The Mermaid's Singing Rock
        # TODO: Find where this is called in game (reverse)
        # Not yet working. This Max Vit+1 is given by the Mermaid after getting the Bronze Medal which clears the event I Want a Bronze Medal
        # ItemLocData(
        # Locations.VITALITY_INCREASE,
        # Regions.THE_MERMAIDS_SINGING_ROCK,
        # Items.MAX_VITALITY_1,
        # Section(0x06, 0x02),
        # rule=HasCleared(Events.I_WANT_A_BRONZE_MEDAL),
        # ),
        ItemLocData(
            Locations.BRONZE_MEDAL,
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.BRONZE_MEDAL,
            event=Events.I_WANT_A_BRONZE_MEDAL,
        ),
        ItemLocData(
            "Silver Medal", Regions.THE_MERMAIDS_SINGING_ROCK, Items.SILVER_MEDAL, event=Events.I_WANT_A_SILVER_MEDAL
        ),
        ItemLocData(
            "Gold Medal", Regions.THE_MERMAIDS_SINGING_ROCK, Items.GOLD_MEDAL, event=Events.I_WANT_A_GOLD_MEDAL
        ),
        ItemLocData(
            "Flying Wing Leftmost",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Sections.MOTOCROSS,
            at=Bitmask(0x09BDBD, 0x10),
        ),
        ItemLocData(
            "Flying Wing Rightmost",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Sections.MOTOCROSS,
            at=Bitmask(0x09BDBD, 0x40),
        ),
        ItemLocData(
            "In the House",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Sections.MOTOCROSS,
            at=Bitmask(0x09BDBD, 0x02),
        ),
        ItemLocData(
            "In the back House",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Sections.MOTOCROSS,
            at=Bitmask(0x09BDBE, 0x01),
        ),
        ItemLocData(
            "Lunch Box",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.LUNCH_BOX,
            Sections.MOTOCROSS,
            at=Bitmask(0x09BDBC, 0x20),
        ),
        ItemLocData(
            "Take Out 1",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Sections.HIDDEN_VILLAGE,
            rule=Has(Items.YANS_LUNCH_BOX) & HasStarted(Events.TAKE_OUT),
            event=Events.TAKE_OUT,
        ),
        ItemLocData(
            "Take Out 2",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Sections.HIDDEN_VILLAGE,
            rule=Has(Items.YANS_LUNCH_BOX) & HasStarted(Events.TAKE_OUT),
            event=Events.TAKE_OUT,
        ),
    ]

    for event in EventHandler.event_table:
        location_table.append(LocationData(Cleared(event.name), event.region, rule=event.cleared_rule))

    by_id: dict[int, LocationData] = {}
    by_name: dict[str, LocationData] = {}
    by_region = defaultdict(list)
    by_item_id: dict[int, list[int]] = defaultdict(list)
    by_event: dict[str, list[int]] = defaultdict(list)
    name_to_id: dict[str, int] = {}
    with_bitmask: list[LocationData] = []

    for location in location_table:
        by_id[location.id] = location
        by_name[location.name] = location
        by_region[location.region].append(location)

        if isinstance(location, ItemLocData) and location.event is not None:
            by_event[location.event].append(location.id)

        if location.item is not None:
            by_item_id[location.item.id].append(location.id)

        name_to_id[location.name] = location.id

        if location.at is not None:
            with_bitmask.append(location)

    @staticmethod
    def filter_and_sort(item: ItemData, section: Section) -> list[ItemLocData]:
        item_ids: list[int] = [item.id]
        if item.is_pants():
            item_ids: list[int] = [ItemHandler.by_name[item_name].id for item_name in PANTS]

        filtered_locations = LocationHandler.filter(LocationHandler.location_table, item_ids, section)

        return filtered_locations

    @staticmethod
    def filter(
        locations: list[LocationData] | list[ItemLocData], item_ids: list[int], section: Section
    ) -> list[ItemLocData]:
        return [
            location
            for location in locations
            if isinstance(location, ItemLocData)
            and location.item is not None
            and location.item.id in item_ids
            and (location.section is None or location.section.equals(section))
        ]


class TombaLocation(Location):
    game = constants.GAME


def create_all_locations(world: TombaWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def create_regular_locations(world: TombaWorld) -> None:
    for name, locations in LocationHandler.by_region.items():
        # Settings: Remove cleared event from locations
        if not world.options.cleared_event_rewards:
            locations = [location for location in locations if isinstance(location, ItemLocData)]

        # Settings: Remove bonus chests from locations
        if not world.options.bonus_chests_randomized:
            locations = [location for location in locations if not location.is_bonus() or not location.is_chest()]

        region = world.get_region(name)
        region.add_locations({location.name: location.id for location in locations}, TombaLocation)

    if not world.options.furious_tornado_randomized:
        # Force furious tornado to be on Mailbox
        MAILBOX = world.get_location(get_name(Locations.MAILBOX, Regions.VILLAGE_OF_ALL_BEGINNINGS))
        MAILBOX.place_locked_item(ItemHandler.create_item(world, Items.FURIOUS_TORNADO))

    if not world.options.chick_randomized:
        CHICK_1 = world.get_location(get_name(Locations.KOKKA_EGG_1, Regions.VILLAGE_OF_ALL_BEGINNINGS))
        CHICK_1.place_locked_item(ItemHandler.create_item(world, Items.CHICK))

        CHICK_2 = world.get_location(get_name(Locations.KOKKA_EGG_2, Regions.FOREST_OF_ALL_BEGINNINGS))
        CHICK_2.place_locked_item(ItemHandler.create_item(world, Items.CHICK))

        CHICK_3 = world.get_location(get_name(Locations.KOKKA_EGG_3, Regions.FOREST_OF_ALL_BEGINNINGS))
        CHICK_3.place_locked_item(ItemHandler.create_item(world, Items.CHICK))

        CHICK_4 = world.get_location(get_name(Locations.KOKKA_EGG_4, Regions.FOREST_OF_ALL_BEGINNINGS))
        CHICK_4.place_locked_item(ItemHandler.create_item(world, Items.CHICK))

    # Force baron to be on the original location
    BARON = world.get_location(get_name(Locations.BARON, Regions.DWARF_VILLAGE))
    BARON.place_locked_item(ItemHandler.create_item(world, Items.BARON))

    if not world.options.optional_randomized:
        # Force Pipe
        PIPE = world.get_location(get_name(Locations.PIPE, Regions.BACCUS_LAKE))
        PIPE.place_locked_item(ItemHandler.create_item(world, Items.PIPE))

        # Force Broken Vase
        JAIL = world.get_location(get_name(Locations.JAIL, Regions.DWARF_VILLAGE))
        JAIL.place_locked_item(ItemHandler.create_item(world, Items.BROKEN_VASE))


def create_events(world: TombaWorld) -> None:
    """Those event are considered cleared once the logic reach the specific region they are in"""
    for event in EventHandler.event_table:
        region = world.get_region(event.region)
        region.add_event(Started(event.name), location_type=TombaLocation, item_type=TombaItem)

        # Adds cleared as events instead of locations
        if not world.options.cleared_event_rewards:
            region.add_event(Cleared(event.name), location_type=TombaLocation, item_type=TombaItem)

    VILLAGE_OF_ALL_BEGINNINGS = world.get_region(Regions.VILLAGE_OF_ALL_BEGINNINGS)
    VILLAGE_OF_ALL_BEGINNINGS.add_event(Locations.AP_150_000, location_type=TombaLocation, item_type=TombaItem)

    # Blue Fortune Teller gives a vitality increase in that case
    # UNDERGROUND_MAZE = world.get_region(Regions.UNDERGROUND_MAZE)
    # UNDERGROUND_MAZE.add_event(Locations.AP_500_000, location_type=TombaLocation, item_type=TombaItem)
