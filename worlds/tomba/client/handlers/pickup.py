from . import Handler, AbstractHandler
from ...constants import Items, Events


class PickupHandler(AbstractHandler):
    """This class defines additional operations upon receiving a specific item from the multiworld"""

    def init_handlers(self):
        self.handlers = {
            Items.FLOWER_SEEDS: Handler(self.on_flower_seeds),
            Items.SEASHELL_NECKLACE: Handler(self.on_seashell_necklace),
            Items.WEED_KILLER: Handler(self.on_weed_killer),
            Items.YANS_LUNCH_BOX: Handler(self.on_yans_lunch_box),
            Items.GOLD_MEDAL: Handler(self.on_gold_medal),
            Items.SILVER_MEDAL: Handler(self.on_silver_medal),
            Items.BRONZE_MEDAL: Handler(self.on_bronze_medal),
            Items.BANANA_JUICE: Handler(self.on_banana_juice),
        }

    async def on_banana_juice(self):
        """Starts a refreshing drink"""
        await self.tomba.events_handler.start(Events.A_REFRESHING_DRINK)

    async def on_bronze_medal(self):
        """Clear Bronze Medal event"""
        await self.tomba.events_handler.clear(Events.I_WANT_A_BRONZE_MEDAL)

    async def on_silver_medal(self):
        """Clear Silver Medal event"""
        # This call should naturaly call the handler to provide Bronze Medal location and clear that event too
        # See on_i_want_a_silver_medal in handler/events.py
        await self.tomba.events_handler.clear(Events.I_WANT_A_SILVER_MEDAL)

    async def on_gold_medal(self):
        """Clear Gold Medal event"""
        await self.tomba.events_handler.clear(Events.I_WANT_A_GOLD_MEDAL)

    async def on_yans_lunch_box(self):
        """Start the Take Out event"""
        await self.tomba.events_handler.start(Events.TAKE_OUT)

    async def on_flower_seeds(self):
        """The Flower Seeds event must be started to be able to use the seeds"""
        await self.tomba.events_handler.start(Events.FLOWER_SEEDS)

    async def on_seashell_necklace(self):
        """Needs the corresponding event to be able to use the necklace"""
        await self.tomba.events_handler.start(Events.THE_MERMAIDS_NECKLACE)

    async def on_weed_killer(self):
        """Needs to start the Death Fruit Juice event"""
        await self.tomba.events_handler.start(Events.DEATH_FRUIT_JUICE)
