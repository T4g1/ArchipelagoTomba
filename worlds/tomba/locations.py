from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from collections import defaultdict
from dataclasses import dataclass
from BaseClasses import Location, LocationProgressType
from rule_builder.rules import Has, Rule

from . import constants
from .constants import Regions, Items, Locations, Events
from .items import ItemHandler, ItemData, TombaItem
from .events import EventHandler, HasStarted, HasCleared, Started, Cleared

if TYPE_CHECKING:
    from .world import TombaWorld


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
    area_id: int | None
    section_id: int | None
    rule: Rule | None

    def __init__(
        self,
        name: str,
        region: str,
        item: ItemData | None = None,
        area_id: int | None = None,
        section_id: int | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
    ):
        self.id = LocationData._id_counter
        LocationData._id_counter += 1

        self.name = name
        self.region = region
        self.progress_type = progress_type
        self.item = item
        self.area_id = area_id
        self.section_id = section_id
        self.rule = rule

    def __repr__(self) -> str:
        return self.name


@dataclass
class ItemLocData(LocationData):
    def __init__(
        self,
        name: str,
        region: str,
        item_name: str,
        area_id: int | None = None,
        section_id: int | None = None,
        progress_type: LocationProgressType = LocationProgressType.DEFAULT,
        rule: Rule | None = None,
    ):
        name = get_name(name, region)

        item = ItemHandler.by_name.get(item_name, None)
        if item is None:
            raise Exception(f"Trying to create a location {name} with an unknown item: {item_name}")

        super().__init__(name, region, item, area_id, section_id, progress_type, rule)


