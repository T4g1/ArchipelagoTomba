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

    def filter(self, item: ItemData, section: Section, x: int, y: int) -> list[LocationData]:
        location_ids = LocationHandler.filter_and_sort(item, section, x, y)
        assert location_ids is not None

        return [LocationHandler.by_id[id] for id in location_ids]
