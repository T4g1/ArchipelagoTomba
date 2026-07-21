from __future__ import annotations

from typing import TYPE_CHECKING, Any
from dataclasses import dataclass
from rule_builder.rules import Has

from BaseClasses import Region, CollectionRule

from .constants import Regions, Items, Events
from .events import Started, Cleared

if TYPE_CHECKING:
    from .world import TombaWorld
    from rule_builder.rules import Rule


purification_mapping: dict[int, dict[int, int]] = {
    # Phoenix Mountain
    0x03: {
        # Cursed to purified
        0x00: 0x04,
        0x01: 0x05,
        # Purified to cursed
        0x04: 0x00,
        0x05: 0x01,
    },
    # Masakari Jungle
    0x0A: {
        # Cursed to purified
        0x00: 0x04,
        0x01: 0x05,
        0x02: 0x06,
        0x03: 0x07,
        # Purified to cursed
        0x04: 0x00,
        0x05: 0x01,
        0x06: 0x02,
        0x07: 0x03,
    },
}


@dataclass
class Section:
    area_id: int
    section_id: int

    def alternate(self) -> int:
        """Give the purified/cursed section ID"""
        area_mapping = purification_mapping.get(self.area_id, {})
        return area_mapping.get(self.section_id, self.section_id)

    def __equ__(self, section: Section) -> bool:
        return self.area_id == section.area_id and (
            self.section_id == section.section_id or self.section_id == section.alternate()
        )

    def __repr__(self) -> str:
        return f"0x{self.area_id:02x}-0x{self.section_id:02x}"


region_names = [value for key, value in Regions.__dict__.items() if not key.startswith("_") and isinstance(value, str)]


def create_and_connect_regions(world: TombaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: TombaWorld) -> None:
    regions = []

    for region_name in region_names:
        regions.append(Region(region_name, world.player, world.multiworld))

    world.multiworld.regions += regions


def connect(world: TombaWorld, source_name: str, target_name: str, rule: CollectionRule | Rule[Any] | None = None):
    source = world.get_region(source_name)
    target = world.get_region(target_name)
    source.connect(target, f"{source} to {target}", rule)


