from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rule_builder.rules import Has, Rule

from .constants import Items, Events
from .helpers import Cleared, Started, HasCleared
from .locations import LocationHandler, ItemLocData
from .items import ItemHandler
from .events import EventHandler

if TYPE_CHECKING:
    from .world import TombaWorld


def set_all_rules(world: TombaWorld) -> None:
    integrity_checks()
    set_all_location_rules(world)
    set_all_events_rules(world)
    set_completion_condition(world)


def integrity_checks():
    bypass_integrity_checks = [Items.LEAF_BUTTERFLY, Items.AP_CRYSTAL, Items.APPLE]

    used_names = []

    for location in LocationHandler.location_table:
        if getattr(location, "non_inventory", False):
            continue
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
            if (
                location.section is None
                and location.at is None
                and (isinstance(location, ItemLocData) and location.event is None)
            ):
                raise Exception(
                    f"Trying to create a location {location.name} "
                    f"with a countable item {location.item.name} "
                    "but no area/section"
                )

    for item in ItemHandler.item_table:
        if item.name in bypass_integrity_checks:
            continue

        location_ids = LocationHandler.by_item_id[item.id]

        if not item.countable and len(location_ids) > 1:
            raise Exception(f"Unique item {item.name} reused across several locations")


def set_all_location_rules(world: TombaWorld) -> None:
    for location in LocationHandler.location_table:
        if location.rule is not None:
            set_rule(world, location.name, location.rule)


def set_all_events_rules(world: TombaWorld) -> None:
    for event in EventHandler.event_table:
        set_rule(world, Started(event.name), event.started_rule)

        if not world.options.cleared_event_rewards:
            set_rule(world, Cleared(event.name), event.cleared_rule)


def set_rule(world: TombaWorld, location_name: str, rule: Rule[Any]):
    # Apply specific settings to rules
    if location_name == Cleared(Events.INSIDE_THE_KOKKA_EGGS):
        amount = world.options.chick_amount.value
        if not world.options.chick_randomized:
            amount = 4

        rule = Has(Items.CHICK, amount)

    world.set_rule(world.get_location(location_name), rule)


def set_completion_condition(world: TombaWorld) -> None:
    world.set_completion_rule(HasCleared(Events.A_REAL_EVIL_PIG))
