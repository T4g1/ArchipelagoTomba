from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has

from .constants import Events, Items
from .locations import Cleared, LocationHandler

if TYPE_CHECKING:
    from .world import TombaWorld


def set_all_rules(world: TombaWorld) -> None:
    integrity_checks()
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def integrity_checks():
    bypass_integrity_checks = [
        Items.LEAF_BUTTERFLY
    ]

    # Make sure that every location that has a countable items has AREA and SECTION set
    for location in LocationHandler.location_table:
        if location.item is None:
            continue
        
        if location.item.countable and (
            location.area_id is None or
            location.section_id is None
        ) and location.item.name not in bypass_integrity_checks:
            raise Exception(f"Trying to create a location {location.name} with a countable item {location.item.name} but no area/section discriminator")


def set_all_entrance_rules(_: TombaWorld) -> None:
    pass


def set_all_location_rules(world: TombaWorld) -> None:
    for location in LocationHandler.location_table:
        if location.rule is not None:
            world.set_rule(world.get_location(location.name), location.rule)


def set_completion_condition(world: TombaWorld) -> None:
    world.set_completion_rule(Has(Items.FURIOUS_TORNADO))
