from .bases import TombaTestBase
from ..locations import get_name
from ..sections import Sections
from ..constants import Regions, Items


class TestChickFilter(TombaTestBase):
    def test_chick_with_no_coordinates(self) -> None:
        item = self.get_item(Items.CHICK)

        # Village
        locations = self.filter(item, Sections.VILLAGE_OF_ALL_BEGINNING, 0, 0)
        self.assertEqual(1, len(locations))

        expected_name = get_name("Kokka Egg in the Village", Regions.VILLAGE_OF_ALL_BEGINNINGS)
        self.assertEqual(expected_name, locations[0].name)

        # Forest (1): Near the elevator
        valid_coordinates = [
            (0, 0),
            (2560, 65010),
            (2535, 64978),
            (2236, 65228),
        ]

        expected_name = get_name("Kokka Egg after the Fog 1", Regions.FOREST_OF_ALL_BEGINNINGS)

        for x, y in valid_coordinates:
            locations = self.filter(item, Sections.FOREST_OF_ALL_BEGINNING_PART_1, x, y)
            self.assertTrue(len(locations) > 0)

            self.assertEqual(expected_name, locations[0].name)

    def test_chick_near_the_pond_intended(self) -> None:
        """Check that a Chick can be grabbed in two sections and in distant coordinates"""
        item = self.get_item(Items.CHICK)

        expected_name = get_name("Kokka Egg after the Fog 2", Regions.FOREST_OF_ALL_BEGINNINGS)

        # When picked-up normaly
        locations = self.filter(item, Sections.FOREST_OF_ALL_BEGINNING_PART_2, 2560, 65010)
        self.assertTrue(len(locations) > 0)

        self.assertEqual(expected_name, locations[0].name)

    def test_chick_near_the_pond_unintended(self) -> None:
        """When picked-up by jumping on the left in another section"""
        item = self.get_item(Items.CHICK)

        valid_coordinates = [
            (2535, 64978),
            (2236, 65228),
            (2011, 65286),
        ]

        expected_name_1 = get_name("Kokka Egg after the Fog 1", Regions.FOREST_OF_ALL_BEGINNINGS)
        expected_name_2 = get_name("Kokka Egg after the Fog 2", Regions.FOREST_OF_ALL_BEGINNINGS)

        for x, y in valid_coordinates:
            locations = self.filter(item, Sections.FOREST_OF_ALL_BEGINNING_PART_1, x, y)
            self.assertEqual(2, len(locations))

            self.assertEqual(expected_name_1, locations[0].name)
            self.assertEqual(expected_name_2, locations[1].name)
