from . import Handler, AbstractHandler
from ...constants import Locations, Regions
from ...locations import LocationHandler, get_name


class CheckHandler(AbstractHandler):
    """Handles location checks"""

    async def check(self, location_name: str, region_name: str):
        location = LocationHandler.by_name.get(get_name(location_name, region_name), None)
        assert location is not None
        await self.ctx.check_locations([location.id])

    def init_handlers(self):
        self.handlers = {get_name(Locations.GOLDEN_FRUIT, Regions.BACCUS_VILLAGE): Handler(self.on_golden_fruit)}

    async def on_golden_fruit(self):
        """Trigger locations from Some Cheese Please"""
        await self.check(Locations.SOME_CHEESE_PLEASE_1, Regions.BACCUS_VILLAGE)
        await self.check(Locations.SOME_CHEESE_PLEASE_2, Regions.BACCUS_VILLAGE)
