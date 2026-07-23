from CommonClient import logger

from . import Handler, AbstractHandler
from ...constants import Addresses, Events, EventStatus
from ...events import EventHandler, EventData
from ...locations import LocationHandler


class EventsHandler(AbstractHandler):
    """Handles events management and specific event processes"""

    event_states: bytearray = bytearray(0xFF)
    externaly_triggered: list[str] = []

    def init_handlers(self):
        self.handlers = {Events.HIDE_AND_GO_SEEK: Handler(self.on_hide_and_go_seek)}

    async def is_victory(self):
        return (await self.get_event_state(Events.GRANDPAS_BRACELET)) is EventStatus.CLEARED

    async def check_win_conditions(self):
        if not self.tomba.check_safe_gameplay():
            return

        if await self.is_victory():
            await self.ctx.on_victory()

    async def get_event_state(self, event_name: str) -> EventStatus:
        event = EventHandler.by_name[event_name]
        return EventStatus(self.event_states[event.id])

    def set_event_state(self, event: EventData, status: EventStatus):
        self.externaly_triggered.append(event.name)
        self.tomba.playstation.write_memory(Addresses.EVENT_FLAGS + event.id, status.to_bytes())

    async def update_events(self):
        old_states = self.event_states
        new_states = await self.tomba.playstation.read_memory_block(Addresses.EVENT_FLAGS, 0xFF)

        self.event_states = new_states

        for id in range(len(new_states)):
            if old_states[id] == new_states[id]:
                continue

            event = EventHandler.by_id.get(id, None)
            if event is None:
                continue

            try:
                status = EventStatus(new_states[id])

                if status is not EventStatus.CLEARED:
                    continue

                # Handle Archipelago checks
                await self.ctx.on_event_cleared(event)

                # Trigger rewards for manualy triggered events
                if self.is_externaly_triggered(event.name):
                    await self.ctx.check_locations(LocationHandler.by_event.get(event.name, []))

                await self.handle(event.name)
            except ValueError:
                # At least Beginners Dward Language event is expected to have other values as its a multi step event
                logger.debug(f"Event {event.name} got updated to {new_states[id]} which is not used here")

    def is_externaly_triggered(self, event_name: str):
        return event_name in self.externaly_triggered

    async def on_hide_and_go_seek(self):
        # Clear Take Out as it becomes softlocked when this one is cleared
        take_out = EventHandler.by_name.get(Events.TAKE_OUT)
        assert take_out is not None

        self.set_event_state(take_out, EventStatus.CLEARED)

    async def on_take_out(self):
        # Special case as this one might be force checked by the softlock prevention routine
        # When Hide and Go seek is cleared before clearing this one
        if Events.TAKE_OUT in self.externaly_triggered:
            await self.ctx.check_locations([location.id for location in LocationHandler.take_out_event_locations])
