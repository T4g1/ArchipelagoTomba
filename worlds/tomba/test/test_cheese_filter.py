from .bases import TombaTestBase
from ..locations import get_name
from ..sections import Sections
from ..constants import Regions, Items, Locations


class TestCheeseFilter(TombaTestBase):
    def test_double_cheese_mansion_cry_room(self) -> None:
        """Check both cheese in the mansion cry room are correctly dispatched"""
        item = self.get_item(Items.CHEESE)

        # Camera is fix there
        locations = self.filter(item, Sections.CRY_ROOM, 160, 65396)
        self.assertEqual(2, len(locations))

        cheese_1 = get_name(Locations.CRY_CHEESE_LEFT, Regions.HAUNTED_MANSION)
        cheese_2 = get_name(Locations.CRY_CHEESE_RIGHT, Regions.HAUNTED_MANSION)

        self.assertIn(locations[0].name, [cheese_1, cheese_2])
        self.assertIn(locations[1].name, [cheese_1, cheese_2])
