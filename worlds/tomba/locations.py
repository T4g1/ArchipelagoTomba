from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from collections import defaultdict
from dataclasses import dataclass
from BaseClasses import Location, LocationProgressType
from rule_builder.rules import Has, Rule

from . import constants
from .constants import Regions, Items, Locations, Events
from .items import ItemHandler, ItemData, TombaItem
from .sections import Section, Sections
from .helpers import HasStarted, HasCleared, Started, Cleared, Rules
from .events import EventHandler
from .bitutils import Bitmask

if TYPE_CHECKING:
    from .world import TombaWorld

MAX_DISTANCE_THRESHOLD = 500000


def get_name(name: str, region: str):
    return f"{name} ({region})"


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

    def __init__(
        self,
        name: str,
        region: str,
        item: ItemData | None = None,
        section: Section | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
        at: Bitmask | None = None,
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

    def with_section(self, section: Section) -> Self:
        self.section = section
        return self

    def __repr__(self) -> str:
        return self.name


@dataclass
class ItemLocData(LocationData):
    x: int | None
    y: int | None
    related_event: str

    def __init__(
        self,
        name: str,
        region: str,
        item_name: str,
        section: Section | None = None,
        x: int | None = None,
        y: int | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
        at: Bitmask | None = None,
        event: str | None = None,
    ):
        name = get_name(name, region)

        item = ItemHandler.by_name.get(item_name, None)
        if item is None:
            raise Exception(f"Trying to create a location {name} with an unknown item: {item_name}")

        super().__init__(name, region, item, section, progress_type, rule, at)

        self.x = x
        self.y = y

        self.event = event

    def with_coordinates(self, x: int, y: int) -> Self:
        self.x = x
        self.y = y
        return self

    def get_distance(self, camera_horizontal: int, camera_vertical: int) -> float:
        # A location with no coordinate is prioritized
        if self.x is None or self.y is None:
            return 0

        distance = (self.x - camera_horizontal) ** 2 + (self.y - camera_vertical) ** 2
        return distance


class LocationHandler:
    # Special case: Those can happens in any of the locations Yan is in
    take_out_event_locations: list[ItemLocData] = [
        ItemLocData(
            "Take Out 1",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Section(0xFF, 0xFF),
            rule=Has(Items.YANS_LUNCH_BOX) & HasStarted(Events.TAKE_OUT),
            event=Events.TAKE_OUT,
        ),
        ItemLocData(
            "Take Out 2",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Section(0xFF, 0xFF),
            rule=Has(Items.YANS_LUNCH_BOX) & HasStarted(Events.TAKE_OUT),
            event=Events.TAKE_OUT,
        ),
    ]

    location_table: list[LocationData] = [
        # Village of all Beginnings
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
            rule=HasStarted(Events.THE_CUTE_WITCH) & Has(Items.GRAPPLE) & Has(Items.GRAPPLEJACK),
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
            at=Bitmask(0x09BCEC, 0x01, on_checked=True, target_value=True),
        ),
        ItemLocData("Peach Flower Gas", Regions.VILLAGE_OF_ALL_BEGINNINGS, Items.BABY_PIG),
        ItemLocData(
            "Kokka Egg in the Village",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.VILLAGE_OF_ALL_BEGINNING,
        ),
        ItemLocData(
            "100 Year Chest in the Tree",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.HUNDRED_YEAR_OLD_BELL,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        # Forest of all Beginnings
        ItemLocData(
            "Biting Plant",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.BITING_PLANT_FLOWER,
            Section(0x00, 0x01),
            at=Bitmask(0x09BD00, 0x20),
        ),
        ItemLocData(
            "10,000 Year Chest",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.LUNCH_BOX,
            Section(0x00, 0x01),
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        # The two following ones cannot be deterministicaly identified
        ItemLocData(
            "Kokka Egg after the Fog 1",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.FOREST_OF_ALL_BEGINNING_PART_1,
        ),
        ItemLocData(
            "Kokka Egg after the Fog 2", Regions.FOREST_OF_ALL_BEGINNINGS, Items.CHICK, x=2560, y=65010
        ),  # This one can be grabbed in Forest of All Beginnings part 1 or part 2 depending on the player movements
        ItemLocData(
            "Kokka Egg near the Top",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHICK,
            Sections.FOREST_OF_ALL_BEGINNING_PART_2,
            3000,
            64415,
        ),
        ItemLocData(
            "100 Year Chest near the Hut",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHARITY_WINGS,
            Section(0x00, 0x02),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Old Reward",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.HUNDRED_YEAR_OLD_KEY,
            rule=Has(Items.CHICK, 4),
        ),
        # Ol' Pond
        ItemLocData("Drown", Regions.OL_POND, Items.BANANAS, Section(0x00, 0x05)),
        ItemLocData("AP Box", Regions.OL_POND, Items.CHEESE, Section(0x00, 0x05)),
        ItemLocData(
            "10,000 Year Old Chest",
            Regions.OL_POND,
            Items.TEN_THOUSAND_YEAR_OLD_BELL,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY) & Rules.CAN_SWIM,
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
        ItemLocData("Campfire", Regions.FOREST_OF_100_FLOWERS, Items.BAKED_YAM, rule=Has(Items.BUCKET_OF_WATER)),
        ItemLocData(
            Locations.HIDDEN_CHEST_FOREST_100_FLOWER_1,
            Regions.FOREST_OF_100_FLOWERS,
            Items.CHARITY_WINGS,
            Sections.FOREST_OF_100_FLOWERS,
            x=1427,
            y=65345,
        ),
        ItemLocData(
            Locations.HIDDEN_CHEST_FOREST_100_FLOWER_2,
            Regions.FOREST_OF_100_FLOWERS,
            Items.CHARITY_WINGS,
            Sections.FOREST_OF_100_FLOWERS,
            x=1427,
            y=65345,
        ),
        ItemLocData(
            "On Top of the Spikes",
            Regions.FOREST_OF_100_FLOWERS,
            Items.WOOD_BOOMERANG,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        # Watch Tower
        ItemLocData("Top of Watch Tower", Regions.WATCH_TOWER, Items.TELESCOPE),
        ItemLocData("Push the Boulder", Regions.WATCH_TOWER, Items.DIRTY_MIRROR),
        ItemLocData("Under the Boulder", Regions.WATCH_TOWER, Items.FLOWER_SEEDS, rule=HasCleared(Events.A_LOST_CHILD)),
        ItemLocData("100 Year Chest", Regions.WATCH_TOWER, Items.JUMPING_PANTS, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)),
        ItemLocData(
            "10,000 Year Chest",
            Regions.WATCH_TOWER,
            Items.LARGE_LUNCH_BOX,
            Section(0x01, 0x03),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Million Year Chest", Regions.WATCH_TOWER, Items.MILLION_YEAR_OLD_BELL, rule=Has(Items.MILLION_YEAR_OLD_KEY)
        ),
        ItemLocData("Fill the Bucket", Regions.WATCH_TOWER, Items.BUCKET_OF_WATER, rule=Has(Items.BUCKET)),
        ItemLocData(
            "Win the Race", Regions.WATCH_TOWER, Items.SILVER_POWDER, rule=HasCleared(Events.THE_WORLDS_GREATEST_POUT)
        ),
        # Wobbly Wharf
        ItemLocData("On top of the Pole", Regions.WOBBLY_WHARF, Items.BUCKET, rule=Rules.CAN_BIG_JUMP),
        # Dwarf Village
        ItemLocData(
            Locations.BARON,
            Regions.DWARF_VILLAGE,
            Items.BARON,
            rule=Has(Items.SEAWEED) & HasCleared(Events.DELICIOUS_KNOWLEDGE_FRUIT),
        ),
        ItemLocData("Rescue the Child", Regions.DWARF_VILLAGE, Items.CHEESE, Section(0x02, 0x00)),
        ItemLocData("Meet the Dwarf Elder", Regions.DWARF_VILLAGE, Items.BLUE_EVIL_PIG_BAG),
        ItemLocData("Plant a Garden", Regions.DWARF_VILLAGE, Items.GOLD_FLOWER, rule=HasCleared(Events.FLOWER_SEEDS)),
        ItemLocData(
            "1,000 Year Chest",
            Regions.DWARF_VILLAGE,
            Items.CHARITY_WINGS,
            Section(0x02, 0x00),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData("Fire Starter", Regions.DWARF_VILLAGE, Items.TORCH, rule=HasStarted(Events.WHERED_THE_LIGHTS_GO)),
        ItemLocData("Jail", Regions.DWARF_VILLAGE, Items.BROKEN_VASE, rule=Has(Items.TORCH)),
        # Mushroom Forest
        ItemLocData("AP Box", Regions.MUSHROOM_FOREST, Items.ORDINARY_MUSHROOM, rule=Has(Locations.AP_150_000)),
        ItemLocData("Tear Jar", Regions.MUSHROOM_FOREST, Items.TEAR_JAR, rule=HasCleared(Events.THE_100_FLOWER_FOREST)),
        ItemLocData(
            "1,000 Year Chest 1",
            Regions.MUSHROOM_FOREST,
            Items.MYSTERIOUS_MUSHROOM,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Chest 2",
            Regions.MUSHROOM_FOREST,
            Items.THOUSAND_YEAR_OLD_BELL,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Chest near the Stairs",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Section(0x09, 0x00),
            x=1523,
            y=64863,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),  # at=Bitmask(0x09BE1F, 0x10)
        ItemLocData(
            "1,000 Year Chest in the Pit",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Section(0x09, 0x00),
            x=2745,
            y=64938,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),  # at=Bitmask(0x09BE1F, 0x10)
        ItemLocData(
            "10,000 Year Chest",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Section(0x09, 0x00),
            x=2433,
            y=64867,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),  # at=Bitmask(0x09BE1F, 0x04)
        ItemLocData(
            "Chest near the Spikes",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            Section(0x09, 0x00),
            x=3941,
            y=64847,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(Locations.MONSTER_HUNT, Regions.MUSHROOM_FOREST, Items.RISE_AND_SHINE_POWDER),
        # Charity Square
        ItemLocData("Sacred Fish", Regions.CHARITY_SQUARE, Items.SACRED_FISH, rule=HasCleared(Events.THE_FLOWER_TOWER)),
        ItemLocData("Crystal Balls", Regions.CHARITY_SQUARE, Items.THREE_CRYSTAL_BALLS, rule=Rules.CAN_BIG_JUMP),
        ItemLocData(
            "Charity Entrance Left", Regions.CHARITY_SQUARE, Items.CHARITY_WINGS, Section(0x01, 0x04), x=2900, y=65005
        ),
        ItemLocData(
            "Charity Entrance Right", Regions.CHARITY_SQUARE, Items.CHARITY_WINGS, Section(0x01, 0x04), x=2930, y=65005
        ),
        # Mansion
        ItemLocData("Familiar Beach", Regions.MANSION, Items.SEAWEED, rule=HasStarted(Events.SEAWEED_FOR_YOUR_HEALTH)),
        # Stormy Mountain
        ItemLocData(
            "100 Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.LUNCH_BOX,
            Section(0x03, 0x00),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.LARGE_LUNCH_BOX,
            Section(0x03, 0x00),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Million Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.IRON_BOOMERANG,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
        ),
        ItemLocData("Smile Wing", Regions.STORMY_MOUNTAIN, Items.CHARITY_WINGS, Section(0x03, 0x01), x=3150, y=63708),
        ItemLocData("Funga", Regions.STORMY_MOUNTAIN, Items.MOLASSES, rule=Has(Items.FUNGA_DRUM)),
        ItemLocData(
            "Dig",
            Regions.STORMY_MOUNTAIN,
            Items.CHEESE,
            Section(0x03, 0x01),
            rule=HasCleared(Events.PHOENIX_MOUNTAIN),
            x=3194,
            y=63937,
        ),
        ItemLocData(
            "When the Wind Dies Down",
            Regions.STORMY_MOUNTAIN,
            Items.LARGE_LUNCH_BOX,
            Section(0x03, 0x01),
            rule=HasCleared(Events.PHOENIX_MOUNTAIN),
        ),
        ItemLocData("Big Keyhole", Regions.STORMY_MOUNTAIN, Items.RED_EVIL_PIG_BAG, rule=Has(Items.BIG_KEY)),
        ItemLocData("Herbs", Regions.STORMY_MOUNTAIN, Items.HEALING_HERBS),
        ItemLocData("Give back the Pants", Regions.STORMY_MOUNTAIN, Items.FUNKY_PARASOL, rule=Has(Items.CHARLES_PANTS)),
        ItemLocData(
            "100 Year Old Pants", Regions.STORMY_MOUNTAIN, Items.DASHING_PANTS, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)
        ),
        ItemLocData(
            "100 Year Old Chest Wing 1",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            Section(0x03, 0x01),
            x=5086,
            y=62932,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD5D, 0x20),
        ),
        ItemLocData(
            "100 Year Old Chest Wing 2",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            Section(0x03, 0x01),
            x=5086,
            y=62932,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD5D, 0x20),
        ),
        ItemLocData(
            "1,000 Year Old Grapple", Regions.STORMY_MOUNTAIN, Items.GRAPPLE, rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
        ),
        # Lava Caves
        ItemLocData("Charle's Pant", Regions.LAVA_CAVES, Items.CHARLES_PANTS),
        ItemLocData(
            "Green Evil Pig Bag Chest",
            Regions.LAVA_CAVES,
            Items.GREEN_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Bunk Flower 1", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=487, y=64860
        ),
        ItemLocData(
            "Bunk Flower 2", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=1049, y=64768
        ),
        ItemLocData(
            "Bunk Flower 3", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=1168, y=64785
        ),
        ItemLocData(
            "Bunk Flower 4", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=1793, y=64505
        ),
        ItemLocData(
            "Bunk Flower 5", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=2074, y=64517
        ),
        ItemLocData(
            "Bunk Flower 6", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=2047, y=64776
        ),
        ItemLocData(
            "Bunk Flower 7", Regions.LAVA_CAVES_PURIFIED, Items.BUNK_FLOWER, Sections.LAVA_CAVES, x=2409, y=64400
        ),
        ItemLocData("Leave Hidden Village", Regions.LAVA_CAVES_PURIFIED, Items.WHAT_THE_THIEF_LOST),
        ItemLocData(
            "In Lava Caves Alcove",
            Regions.LAVA_CAVES_PURIFIED,
            Items.WHAT_THE_THIEF_FORGOT,
            rule=HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ItemLocData(
            "10,000 Year Charity Wing 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            x=1539,
            y=64701,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x10),
        ),
        ItemLocData(
            "10,000 Year Charity Wing 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            x=1539,
            y=64701,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x10),
        ),
        ItemLocData(
            "1,000 Year Charity Wing 1",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            x=1570,
            y=64443,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x02),
        ),
        ItemLocData(
            "1,000 Year Charity Wing 2",
            Regions.LAVA_CAVES_PURIFIED,
            Items.CHARITY_WINGS,
            Sections.LAVA_CAVES,
            x=1570,
            y=64443,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
            at=Bitmask(0x09BD62, 0x02),
        ),
        ItemLocData(
            "Million Year Large Lunch",
            Regions.LAVA_CAVES_PURIFIED,
            Items.LARGE_LUNCH_BOX,
            Sections.LAVA_CAVES,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Lunch",
            Regions.LAVA_CAVES_PURIFIED,
            Items.LUNCH_BOX,
            Sections.LAVA_CAVES,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        # Baccus Village
        ItemLocData(
            "Some Cheese 1",
            Regions.BACCUS_VILLAGE,
            Items.LARGE_LUNCH_BOX,
            Section(0x05, 0x02),
            x=574,
            y=350,
            rule=Has(Items.CHEESE, 10),
        ),
        ItemLocData(
            "Some Cheese 2",
            Regions.BACCUS_VILLAGE,
            Items.LARGE_LUNCH_BOX,
            Section(0x05, 0x02),
            x=574,
            y=350,
            rule=Has(Items.CHEESE, 10),
        ),
        ItemLocData("More Cheese", Regions.BACCUS_VILLAGE, Items.GOLDEN_FRUIT, rule=Has(Items.CHEESE, 15)),
        ItemLocData("Grownups", Regions.BACCUS_VILLAGE, Items.WEED_KILLER, rule=HasCleared(Events.MONSTER_HUNT)),
        ItemLocData(
            "Give the Baby Pig",
            Regions.BACCUS_VILLAGE,
            Items.KOKKA_CLAW,
            Section(0x05, 0x00),
            rule=Has(Items.BABY_PIG) & HasCleared(Events.CANT_STOP_CRYING),
        ),
        ItemLocData(
            "Weed Killer",
            Regions.BACCUS_VILLAGE,
            Items.CHARITY_WINGS,
            Section(0x05, 0x00),
            rule=HasStarted(Events.DEATH_FRUIT_JUICE),
        ),
        # Central Park
        ItemLocData(
            "Central Park Chest",
            Regions.CENTRAL_PARK,
            Items.ORANGE_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
            & HasCleared(Events.WHERES_THE_BABY_MOUSE)
            & HasCleared(Events.A_DRINK_FOR_GROWNUPS),
        ),
        ItemLocData("Baccus Wine", Regions.CENTRAL_PARK, Items.WINE, rule=HasStarted(Events.FOOD_FOR_FUEL)),
        # Haunted Mansion
        ItemLocData(
            "Unbreakable Wire", Regions.HAUNTED_MANSION, Items.STRONG_WIRE, rule=HasStarted(Events.UNBREAKABLE_WIRE)
        ),
        ItemLocData(
            "100 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x0C),
            x=464,
            y=65416,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x20),
        ),
        ItemLocData(
            "100 Year Old Chest 2",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x0C),
            x=464,
            y=65416,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
            at=Bitmask(0x09BD7C, 0x20),
        ),
        ItemLocData(
            "What's Underwater ?",
            Regions.HAUNTED_MANSION,
            Items.MIGHTY_FISH_FOOD,
            rule=Has(Items.SEASHELL_NECKLACE) & HasCleared(Events.THE_10000_YEAR_OLD_MAN),
        ),
        ItemLocData(
            "1,000 Year Old Chest near Yan",
            Regions.HAUNTED_MANSION,
            Items.LUNCH_BOX,
            Section(0x04, 0x0C),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            Section(0x04, 0x06),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            Section(0x04, 0x10),
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Millions Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            Section(0x04, 0x04),
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            Locations.CRY_CHEESE_LEFT, Regions.HAUNTED_MANSION, Items.CHEESE, Sections.CRY_ROOM, x=160, y=65396
        ),
        ItemLocData(
            Locations.CRY_CHEESE_RIGHT, Regions.HAUNTED_MANSION, Items.CHEESE, Sections.CRY_ROOM, x=160, y=65396
        ),
        ItemLocData(
            "Pink Evil Bag",
            Regions.HAUNTED_MANSION,
            Items.PINK_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY) & Has(Items.BIG_KEY),
        ),
        ItemLocData(
            "Near the Magic Egg",
            Regions.HAUNTED_MANSION,
            Items.BOSS_JEWEL,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY) & Has(Items.SMALL_KEY) & HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ItemLocData("Save the Villager", Regions.HAUNTED_MANSION, Items.SMALL_KEY),
        ItemLocData("Near the Million Year Old Chest", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_1),
        ItemLocData("Near the Healing Fountain", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_2),
        ItemLocData("Near the Siren", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_3),
        ItemLocData("On the Elevator", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_4),
        ItemLocData("Near the Forest Ping Entrance", Regions.HAUNTED_MANSION, Items.LARGE_KEY_PANEL_5),
        ItemLocData("In the Chimney", Regions.HAUNTED_MANSION, Items.JEWEL_OF_FIRE),
        ItemLocData("Save the Old Man", Regions.HAUNTED_MANSION, Items.THOUSAND_YEAR_OLD_KEY),
        ItemLocData(
            "Thief in the Chimney 1",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x02),
            x=906,
            y=64428,
            rule=Has(Items.WHAT_THE_THIEF_FORGOT) & HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ItemLocData(
            "Thief in the Chimney 2",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            Section(0x04, 0x02),
            x=906,
            y=64428,
            rule=Has(Items.WHAT_THE_THIEF_FORGOT) & HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ItemLocData(
            "Stone Boomerang", Regions.HAUNTED_MANSION, Items.STONE_BOOMERANG, rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
        ),
        ItemLocData(
            "Painting of a Big Key",
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
            "Pipe",
            Regions.BACCUS_LAKE,
            Items.PIPE,
        ),
        # Phoenix's Nest
        ItemLocData(
            "Green Jewel", Regions.PHOENIXS_NEST, Items.JEWEL_OF_WIND, rule=HasCleared(Events.THE_PHOENIXS_FAVORITE)
        ),
        # Masakari Jungle
        ItemLocData("Get the Drum", Regions.MASAKARI_JUNGLE, Items.FUNGA_DRUM, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)),
        *[
            ItemLocData(
                f"Leaf Butterfly {index}", Regions.MASAKARI_JUNGLE, Items.LEAF_BUTTERFLY, Sections.MASAKARI_JUNGLE
            )
            for index in range(1, 5)
        ],
        ItemLocData("Bananas", Regions.MASAKARI_JUNGLE, Items.BANANAS, Section(0x0A, 0x00)),
        ItemLocData("Coconut Tree", Regions.MASAKARI_JUNGLE, Items.BOMB, rule=HasStarted(Events.I_NEED_A_BOMB)),
        ItemLocData("New Pants", Regions.MASAKARI_JUNGLE, Items.FLASH_PANTS, rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY)),
        ItemLocData(
            "100 Year Old Chest",
            Regions.MASAKARI_JUNGLE,
            Items.LARGE_LUNCH_BOX,
            Section(0x0A, 0x00),
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("Drown a Second Time", Regions.MASAKARI_JUNGLE, Items.MINERS_HAT),
        # Old Tree Hill
        ItemLocData("Old Tree", Regions.OLD_TREE_HILL, Items.KNOWLEDGE_FRUIT),
        ItemLocData(
            "Navy Evil Pig Bag",
            Regions.OLD_TREE_HILL,
            Items.NAVY_EVIL_PIG_BAG,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        # Clock Tower
        ItemLocData("Mixer", Regions.CLOCK_TOWER, Items.BANANA_JUICE, rule=Has(Items.BANANAS)),
        # Lumberjack Factory
        ItemLocData("Bassement", Regions.LUMBERJACK_FACTORY, Items.CHARITY_WINGS, Section(0x0B, 0x02)),
        ItemLocData("Build a Raft", Regions.LUMBERJACK_FACTORY, Items.RAFT, rule=HasStarted(Events.LETS_RIDE_THE_RAFT)),
        ItemLocData(
            "Fuel Bar",
            Regions.LUMBERJACK_FACTORY,
            Items.FUEL_BAR,
            rule=Has(Items.WINE) & HasStarted(Events.FOOD_FOR_FUEL),
        ),
        # Iron Castle
        ItemLocData("Need Power", Regions.IRON_CASTLE, Items.KEY_TO_OL_POND, rule=Has(Items.BOMB)),
        # Hidden Village
        ItemLocData("Find my Son", Regions.HIDDEN_VILLAGE, Items.YANS_LUNCH_BOX),
        ItemLocData(
            "Golden Butterfly", Regions.HIDDEN_VILLAGE, Items.GOLDEN_LEAF_BUTTERFLY, rule=Has(Items.LEAF_BUTTERFLY, 29)
        ),
        ItemLocData(
            "Hungry but not for Cheese 1",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Section(0x13, 0x02),
            x=33,
            y=292,
            rule=Has(Items.LUNCH_BOX) | Has(Items.LARGE_LUNCH_BOX),
        ),
        ItemLocData(
            "Hungry but not for Cheese 2",
            Regions.HIDDEN_VILLAGE,
            Items.CHEESE,
            Section(0x13, 0x02),
            x=33,
            y=292,
            rule=Has(Items.LUNCH_BOX) | Has(Items.LARGE_LUNCH_BOX),
        ),
        # Trick Village
        ItemLocData(
            "On Top of Water", Regions.TRICK_VILLAGE, Items.SEASHELL_NECKLACE, rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
        ),
        ItemLocData(
            "Left 1,000 Wing",
            Regions.TRICK_VILLAGE,
            Items.CHARITY_WINGS,
            Section(0x0A, 0x03),
            x=713,
            y=65294,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Right 1,000 Wing",
            Regions.TRICK_VILLAGE,
            Items.CHARITY_WINGS,
            Section(0x0A, 0x03),
            x=939,
            y=65194,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Rock Bottom",
            Regions.TRICK_VILLAGE,
            Items.LARGE_LUNCH_BOX,
            Section(0x0A, 0x03),
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Yellow Pig Bag",
            Regions.TRICK_VILLAGE,
            Items.YELLOW_EVIL_PIG_BAG,
            rule=HasCleared(Events.WHATS_UNDERWATER) & Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData("Math Bead 1", Regions.TRICK_VILLAGE, Items.MATH_BEAD_1, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 2", Regions.TRICK_VILLAGE, Items.MATH_BEAD_2, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 3", Regions.TRICK_VILLAGE, Items.MATH_BEAD_3, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 4", Regions.TRICK_VILLAGE, Items.MATH_BEAD_4, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 5", Regions.TRICK_VILLAGE, Items.MATH_BEAD_5, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 6", Regions.TRICK_VILLAGE, Items.MATH_BEAD_6, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 7", Regions.TRICK_VILLAGE, Items.MATH_BEAD_7, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 8", Regions.TRICK_VILLAGE, Items.MATH_BEAD_8, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData("Math Bead 9", Regions.TRICK_VILLAGE, Items.MATH_BEAD_9, rule=HasCleared(Events.WHATS_UNDERWATER)),
        ItemLocData(
            "Math Bead 10", Regions.TRICK_VILLAGE, Items.MATH_BEAD_10, rule=HasCleared(Events.WHATS_UNDERWATER)
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
        ItemLocData(
            "Needlegator Teeth",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.NEEDLEGATOR_TEETH,
            Section(0x02, 0x03),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Medecine",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.COLD_MEDECINE,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Old Cheese",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.CHEESE,
            Section(0x02, 0x03),
            x=1440,
            y=64386,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Old Cheese",
            Regions.UNDERGROUND_MAZE_ENTRANCE,
            Items.CHEESE,
            Section(0x02, 0x03),
            x=1083,
            y=65128,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        # Underground Maze
        ItemLocData(
            "100 Year Old Cheese",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Section(0x02, 0x03),
            x=1149,
            y=64562,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Old Lunch",
            Regions.UNDERGROUND_MAZE,
            Items.LUNCH_BOX,
            Section(0x02, 0x03),
            x=472,
            y=64707,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Near the Small Strange Room",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Section(0x02, 0x03),
            x=240,
            y=64380,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Cheese",
            Regions.UNDERGROUND_MAZE,
            Items.CHEESE,
            Section(0x02, 0x03),
            x=630,
            y=64934,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Lunch",
            Regions.UNDERGROUND_MAZE,
            Items.LUNCH_BOX,
            Section(0x02, 0x03),
            x=1202,
            y=64551,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Biting Plant Flower",
            Regions.UNDERGROUND_MAZE,
            Items.BITING_PLANT_FLOWER,
            Section(0x02, 0x03),
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Old Claw",
            Regions.UNDERGROUND_MAZE,
            Items.KOKKA_CLAW,
            Section(0x02, 0x03),
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Old Wing",
            Regions.UNDERGROUND_MAZE,
            Items.CHARITY_WINGS,
            Section(0x02, 0x03),
            x=549,
            y=64739,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Butamashi Thorn",
            Regions.UNDERGROUND_MAZE,
            Items.BUTAMUSHI_THORN,
            Section(0x02, 0x03),
            rule=HasCleared(Events.SOURCE_OF_EVIL_MAGIC) & Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Old Wing",
            Regions.UNDERGROUND_MAZE,
            Items.CHARITY_WINGS,
            Section(0x02, 0x03),
            x=816,
            y=65091,
            rule=HasCleared(Events.SOURCE_OF_EVIL_MAGIC) & Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("Million Year Old Key", Regions.MILLION_YEAR_OLD_MANS_ROOM, Items.MILLION_YEAR_OLD_KEY),
        # The Mermaid's Singing Rock
        ItemLocData("Bronze Medal", Regions.THE_MERMAIDS_SINGING_ROCK, Items.BRONZE_MEDAL),
        ItemLocData("Silver Medal", Regions.THE_MERMAIDS_SINGING_ROCK, Items.SILVER_MEDAL),
        ItemLocData("Gold Medal", Regions.THE_MERMAIDS_SINGING_ROCK, Items.GOLD_MEDAL),
        ItemLocData(
            "Flying Wing Leftmost",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Section(0x06, 0x00),
            x=1612,
            y=64956,
        ),
        ItemLocData(
            "Flying Wing Rightmost",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Section(0x06, 0x00),
            x=2280,
            y=65028,
        ),
        ItemLocData(
            "In the House", Regions.THE_MERMAIDS_SINGING_ROCK, Items.CHARITY_WINGS, Section(0x06, 0x00), x=3158, y=65328
        ),
        ItemLocData(
            "In the back House",
            Regions.THE_MERMAIDS_SINGING_ROCK,
            Items.CHARITY_WINGS,
            Section(0x06, 0x00),
            x=3260,
            y=65303,
        ),
        ItemLocData("Lunch Box", Regions.THE_MERMAIDS_SINGING_ROCK, Items.LUNCH_BOX, Section(0x06, 0x00)),
        *take_out_event_locations,
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

    yan_positions = [
        # (Section(0x00, 0x02), 3060, 64861), # Forest of all Beginnings
        (Section(0x01, 0x04), 3540, 64580),  # Charity Square
        (Section(0x03, 0x05), 3184, 63708),  # Stormy Mountain
        (Section(0x04, 0x0C), 428, 65416),  # Haunted Mansion
        (Section(0x0A, 0x04), 1101, 65280),  # Masakari Jungle
        # (Section(0x13, 0x02), 94, 153) # Hidden Village
    ]

    # Create a list of location checks based on Yan possible positions which all originates from the Take Out event location
    yan_locations: list[ItemLocData] = [
        location.with_section(position[0]).with_coordinates(position[1], position[2])
        for position, location in zip(yan_positions, take_out_event_locations)
    ]

    @staticmethod
    def filter_and_sort(item: ItemData, section: Section, camera_horizontal: int, camera_vertical: int) -> list[int]:
        filtered_locations = LocationHandler.filter(LocationHandler.location_table, item.id, section)
        if len(filtered_locations) <= 0 and item.name == Items.CHEESE:
            filtered_locations = LocationHandler.filter(LocationHandler.yan_locations, item.id, section)

        # Remove locations that are too far away
        filtered_locations = [
            location
            for location in filtered_locations
            if location.get_distance(camera_horizontal, camera_vertical) <= MAX_DISTANCE_THRESHOLD
        ]

        filtered_locations = sorted(
            filtered_locations, key=lambda location: location.get_distance(camera_horizontal, camera_vertical)
        )

        return [location.id for location in filtered_locations]

    @staticmethod
    def filter(locations: list[LocationData] | list[ItemLocData], item_id: int, section: Section) -> list[ItemLocData]:
        return [
            location
            for location in locations
            if isinstance(location, ItemLocData)
            and location.item is not None
            and location.item.id == item_id
            and (location.section is None or location.section.equals(section))
        ]


class TombaLocation(Location):
    game = constants.GAME


def create_all_locations(world: TombaWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def create_regular_locations(world: TombaWorld) -> None:
    for name, locations in LocationHandler.by_region.items():
        region = world.get_region(name)
        region.add_locations({location.name: location.id for location in locations}, TombaLocation)

    # Force furious tornado to be on Mailbox
    MAILBOX = world.get_location(get_name(Locations.MAILBOX, Regions.VILLAGE_OF_ALL_BEGINNINGS))
    MAILBOX.place_locked_item(ItemHandler.create_item(world, Items.FURIOUS_TORNADO))

    # Force baron to be on the original location
    BARON = world.get_location(get_name(Locations.BARON, Regions.DWARF_VILLAGE))
    BARON.place_locked_item(ItemHandler.create_item(world, Items.BARON))


def create_events(world: TombaWorld) -> None:
    """Those event are considered cleared once the logic reach the specific region they are in"""
    for event in EventHandler.event_table:
        region = world.get_region(event.region)
        region.add_event(Started(event.name), rule=event.started_rule, location_type=TombaLocation, item_type=TombaItem)

    VILLAGE_OF_ALL_BEGINNINGS = world.get_region(Regions.VILLAGE_OF_ALL_BEGINNINGS)
    VILLAGE_OF_ALL_BEGINNINGS.add_event(Locations.AP_150_000, location_type=TombaLocation, item_type=TombaItem)
