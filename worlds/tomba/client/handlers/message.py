from asyncio import Lock

from . import AbstractHandler
from ...constants import CustomCommand, Music, SFX
from ..emulators.emulator import Emulator
from ..popup_mappings import CHARMAPS, DEFAULT_CHARMAP
from ..entity.event_entity import display_cube_message

CHARACTER_WIDTH = 0x08

WFM_POPUP_PTR = 0x1F800398
WFM_EVENT_PTR = 0x1F80039C


class WFMPopup:
    MAGIC_WORD = "WFM3"

    loaded: bool = False

    address: int
    dialog_table_offset: int
    dialog_table: int

    wfm_pointer: int

    def __init__(self, wfm_pointer: int):
        self.wfm_pointer = wfm_pointer

    async def _load_dialog_table(self, psx: Emulator):
        """Load dialog table addresses"""

        raw_dialog_table_offset = await psx.read_memory_block(self.address + 8, 2)
        self.dialog_table_offset = int.from_bytes(raw_dialog_table_offset, byteorder="little")

        self.dialog_table = self.address + self.dialog_table_offset

    async def load(self, psx: Emulator) -> bool:
        """Check the WFM table address and availability"""
        raw_address = await psx.read_memory_block(self.wfm_pointer, 4)
        self.address = int.from_bytes(raw_address, byteorder="little") & 0x0FFFFFFF

        if not await self.has_magic_word(psx):
            return False

        await self._load_dialog_table(psx)

        self.loaded = True

        return True

    async def is_loaded(self, psx: Emulator) -> bool:
        if (
            not await self.has_magic_word(psx)
            or not await self.has_correct_wfm(psx)
            or not await self.has_correct_dialog_table(psx)
        ):
            return False

        if not hasattr(self, "dialog_table"):
            return False

        return self.loaded

    async def has_correct_wfm(self, psx: Emulator) -> bool:
        """Check that we are still using that WFM"""
        raw_address = await psx.read_memory_block(self.wfm_pointer, 4)
        address = int.from_bytes(raw_address, byteorder="little") & 0x0FFFFFFF

        return address == self.address

    async def has_magic_word(self, psx: Emulator) -> bool:
        """Check that the current WFM adress is valid"""
        if not hasattr(self, "address"):
            return False

        wfm_popup = await psx.read_memory_block(self.address, 4)

        try:
            return wfm_popup.decode("utf-8") == self.MAGIC_WORD
        except UnicodeDecodeError:
            return False

    async def has_correct_dialog_table(self, psx: Emulator) -> bool:
        """Check that we are still using that WFM"""
        raw_dialog_table_offset = await psx.read_memory_block(self.address + 8, 2)
        return self.dialog_table_offset == int.from_bytes(raw_dialog_table_offset, byteorder="little")

    async def get_dialog_entry(self, psx: Emulator, dialog_index: int):
        """Compute the address of a particular dialog in the dialog table"""

        # The dialog table is constructed with:
        # * List of offset for each dialog
        # * List of dialogs

        dialog_offset_address = self.dialog_table + dialog_index

        raw_dialog_offset = await psx.read_memory_block(dialog_offset_address, 2)
        dialog_offset = int.from_bytes(raw_dialog_offset, byteorder="little")

        return self.dialog_table + dialog_offset

    async def write_message(self, psx: Emulator, area_id: int, address: int, message: str):
        charmaps = CHARMAPS.get(area_id, DEFAULT_CHARMAP)

        # Set size
        size = (len(message) + 2) * CHARACTER_WIDTH

        # Header
        await psx.write_memory(address, 0xFFFA.to_bytes(2, byteorder="little"))
        await psx.write_memory(address + 2, size.to_bytes(2, byteorder="little"))
        await psx.write_memory(address + 4, 0x001D.to_bytes(2, byteorder="little"))

        # Message content
        index = 6
        for character in message:
            value = charmaps.get(character, None)
            if value is not None:
                await psx.write_memory(address + index, value.to_bytes(2, byteorder="little"))
            index += 2

        # Footer
        await psx.write_memory(address + index, 0xFFFD.to_bytes(2, byteorder="little"))
        await psx.write_memory(address + index + 2, 0xFFFE.to_bytes(2, byteorder="little"))


class MessageHandler(AbstractHandler):
    """Handle message displays like popup in the bottom of the screen
    or cube event messages
    Handle two separate message queue: one for each message type"""

    wfm: WFMPopup | None = None

    wfm_message_queue: list[str] = []
    event_message_queue: list[tuple[str, bool]] = []

    POPUP_SLOT_1_STATUS = 0x0A39C2
    POPUP_SLOT_2_STATUS = 0x0A39BA
    POPUP_SIZES = 0x07D05C

    lock: Lock = Lock()

    async def update_messages(self):
        await self.update_wfm()
        await self.update_event()

    async def update_wfm(self):
        """Display popup notification if possible"""
        async with self.lock:
            if len(self.wfm_message_queue) <= 0:
                return

            message = self.wfm_message_queue[0]
            if await self._print(message):
                try:
                    self.wfm_message_queue.pop(0)
                except Exception:
                    pass

    async def update_event(self):
        """Display event message if possible"""
        # Check the game is running
        if not await self.tomba.is_playing():
            return False

        async with self.lock:
            if len(self.event_message_queue) <= 0:
                return

            message, is_cleared = self.event_message_queue[0]
            if await display_cube_message(self.tomba.playstation, message, is_cleared):
                if is_cleared:
                    await self.tomba.set_music(Music.EVENT_CLEARED)
                else:
                    await self.tomba.play_sfx(SFX.EVENT_STARTED)

                try:
                    self.event_message_queue.pop(0)
                except Exception:
                    pass

    async def has_free_slot(self) -> bool:
        """Wait for the first slot to be free
        Leave at least one free slot to avoid issue displaying text during cutscenes"""
        status = await self.tomba.playstation.read_memory_block(self.POPUP_SLOT_2_STATUS, 2)
        return status == bytes.fromhex("FFFF")

    async def has_event_cube_display(self) -> bool:
        """Check if any other event is being displayed"""
        status = await self.tomba.playstation.read_memory_block(self.POPUP_SLOT_2_STATUS, 2)
        return status == bytes.fromhex("FFFF")

    async def print_event(self, message: str, is_cleared: bool):
        self.event_message_queue.append((message, is_cleared))

        await self.update_event()

    async def print(self, message: str):
        self.wfm_message_queue.append(message)

        await self.update_wfm()

    async def _print(self, message: str) -> bool:
        if self.wfm is None:
            self.wfm = WFMPopup(WFM_POPUP_PTR)

        # Check the game is running
        if not await self.tomba.is_playing():
            return False

        psx = self.tomba.playstation
        if not await self.wfm.load(psx):
            return False

        if not await self.has_free_slot():
            return False

        # First three entries are: Used, Equipped, Acquired! followed by one entry by item
        # Item ID 0 is at position 3 (multiplied by two as it's short)
        dialog_offset = 3 * 2

        dialog_entry = await self.wfm.get_dialog_entry(psx, dialog_offset)
        await self.wfm.write_message(psx, self.tomba.section.area_id, dialog_entry, message)

        # Set size
        DEFAULT_SIZE = 12  # + 0x60 when param_2 == 0 (size of Acquired!)
        size = max(0, len(message) + 2 - DEFAULT_SIZE) * CHARACTER_WIDTH
        await psx.write_memory(self.POPUP_SIZES, size.to_bytes(2, byteorder="little"))

        await self.tomba.set_command(CustomCommand.SHOW_MESSAGE)

        return True
