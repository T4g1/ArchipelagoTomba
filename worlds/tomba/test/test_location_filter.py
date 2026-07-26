from .bases import TombaTestBase
from ..locations import LocationHandler, ItemLocData, get_name
from ..constants import Items, Locations, Regions
from ..sections import Sections


class TestLocationFilter(TombaTestBase):
    def test_coordinates_filter(self) -> None:
        """For each location with coordinates, make sure finding
        something at those coordinates return that location"""

        for location in LocationHandler.location_table:
            if not location.name.startswith("Take Out 2"):
                continue

            if not isinstance(location, ItemLocData):
                continue

            assert location.item is not None

            if location.section is None:
                continue

            if location.x is None or location.y is None:
                continue

            locations = self.filter(location.item, location.section, location.x, location.y)

            assert isinstance(locations[0], ItemLocData)

            error = f"Location {location.name} got matched with wrong {locations[0].name}"
            self.assertEqual(location.x, locations[0].x, error)
            self.assertEqual(location.y, locations[0].y, error)
            self.assertEqual(location.region, locations[0].region, error)

    def test_rise_and_shine_powder(self) -> None:
        item = self.get_item(Items.RISE_AND_SHINE_POWDER)

        locations = self.filter(item, Sections.MUSHROOM_FOREST, 0, 0)
        self.assertEqual(1, len(locations))

        expected = get_name(Locations.MONSTER_HUNT, Regions.MUSHROOM_FOREST)
        self.assertEqual(expected, locations[0].name)
