from CommonClient import logger

from . import Handler, AbstractHandler
from ...constants import Addresses, Events, EventStatus, Items, Locations, Regions
from ...events import EventHandler, EventData
from ...locations import LocationHandler, get_name, Cleared
from ...items import ItemHandler
from .door import Doors


class EventsHandler(AbstractHandler):
    """Handles events management and specific event processes"""

    event_states: bytearray = bytearray(0xFF)
    externaly_triggered: list[str] = []

    def init_handlers(self):
        self.handlers = {
            Events.HIDE_AND_GO_SEEK: Handler(self.on_hide_and_go_seek),
            Events.LOOK_AND_SEE: Handler(self.on_look_and_see),
            Events.WHERED_THE_LIGHTS_GO: Handler(self.on_where_the_lights_go),
            Events.I_WANT_A_SILVER_MEDAL: Handler(self.on_i_want_a_silver_medal),
            Events.THE_HAUNTED_MANSION: Handler(self.on_haunted_mansion),
            Events.LAVA_CAVES: Handler(self.on_lava_caves),
            Events.THE_100_FLOWER_FOREST: Handler(self.on_the_100_flower_forest),
            Events.PHOENIX_MOUNTAIN: Handler(self.on_phoenix_mountain),
            Events.BACCUS_VILLAGE: Handler(self.on_baccus_village),
            Events.THE_DEEP_JUNGLE_PIG: Handler(self.on_deep_jungle_pig),
            Events.TRICK_VILLAGE: Handler(self.on_trick_village),
            Events.BREAK_THE_RUSTY_DOOR: Handler(self.on_break_the_rusty_door),
            Events.WE_NEED_POWER: Handler(self.on_we_need_power),
            Events.THE_REAL_EVIL_PIG: Handler(self.on_the_real_evil_pig),
        }

    async def on_the_real_evil_pig(self):
        """Win condition"""
        await self.ctx.on_victory()

    async def on_break_the_rusty_door(self):
        """Uncheck Let's Ride the Raft
        If it's check at this point, the We Need Power event is softlocked"""
        await self.forget(Events.LETS_RIDE_THE_RAFT)

    async def on_we_need_power(self):
        """Check if the Let's Ride The Raft has been cleared before
        See on_break_the_rusty_door: We reset it there to avoid issue"""
        location = LocationHandler.by_name.get(Cleared(Events.LETS_RIDE_THE_RAFT))
        assert location is not None

        if location.id in self.ctx.checked_locations:
            await self.clear(Events.LETS_RIDE_THE_RAFT)

    async def on_trick_village(self):
        """Clear related events"""
        await self.clear(Events.THE_UNDERWATER_PIG_BAG)

    async def on_deep_jungle_pig(self):
        """Clear related events"""
        await self.clear(Events.THE_JUNGLE_PIG_BAG)

    async def on_baccus_village(self):
        """Clear related events"""
        await self.clear(Events.THE_MOUSE_PIG_BAG)

    async def on_phoenix_mountain(self):
        """Clear related events"""
        await self.clear(Events.A_STORMY_PIG_BAG)

        # If the player seal the evil pig before going in the mountain for the first time
        if await self.get_event_state(Events.THE_MOUSE_PIG_BAG) is EventStatus.UNDISCOVERED:
            # Prevents softlock if speaking to the Phoenix guy
            await self.start(Events.THE_MOUSE_PIG_BAG)

            # Allow the player to go to Baccus Village
            await self.tomba.doors_handler.open(Doors.BACCUS_DOOR)

    async def on_the_100_flower_forest(self):
        """Clear related events"""
        await self.clear(Events.THE_EVIL_PIG_BAG)

    async def on_lava_caves(self):
        """Clear related events"""
        await self.clear(Events.THE_FIRE_PIG_BAG)

    async def on_haunted_mansion(self):
        """Clear related events"""
        await self.clear(Events.PAINTING_OF_A_BIG_KEY)
        await self.clear(Events.THE_HAUNTED_PIG_BAG)

    async def on_i_want_a_silver_medal(self):
        """Lock the bronze medal out"""
        await self.clear(Events.I_WANT_A_BRONZE_MEDAL)

    async def on_where_the_lights_go(self):
        """This can be cleared without requiring the dwarf to hand the torch, we need to check that manualy"""
        location = LocationHandler.by_name.get(get_name(Locations.FIRE_STARTER, Regions.DWARF_VILLAGE), None)
        assert location is not None
        await self.ctx.check_locations([location.id])

    async def on_hide_and_go_seek(self):
        # Clear Take Out as it becomes softlocked when this one is cleared
        take_out = EventHandler.by_name.get(Events.TAKE_OUT)
        assert take_out is not None

        await self.set_event_state(take_out, EventStatus.CLEARED)

    async def on_look_and_see(self):
        """When this is cleared prior to grabbing the Telescope, that location becomes unreachable"""
        telescope = ItemHandler.by_name.get(Items.TELESCOPE)
        assert telescope is not None
        locations = LocationHandler.by_item_id.get(telescope.id, [])

        await self.ctx.check_locations(locations)

    async def on_take_out(self):
        # Special case as this one might be force checked by the softlock prevention routine
        # When Hide and Go seek is cleared before clearing this one
        if Events.TAKE_OUT in self.externaly_triggered:
            await self.ctx.check_locations([location.id for location in LocationHandler.take_out_event_locations])

    def get_event(self, event_name: str) -> EventData:
        event = EventHandler.by_name.get(event_name)
        assert event is not None
        return event

    async def clear(self, event_name: str):
        await self.set_event_state(self.get_event(event_name), EventStatus.CLEARED)

    async def forget(self, event_name: str):
        await self.set_event_state(self.get_event(event_name), EventStatus.UNDISCOVERED)

    async def start(self, event_name: str):
        await self.set_event_state(self.get_event(event_name), EventStatus.STARTED)

    async def get_event_state(self, event_name: str) -> EventStatus:
        event = EventHandler.by_name[event_name]
        return EventStatus(self.event_states[event.id])

    async def set_event_state(self, event: EventData, status: EventStatus):
        self.externaly_triggered.append(event.name)
        await self.tomba.playstation.write_memory(Addresses.EVENT_FLAGS + event.id, status.to_bytes())

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
