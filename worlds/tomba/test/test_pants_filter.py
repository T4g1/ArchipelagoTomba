from .bases import TombaTestBase
from ..locations import get_name
from ..sections import Sections
from ..constants import Regions, Locations
from ..items import PANTS


class TestPantsFilter(TombaTestBase):
    def test_pants_filter(self) -> None:
        for pant in PANTS:
            """Check what happens when we get pants"""
            # In Watch Tower
            item = self.get_item(pant)

            locations = self.filter(item, Sections.WATCH_TOWER, 0, 0)
            self.assertEqual(1, len(locations))

            pants = get_name(Locations.WATCH_TOWER_PANTS, Regions.WATCH_TOWER)
            self.assertEqual(locations[0].name, pants)

            # In Stormy Mountains
            locations = self.filter(item, Sections.STORMY_MOUNTAINS_SECOND, 0, 0)
            self.assertEqual(1, len(locations))

            pants = get_name(Locations.STORMY_MOUNTAIN_PANTS, Regions.STORMY_MOUNTAIN)
            self.assertEqual(locations[0].name, pants)

            # In Masakari Jungle
            locations = self.filter(item, Sections.MASAKARI_JUNGLE, 0, 0)
            self.assertEqual(1, len(locations))

            pants = get_name(Locations.MASAKARI_JUNGLE_PANTS, Regions.MASAKARI_JUNGLE)
            self.assertEqual(locations[0].name, pants)