class LocationHandler:
    location_table: list[LocationData] = [
        ItemLocData(Locations.MAILBOX, Regions.VILLAGE_OF_ALL_BEGINNINGS, Items.FURIOUS_TORNADO),
        ItemLocData("Peach Flower Gas", Regions.VILLAGE_OF_ALL_BEGINNINGS, Items.BABY_PIG),
        ItemLocData("Kokka Egg in the Village", Regions.VILLAGE_OF_ALL_BEGINNINGS, Items.CHICK, 0x00, 0x00),
        ItemLocData(
            "100 Year Chest in the Tree",
            Regions.VILLAGE_OF_ALL_BEGINNINGS,
            Items.HUNDRED_YEAR_OLD_BELL,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("Bitting Plant", Regions.FOREST_OF_ALL_BEGINNINGS, Items.BITING_PLANT_FLOWER, 0x00, 0x01),
        ItemLocData(
            "10,000 Year Chest",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.LUNCH_BOX,
            0x00,
            0x01,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("Kokka Egg near the elevator", Regions.FOREST_OF_ALL_BEGINNINGS, Items.CHICK, 0x00, 0x01),
        ItemLocData("Kokka Egg near the Hut 1", Regions.FOREST_OF_ALL_BEGINNINGS, Items.CHICK, 0x00, 0x02),
        ItemLocData("Kokka Egg near the Hut 2", Regions.FOREST_OF_ALL_BEGINNINGS, Items.CHICK, 0x00, 0x02),
        ItemLocData(
            "100 Year Chest near the Hut",
            Regions.FOREST_OF_ALL_BEGINNINGS,
            Items.CHARITY_WINGS,
            0x00,
            0x02,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("100 Year Old Reward", Regions.FOREST_OF_ALL_BEGINNINGS, Items.HUNDRED_YEAR_OLD_KEY),
        ItemLocData("Drown", Regions.OL_POND, Items.BANANAS, 0x00, 0x05),
        *[
            ItemLocData(f"Leaf Butterfly {index}", Regions.FOREST_OF_100_FLOWERS, Items.LEAF_BUTTERFLY)
            for index in range(1, 30)
        ],
        ItemLocData("Campfire", Regions.FOREST_OF_100_FLOWERS, Items.BAKED_YAM, rule=Has(Items.BUCKET_OF_WATER)),
        ItemLocData(
            "On Top of the Spikes",
            Regions.FOREST_OF_100_FLOWERS,
            Items.WOOD_BOOMERANG,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("Top of Watch Tower", Regions.WATCH_TOWER, Items.TELESCOPE),
        ItemLocData("Push the Boulder", Regions.WATCH_TOWER, Items.DIRTY_MIRROR),
        ItemLocData("Under the Boulder", Regions.WATCH_TOWER, Items.FLOWER_SEEDS),
        ItemLocData("100 Year Chest", Regions.WATCH_TOWER, Items.JUMPING_PANTS, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)),
        ItemLocData(
            "10,000 Year Chest",
            Regions.WATCH_TOWER,
            Items.LARGE_LUNCH_BOX,
            0x01,
            0x03,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Million Year Chest", Regions.WATCH_TOWER, Items.MILLION_YEAR_OLD_BELL, rule=Has(Items.MILLION_YEAR_OLD_KEY)
        ),
        ItemLocData("Fill the Bucket", Regions.WATCH_TOWER, Items.BUCKET_OF_WATER, rule=Has(Items.BUCKET)),
        ItemLocData(
            "Win the Race", Regions.WATCH_TOWER, Items.SILVER_POWDER, rule=HasCleared(Events.THE_WORLDS_GREATEST_POUT)
        ),
        ItemLocData("On top of the Pole", Regions.WOBBLY_WHARF, Items.BUCKET),
        ItemLocData("Rescue the Child", Regions.DWARF_VILLAGE, Items.CHEESE, 0x02, 0x00),
        ItemLocData("Meet the Dwarf Elder", Regions.DWARF_VILLAGE, Items.BLUE_EVIL_PIG_BAG),
        ItemLocData(
            "1,000 Year Chest",
            Regions.DWARF_VILLAGE,
            Items.CHARITY_WINGS,
            0x02,
            0x00,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData("Fire Starter", Regions.DWARF_VILLAGE, Items.TORCH, rule=HasStarted(Events.WHERED_THE_LIGHTS_GO)),
        ItemLocData("Jail", Regions.DWARF_VILLAGE, Items.BROKEN_VASE, rule=Has(Items.TORCH)),
        ItemLocData("AP Box", Regions.MUSHROOM_FOREST, Items.ORDINARY_MUSHROOM, rule=Has(Locations.AP_150_000)),
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
            "1,000 Year Chest in the Pit 1",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            0x09,
            0x00,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Chest in the Pit 2",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            0x09,
            0x00,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Chest",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            0x09,
            0x00,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Chest",
            Regions.MUSHROOM_FOREST,
            Items.CHARITY_WINGS,
            0x09,
            0x00,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData("Monster Fight", Regions.MUSHROOM_FOREST, Items.RISE_AND_SHINE_POWDER),
        ItemLocData("Crystal Balls", Regions.CHARITY_SQUARE, Items.THREE_CRYSTAL_BALLS),
        ItemLocData("Charity Entrance 1", Regions.CHARITY_SQUARE, Items.CHARITY_WINGS, 0x01, 0x04),
        ItemLocData("Charity Entrance 2", Regions.CHARITY_SQUARE, Items.CHARITY_WINGS, 0x01, 0x04),
        ItemLocData("Leaf Slider", Regions.CHARITY_SQUARE, Items.BLUE_POWDER),
        ItemLocData("Familiar Beach", Regions.MANSION, Items.SEAWEED),
        ItemLocData(
            "100 Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.LUNCH_BOX,
            0x03,
            0x00,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.LARGE_LUNCH_BOX,
            0x03,
            0x00,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Million Year Old Chest",
            Regions.STORMY_MOUNTAIN,
            Items.IRON_BOOMERANG,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
        ),
        ItemLocData("Funga", Regions.STORMY_MOUNTAIN, Items.MOLASSES, rule=Has(Items.FUNGA_DRUM)),
        ItemLocData("Dig", Regions.STORMY_MOUNTAIN, Items.CHEESE, 0x03, 0x01, rule=HasCleared(Events.PHOENIX_MOUNTAIN)),
        ItemLocData(
            "When the Wind Dies Down",
            Regions.STORMY_MOUNTAIN,
            Items.LARGE_LUNCH_BOX,
            0x03,
            0x01,
            rule=HasCleared(Events.PHOENIX_MOUNTAIN),
        ),
        ItemLocData("Big Keyhole", Regions.STORMY_MOUNTAIN, Items.RED_EVIL_PIG_BAG, rule=Has(Items.BIG_KEY)),
        ItemLocData("Herbs", Regions.STORMY_MOUNTAIN, Items.HEALING_HERBS),
        ItemLocData(
            "100 Year Old Pants", Regions.STORMY_MOUNTAIN, Items.DASHING_PANTS, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)
        ),
        ItemLocData(
            "100 Year Old Chest Wing 1",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            0x03,
            0x01,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Old Chest Wing 2",
            Regions.STORMY_MOUNTAIN,
            Items.CHARITY_WINGS,
            0x03,
            0x01,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Grapple", Regions.STORMY_MOUNTAIN, Items.GRAPPLE, rule=Has(Items.THOUSAND_YEAR_OLD_KEY)
        ),
        ItemLocData("Charle's Pant", Regions.LAVA_CAVES, Items.CHARLES_PANTS),
        ItemLocData(
            "Green Evil Pig Bag Chest",
            Regions.LAVA_CAVES,
            Items.GREEN_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData("Grownups", Regions.BACCUS_VILLAGE, Items.WEED_KILLER, rule=HasCleared(Events.MONSTER_HUNT)),
        ItemLocData(
            "Weed Killer",
            Regions.BACCUS_VILLAGE,
            Items.CHARITY_WINGS,
            0x05,
            0x00,
            rule=HasStarted(Events.DEATH_FRUIT_JUICE),
        ),
        ItemLocData(
            "Central Park Chest",
            Regions.BACCUS_VILLAGE,
            Items.ORANGE_EVIL_PIG_BAG,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY) & HasCleared(Events.THE_1000_YEAR_OLD_MAN),
        ),
        ItemLocData(
            "100 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            0x04,
            0x0C,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Old Chest 2",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            0x04,
            0x0C,
            rule=Has(Items.HUNDRED_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Chest near Yan",
            Regions.HAUNTED_MANSION,
            Items.LUNCH_BOX,
            0x04,
            0x0C,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            0x04,
            0x06,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            0x04,
            0x10,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Millions Year Old Chest 1",
            Regions.HAUNTED_MANSION,
            Items.LARGE_LUNCH_BOX,
            0x04,
            0x04,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
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
            0x04,
            0x02,
            rule=HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ItemLocData(
            "Thief in the Chimney 2",
            Regions.HAUNTED_MANSION,
            Items.CHEESE,
            0x04,
            0x02,
            rule=HasCleared(Events.THE_HAUNTED_MANSION),
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
        ItemLocData("Leave Hidden Village", Regions.LAVA_CAVES, Items.WHAT_THE_THIEF_LOST),
        ItemLocData(
            "In Lava Caves Alcove",
            Regions.LAVA_CAVES,
            Items.WHAT_THE_THIEF_FORGOT,
            rule=HasCleared(Events.THE_HAUNTED_MANSION),
        ),
        ItemLocData(
            "10,000 Year Charity Wing 1",
            Regions.LAVA_CAVES,
            Items.CHARITY_WINGS,
            0x03,
            0x02,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "10,000 Year Charity Wing 2",
            Regions.LAVA_CAVES,
            Items.CHARITY_WINGS,
            0x03,
            0x02,
            rule=Has(Items.TEN_THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Charity Wing 1",
            Regions.LAVA_CAVES,
            Items.CHARITY_WINGS,
            0x03,
            0x02,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "1,000 Year Charity Wing 2",
            Regions.LAVA_CAVES,
            Items.CHARITY_WINGS,
            0x03,
            0x02,
            rule=Has(Items.THOUSAND_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "Million Year Large Lunch",
            Regions.LAVA_CAVES,
            Items.LARGE_LUNCH_BOX,
            0x03,
            0x02,
            rule=Has(Items.MILLION_YEAR_OLD_KEY),
        ),
        ItemLocData(
            "100 Year Lunch", Regions.LAVA_CAVES, Items.LUNCH_BOX, 0x03, 0x02, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)
        ),
        ItemLocData("Get the Drum", Regions.MASAKARI_JUNGLE, Items.FUNGA_DRUM, rule=Has(Items.HUNDRED_YEAR_OLD_KEY)),
    ]

    for event in EventHandler.event_table:
        location_table.append(LocationData(Cleared(event.name), event.region, rule=event.cleared_rule))

    by_id: dict[int, LocationData] = {}
    by_name: dict[str, LocationData] = {}
    by_region = defaultdict(list)
    by_item_id: dict[int, list[int]] = defaultdict(list)
    name_to_id: dict[str, int] = {}

    for location in location_table:
        by_id[location.id] = location
        by_name[location.name] = location
        by_region[location.region].append(location)

        if location.item is not None:
            by_item_id[location.item.id].append(location.id)

        name_to_id[location.name] = location.id

    @staticmethod
    def filter(item_id: int, area_id: int, section_id: int) -> list[int]:
        return [
            location.id
            for location in LocationHandler.location_table
            if location.item is not None
            and location.item.id == item_id
            and (location.area_id is None or location.area_id == area_id)
            and (location.section_id is None or location.section_id == section_id)
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
    # TODO: Fix crash when using Tornado and mailbox still has the animation
    MAILBOX = world.get_location(get_name(Locations.MAILBOX, Regions.VILLAGE_OF_ALL_BEGINNINGS))
    MAILBOX.place_locked_item(ItemHandler.create_item(world, Items.FURIOUS_TORNADO))


def create_events(world: TombaWorld) -> None:
    """Those event are considered cleared once the logic reach the specific region they are in"""
    for event in EventHandler.event_table:
        region = world.get_region(event.region)
        region.add_event(Started(event.name), rule=event.started_rule, location_type=TombaLocation, item_type=TombaItem)

    VILLAGE_OF_ALL_BEGINNINGS = world.get_region(Regions.VILLAGE_OF_ALL_BEGINNINGS)
    VILLAGE_OF_ALL_BEGINNINGS.add_event(Locations.AP_150_000, location_type=TombaLocation, item_type=TombaItem)