def connect_regions(world: TombaWorld) -> None:
    connect(world, Regions.VILLAGE_OF_ALL_BEGINNINGS, Regions.FOREST_OF_ALL_BEGINNINGS, Has(Items.FURIOUS_TORNADO))
    connect(world, Regions.VILLAGE_OF_ALL_BEGINNINGS, Regions.THE_MERMAIDS_SINGING_ROCK, Has(Items.FUEL_BAR))

    connect(world, Regions.FOREST_OF_ALL_BEGINNINGS, Regions.FOREST_OF_100_FLOWERS, Has(Items.CHICK, 4))
    connect(world, Regions.FOREST_OF_ALL_BEGINNINGS, Regions.OL_POND)

    connect(world, Regions.FOREST_OF_100_FLOWERS, Regions.DWARF_VILLAGE)
    connect(
        world,
        Regions.FOREST_OF_100_FLOWERS,
        Regions.WOBBLY_WHARF,
        lambda state: state.can_reach_location(Started(Events.SAVE_THE_DWARVES), world.player),
    )
    connect(
        world,
        Regions.FOREST_OF_100_FLOWERS,
        Regions.WATCH_TOWER,
        lambda state: state.can_reach_location(Started(Events.SAVE_THE_DWARVES), world.player),
    )

    connect(world, Regions.CHARITY_SQUARE, Regions.HIDDEN_VILLAGE, Has(Items.LEAF_BUTTERFLY, 29))

    connect(
        world,
        Regions.DWARF_VILLAGE,
        Regions.DWARF_JAIL,
        lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), world.player),
    )

    connect(
        world,
        Regions.WATCH_TOWER,
        Regions.MUSHROOM_FOREST,
        lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), world.player),
    )
    connect(
        world,
        Regions.WATCH_TOWER,
        Regions.CHARITY_SQUARE,
        lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), world.player),
    )
    connect(
        world,
        Regions.WATCH_TOWER,
        Regions.UNDERGROUND_MAZE_ENTRANCE,
        lambda state: state.can_reach_location(Cleared(Events.WE_NEED_POWER), world.player),
    )

    connect(
        world,
        Regions.WOBBLY_WHARF,
        Regions.CHARITY_SQUARE,
        lambda state: state.can_reach_location(Started(Events.TO_PHOENIX_MOUNTAIN), world.player),
    )

    connect(world, Regions.MUSHROOM_FOREST, Regions.MANSION)
    connect(
        world,
        Regions.MUSHROOM_FOREST,
        Regions.STORMY_MOUNTAIN,
        lambda state: state.can_reach_location(Cleared(Events.THE_WORLDS_GREATEST_POUT), world.player),
    )

    connect(world, Regions.STORMY_MOUNTAIN, Regions.LAVA_CAVES)
    connect(world, Regions.STORMY_MOUNTAIN, Regions.BACCUS_VILLAGE)

    connect(
        world,
        Regions.LAVA_CAVES,
        Regions.PHOENIXS_NEST,
        lambda state: state.can_reach_location(Cleared(Events.LAVA_CAVES), world.player),
    )

    connect(world, Regions.PHOENIXS_NEST, Regions.MASAKARI_JUNGLE, Has(Items.BUNK_FLOWER, 5))

    connect(world, Regions.BACCUS_VILLAGE, Regions.MUSHROOM_FOREST)
    connect(world, Regions.BACCUS_VILLAGE, Regions.CENTRAL_PARK)
    connect(
        world,
        Regions.BACCUS_VILLAGE,
        Regions.BACCUS_LAKE,
        lambda state: state.can_reach_location(Started(Events.A_DRINK_FOR_GROWNUPS), world.player),
    )
    connect(
        world,
        Regions.BACCUS_VILLAGE,
        Regions.HAUNTED_MANSION,
        lambda state: state.can_reach_location(Cleared(Events.A_DRINK_FOR_GROWNUPS), world.player),
    )

    connect(
        world,
        Regions.MASAKARI_JUNGLE,
        Regions.OLD_TREE_HILL,
        lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), world.player),
    )
    connect(world, Regions.MASAKARI_JUNGLE, Regions.Y_CROSSING, Has(Items.MINERS_HAT))

    connect(world, Regions.Y_CROSSING, Regions.CLOCK_TOWER)
    connect(
        world,
        Regions.Y_CROSSING,
        Regions.IRON_CASTLE,
        lambda state: state.can_reach_location(Started(Events.WE_NEED_POWER), world.player),
    )
    connect(
        world,
        Regions.Y_CROSSING,
        Regions.LUMBERJACK_FACTORY,
        lambda state: state.can_reach_location(Started(Events.WE_NEED_POWER), world.player),
    )

    connect(
        world,
        Regions.OL_POND,
        Regions.TRICK_VILLAGE,
        lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), world.player)
        and state.has(Items.KEY_TO_OL_POND, world.player),
    )
    connect(
        world,
        Regions.UNDERGROUND_MAZE_ENTRANCE,
        Regions.UNDERGROUND_MAZE,
        Has(Items.THIEFS_WIRE),
    )
    connect(world, Regions.UNDERGROUND_MAZE, Regions.THE_STRANGE_SMALL_ROOM)

    connect(
        world,
        Regions.THE_MERMAIDS_SINGING_ROCK,
        Regions.OLD_TREE_HILL,
        lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), world.player),
    )
    connect(
        world,
        Regions.THE_MERMAIDS_SINGING_ROCK,
        Regions.MASAKARI_JUNGLE,
        lambda state: state.can_reach_location(Cleared(Events.I_CANT_SWIM), world.player),
    )
