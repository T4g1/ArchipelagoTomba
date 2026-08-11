from .bases import TombaTestBase
from ..locations import get_name
from ..constants import Items, Locations, Regions
from ..sections import Sections


class TestLocationFilter(TombaTestBase):
    def test_rise_and_shine_powder(self) -> None:
        item = self.get_item(Items.RISE_AND_SHINE_POWDER)

        locations = self.filter(item, Sections.MUSHROOM_FOREST)
        self.assertEqual(1, len(locations))

        expected = get_name(Locations.MONSTER_HUNT, Regions.MUSHROOM_FOREST)
        self.assertEqual(expected, locations[0].name)
