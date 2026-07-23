from . import Handler, AbstractHandler
from ...constants import Items, Events, EventStatus
from ...events import EventHandler


class PickupHandler(AbstractHandler):
    """This class defines additional operations upon receiving a specific item from the multiworld"""

    def init_handlers(self):
        self.handlers = {Items.FLOWER_SEEDS: Handler(self.on_flower_seeds, 0, 0)}

    async def on_flower_seeds(self):
        """The Flower Seeds event must be started to be able to use the seeds"""
        event = EventHandler.by_name.get(Events.FLOWER_SEEDS)
        assert event is not None
        self.ctx.tomba.events_handler.set_event_state(event, EventStatus.STARTED)
