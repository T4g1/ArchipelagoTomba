from collections.abc import Mapping
from typing import Any

from entrance_rando import randomize_entrances
from worlds.AutoWorld import World

from . import constants
from . import locations, regions, rules, web_world
from . import (
    options as tomba_options,
)
from .constants import Regions
from .locations import LocationHandler
from .items import ItemHandler, TombaItem
from .regions import get_entrance_info


class TombaWorld(World):
    """
    Tomba! is a platform/adventure/puzzle game for the PSX
    """

    game = constants.GAME
    web = web_world.APQuestWebWorld()

    options_dataclass = tomba_options.TombaOptions
    options: tomba_options.TombaOptions

    location_name_to_id = LocationHandler.name_to_id
    item_name_to_id = ItemHandler.name_to_id

    origin_region_name = Regions.VILLAGE_OF_ALL_BEGINNINGS

    entrance_pairings: dict[str, dict[int, tuple[int, int, int]]]

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        ItemHandler.create_all_items(self)

    def create_item(self, name: str) -> TombaItem:
        return ItemHandler.create_item(self, name)

    def connect_entrances(self):
        self.entrance_pairings = {}
        if self.options.entrance_randomization:
            placement = randomize_entrances(self, coupled=True, target_group_lookup={0: [0]})

            # Flatten the array so the client can query by section all entrances to update
            for pairing in placement.pairings:
                source_section, source_spawn = get_entrance_info(self.player, pairing[0])
                target_section, target_spawn = get_entrance_info(self.player, pairing[1])

                section_key = source_section.network_key()
                if section_key not in self.entrance_pairings:
                    self.entrance_pairings[section_key] = {}

                self.entrance_pairings[section_key][source_spawn] = (
                    target_section.area_id,
                    target_section.section_id,
                    target_spawn,
                )

    def get_filler_item_name(self) -> str:
        return ItemHandler.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data = self.options.as_dict(
            "bell_warp",
            "keep_blackjack",
            "emulator",
            "optional_randomized",
            "bonus_chests_randomized",
            "cleared_event_rewards",
            "chick_amount",
            "deathlink",
            "god_mode",
            "entrance_randomization",
        )

        slot_data["world_version"] = self.world_version.as_simple_string()

        slot_data["entrance_pairings"] = self.entrance_pairings

        return slot_data
