from test.bases import WorldTestBase

from ..constants import GAME
from ..locations import LocationHandler, LocationData
from ..items import ItemHandler, ItemData
from ..sections import Section


class TombaTestBase(WorldTestBase):
    game = GAME

    def get_item(self, item_name: str) -> ItemData:
        item = ItemHandler.by_name.get(item_name)
        assert item is not None

        return item

    def filter(self, item: ItemData, section: Section) -> list[LocationData]:
        location_ids = LocationHandler.filter_and_sort(item, section)
        assert location_ids is not None

        return [LocationHandler.by_id[location.id] for location in location_ids]
