from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import Items, Events
from .helpers import Cleared, Started, HasCleared
from .locations import LocationHandler, ItemLocData
from .items import ItemHandler

if TYPE_CHECKING:
    from .world import TombaWorld


def set_all_rules(world: TombaWorld) -> None:
    integrity_checks()
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def integrity_checks():
    bypass_integrity_checks = [Items.LEAF_BUTTERFLY]

    used_names = []

    for location in LocationHandler.location_table:
        if location.item is None:
            if Started(location.name) in used_names:
                raise Exception(f"Trying to re-use the location name {Started(location.name)}")

            if Cleared(location.name) in used_names:
                raise Exception(f"Trying to re-use the location name {Cleared(location.name)}")

            used_names.append(Started(location.name))
            used_names.append(Cleared(location.name))

            continue

        if location.name in used_names:
            raise Exception(f"Trying to re-use the location name {location.name}")

        used_names.append(location.name)

        # Make sure that every location that has a countable items has AREA and SECTION set
        if location.item.countable:
            has_coordinates = isinstance(location, ItemLocData) and location.x is not None and location.y is not None
            if location.section is None and not has_coordinates:
                raise Exception(
                    f"Trying to create a location {location.name} "
                    f"with a countable item {location.item.name} "
                    "but no area/section or coordinates discriminator"
                )
        elif location.section is not None and not location.item.is_pants():
            raise Exception(f"Uneccessary area/section for unique item {location.item.name}")

    for item in ItemHandler.item_table:
        if item.name in bypass_integrity_checks:
            continue

        location_ids = LocationHandler.by_item_id[item.id]

        if not item.countable and len(location_ids) > 1:
            raise Exception(f"Unique item {item.name} reused across several locations")

        used_areas_sections = []
        for id in location_ids:
            location = LocationHandler.by_id[id]
            if not isinstance(location, ItemLocData):
                continue

            if location.section is None:
                continue

            if location.x is not None and location.y is not None:
                continue

            section = str(location.section)
            if section in used_areas_sections:
                print(f"Duplicate section discriminator for item {item.name}: {section}")

            used_areas_sections.append(section)


def set_all_entrance_rules(_: TombaWorld) -> None:
    pass


def set_all_location_rules(world: TombaWorld) -> None:
    for location in LocationHandler.location_table:
        if location.rule is not None:
            world.set_rule(world.get_location(location.name), location.rule)


def set_completion_condition(world: TombaWorld) -> None:
    world.set_completion_rule(HasCleared(Events.THE_REAL_EVIL_PIG))
