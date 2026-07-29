from . import AbstractHandler
from ...constants import CustomCommand
from ..retroarch import RetroArch

CHARACTER_WIDTH = 0x08
CHARMAP: dict[str, int] = {
    # Uppercase letters
    "A": 0x800C,
    "B": 0x801A,
    "C": 0x8010,
    "D": 0x8016,
    "E": 0x8007,
    "F": 0x8012,
    "G": 0x802F,
    "H": 0x8026,
    "I": 0x802A,
    "J": 0x802C,
    "K": 0x8022,
    "L": 0x8015,
    "M": 0x8027,
    "N": 0x802E,
    "O": 0x801E,
    "P": 0x8025,
    "Q": 0x8008,
    "R": 0x8032,
    "S": 0x8029,
    "T": 0x801C,
    "U": 0x8000,
    "V": 0x8035,
    "W": 0x8024,
    "X": 0x8038,
    "Y": 0x801F,
    "Z": 0x8004,
    # Lowercase letters
    "a": 0x8018,
    "b": 0x8030,
    "c": 0x800D,
    "d": 0x8003,
    "e": 0x8002,
    "f": 0x8019,
    "g": 0x8014,
    "h": 0x8006,
    "i": 0x800A,
    "j": 0x802B,
    "k": 0x8011,
    "l": 0x8021,
    "m": 0x8028,
    "n": 0x801B,
    "o": 0x8013,
    "p": 0x800B,
    "q": 0x8008,
    "r": 0x800E,
    "s": 0x8001,
    "t": 0x8005,
    "u": 0x8009,
    "v": 0x8033,
    "w": 0x8017,
    "x": 0x802D,
    "y": 0x8023,
    "z": 0x8004,
    # "0": 0x8020, "1": 0x801D, "2": 0x80, "3": 0x80, "4": 0x80,
    # "5": 0x80, "6": 0x80, "7": 0x80, "8": 0x80, "9": 0x80,
    # Math
    "*": 0x8038,
    "+": 0x8036,
    # Punctuation and Space
    "!": 0x800F,
    "?": 0x8004,
    ".": 0x8037,
    " ": 0x8004,
    ",": 0x8031,
    "'": 0x8034,
    # Unsupported: QZz?
}


class WFMPopup:
    MAGIC_WORD = "WFM3"
    WFM_POPUP_PTR = 0x1F800398

    available: bool = False
    address: int
    dialog_table_offset: int
    dialog_table: int

    async def load_dialog_table(self, psx: RetroArch) -> bool:
        """Load dialog table addresses"""
        if not self.available:
            return False

        raw_dialog_table_offset = await psx.read_memory_block(self.address + 8, 2)
        self.dialog_table_offset = int.from_bytes(raw_dialog_table_offset, byteorder="little")

        self.dialog_table = self.address + self.dialog_table_offset

        return True

    async def load(self, psx: RetroArch) -> bool:
        """Check the WFM table address and availability"""
        raw_address = await psx.read_memory_block(self.WFM_POPUP_PTR, 4)
        self.address = int.from_bytes(raw_address, byteorder="little") & 0x0FFFFFFF

        wfm_popup = await psx.read_memory_block(self.address, 4)
        self.available = wfm_popup.decode("utf-8") == self.MAGIC_WORD

        if not self.available:
            return False

        return await self.load_dialog_table(psx)

    async def get_dialog_entry(self, psx: RetroArch, dialog_index: int):
        """Compute the address of a particular dialog in the dialog table"""

        # The dialog table is constructed with:
        # * List of offset for each dialog
        # * List of dialogs

        dialog_offset_address = self.dialog_table + dialog_index

        raw_dialog_offset = await psx.read_memory_block(dialog_offset_address, 2)
        dialog_offset = int.from_bytes(raw_dialog_offset, byteorder="little")

        return self.dialog_table + dialog_offset

    async def write_message(self, psx: RetroArch, address: int, message: str):
        # Set size
        size = (len(message) + 2) * CHARACTER_WIDTH

        # Header
        psx.write_memory(address, 0xFFFA.to_bytes(2, byteorder="little"))
        psx.write_memory(address + 2, size.to_bytes(2, byteorder="little"))
        psx.write_memory(address + 4, 0x001D.to_bytes(2, byteorder="little"))

        # Message content
        index = 6
        for character in message:
            value = CHARMAP.get(character, 0x8004)
            psx.write_memory(address + index, value.to_bytes(2, byteorder="little"))
            index += 2

        # Footer
        psx.write_memory(address + index, 0xFFFD.to_bytes(2, byteorder="little"))
        psx.write_memory(address + index + 2, 0xFFFE.to_bytes(2, byteorder="little"))


class PopupHandler(AbstractHandler):
    """Handle popup message in the bottom of the screen"""

    loaded = False
    wfm: WFMPopup | None = None

    message_queue: list[str] = []

    POPUP_SLOT_1_STATUS = 0x0A39C2
    POPUP_SLOT_2_STATUS = 0x0A39BA
    POPUP_SIZES = 0x07D05C

    async def update_popups(self):
        if len(self.message_queue) <= 0:
            return

        message = self.message_queue[0]
        if await self._print(message):
            self.message_queue.pop(0)

    async def has_free_slot(self) -> bool:
        """Wait for the first slot to be free
        Leave at least one free slot to avoid issue displaying text during cutscenes"""
        status = await self.tomba.playstation.read_memory_block(self.POPUP_SLOT_2_STATUS, 2)
        return status == bytes.fromhex("FFFF")

    def print(self, message: str):
        self.message_queue.append(message)

    async def _print(self, message: str) -> bool:
        if self.wfm is None:
            self.wfm = WFMPopup()

        psx = self.tomba.playstation
        if not self.wfm.available and not await self.wfm.load(psx):
            return False

        if not await self.has_free_slot():
            return False

        # First three entries are: Used, Equipped, Acquired! followed by one entry by item
        # Item ID 0 is at position 3 (multiplied by two as it's short)
        dialog_offset = 3 * 2

        dialog_entry = await self.wfm.get_dialog_entry(psx, dialog_offset)
        await self.wfm.write_message(psx, dialog_entry, message)

        # Set size
        DEFAULT_SIZE = 12  # + 0x60 when param_2 == 0 (size of Acquired!)
        size = max(0, len(message) + 2 - DEFAULT_SIZE) * CHARACTER_WIDTH
        psx.write_memory(self.POPUP_SIZES, size.to_bytes(2, byteorder="little"))

        await self.tomba.set_command(CustomCommand.SHOW_MESSAGE)

        return True
