from . import Handler, AbstractHandler
from ...constants import Locations, Regions, Events
from ...locations import LocationHandler, get_name


class CheckHandler(AbstractHandler):
    """Handles location checks"""

    def is_checked(self, location_name: str, region_name: str):
        """Indicate if the given location has been checked already or not"""
        location = self.get_location(location_name, region_name)
        return location.id in self.ctx.checked_locations

    async def check(self, location_name: str, region_name: str):
        location = self.get_location(location_name, region_name)
        await self.ctx.check_locations([location.id])

    def get_location(self, location_name: str, region_name: str):
        location = LocationHandler.by_name.get(get_name(location_name, region_name), None)
        assert location is not None
        return location

    def init_handlers(self):
        self.handlers = {
            get_name(Locations.GOLDEN_FRUIT, Regions.BACCUS_VILLAGE): Handler(self.on_golden_fruit),
            get_name(Locations.CAMPFIRE, Regions.FOREST_OF_100_FLOWERS): Handler(self.on_campfire),
        }

    async def on_campfire(self):
        """When this is checked, check if the Something Cookin event should be cleared too
        This can happen when the player clears that event before this campfire location
        We disable the event clear in order to leave the campfire accessible"""
        if self.tomba.events_handler.is_cleared(Events.SOMETHINGS_COOKIN):
            await self.tomba.events_handler.clear(Events.SOMETHINGS_COOKIN)

    async def on_golden_fruit(self):
        """Trigger locations from Some Cheese Please"""
        await self.check(Locations.SOME_CHEESE_PLEASE_1, Regions.BACCUS_VILLAGE)
        await self.check(Locations.SOME_CHEESE_PLEASE_2, Regions.BACCUS_VILLAGE)
