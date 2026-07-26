from . import Handler, AbstractHandler
from ...constants import Items, Events, EventStatus
from ...events import EventHandler


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
        event = EventHandler.by_name.get(Events.TAKE_OUT)
        assert event is not None
        self.ctx.tomba.events_handler.set_event_state(event, EventStatus.STARTED)

    async def on_flower_seeds(self):
        """The Flower Seeds event must be started to be able to use the seeds"""
        event = EventHandler.by_name.get(Events.FLOWER_SEEDS)
        assert event is not None
        self.ctx.tomba.events_handler.set_event_state(event, EventStatus.STARTED)

    async def on_seashell_necklace(self):
        """Needs the corresponding event to be able to use the necklace"""
        event = EventHandler.by_name.get(Events.THE_MERMAIDS_NECKLACE)
        assert event is not None
        self.ctx.tomba.events_handler.set_event_state(event, EventStatus.STARTED)

    async def on_weed_killer(self):
        """Needs to start the Death Fruit Juice event"""
        event = EventHandler.by_name.get(Events.DEATH_FRUIT_JUICE)
        assert event is not None
        self.ctx.tomba.events_handler.set_event_state(event, EventStatus.STARTED)
