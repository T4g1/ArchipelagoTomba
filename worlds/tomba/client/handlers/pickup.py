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
        }

    async def on_yans_lunch_box(self):
        """Start the Take Out event"""
        self.tomba.events_handler.start(Events.TAKE_OUT)

    async def on_flower_seeds(self):
        """The Flower Seeds event must be started to be able to use the seeds"""
        self.tomba.events_handler.start(Events.FLOWER_SEEDS)

    async def on_seashell_necklace(self):
        """Needs the corresponding event to be able to use the necklace"""
        self.tomba.events_handler.start(Events.THE_MERMAIDS_NECKLACE)

    async def on_weed_killer(self):
        """Needs to start the Death Fruit Juice event"""
        self.tomba.events_handler.start(Events.DEATH_FRUIT_JUICE)
