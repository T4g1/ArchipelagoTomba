import textwrap

from .entity import Entity, EntityHandler
from ..emulators.emulator import Emulator
from ...bitutils import TypeSize, read_int, write_int

EVENT_CHAR_ADDRESS = 0x0B0B88
EVENT_CHAR_COUNT = 0x2D

EVENT_CHAR_START_X_ADDRESS = 0x0774F2
EVENT_CHAR_START_Y_ADDRESS = 0x0774F4

EVENT_CHAR_HANDLER_ARRAY_ADDRESS = 0x1F80033C
EVENT_CHAR_HANDLER_ARRAY_OFFSET = 0x1F800340

CHARACTER_SLOTS_COUNT = 0x1F80023A
CHARACTER_SLOTS_ADDRESSES = 0x1F80020C

LETTER_WIDTH = 0x14
WHITESPACE_WIDTH = 0x10
LETTER_HEIGHT = 0x20

MAX_EVENT_MESSAGE_SIZE = 32
MAX_EVENT_MESSAGE_LINE_SIZE = 17

EVENT_CUBE_TYPE = 0x7D16


event_glyph_map: dict[str, int] = {
    "a": 0x0D,
    "b": 0x31,
    "c": 0x13,
    "d": 0x0F,
    "e": 0x14,
    "f": 0x2D,
    "g": 0x20,
    "h": 0x18,
    "i": 0x1D,
    "j": 0x34,  # Upper case only
    "k": 0x24,
    "l": 0x15,
    "m": 0x25,
    "n": 0x0E,
    "o": 0x1F,
    "p": 0x10,
    "q": 0x2B,  # Not found
    "r": 0x0C,
    "s": 0x12,
    "t": 0x16,
    "u": 0x22,
    "v": 0x2E,
    "w": 0x27,
    "x": 0x2F,
    "y": 0x23,
    "z": 0x37,
    "A": 0x03,
    "B": 0x0A,
    "C": 0x00,
    "D": 0x06,
    "E": 0x02,
    "F": 0x1E,
    "G": 0x0B,
    "H": 0x21,
    "I": 0x2A,
    "J": 0x34,
    "K": 0x2C,
    "L": 0x01,
    "M": 0x08,
    "N": 0x36,
    "O": 0x1B,
    "P": 0x26,
    "Q": 0x2B,  # Not found
    "R": 0x04,
    "S": 0x29,
    "T": 0x17,
    "U": 0x07,
    "V": 0x35,
    "W": 0x1C,
    "X": 0x2F,  # Lower case
    "Y": 0x09,
    "Z": 0x37,  # Lower case
    "!": 0x05,
    "?": 0x28,
    "'": 0x11,
    "+": 0x32,
    "=": 0x33,
    ".": 0x2B,
    ",": 0x30,
    "0": 0x1A,
    "1": 0x19,
    "2": 0x2B,  # Not found
    "3": 0x2B,  # Not found
    "4": 0x2B,  # Not found
    "5": 0x38,
    "6": 0x2B,  # Not found
    "7": 0x2B,  # Not found
    "8": 0x39,
    "9": 0x2B,  # Not found
}


class EventCharacter(Entity):
    is_cleared: bool

    index: int
    glyph_id: int

    handler_address: int

    def __init__(
        self,
        address: int,
        letter: str,
        index: int,
        is_cleared: bool,
        start_x: int,
        start_y: int,
        target_x: int,
        target_y: int,
    ):
        super().__init__(address)

        self.is_cleared = is_cleared
        self.index = index
        self.handler_address = 0x00000000

        self.glyph_id = event_glyph_map.get(letter, 0x2B)

        self.occupied = 0x01
        self.initialized = 0x00
        self.param_1 = 0x01
        self.param_2 = 0x01 if is_cleared else 0x00
        self.type = EVENT_CUBE_TYPE
        self.status = 0x00
        self.step = 0x00
        self.ttl = 0x00000001

        # Starting position
        self.position_x = start_x
        self.position_y = start_y
        self.position_z = 0

        # Goal position
        self.target_x = target_x
        self.target_y = target_y

    def to_bytearray(self) -> bytearray:
        data = super().to_bytearray()

        data[0x0A] = 0x14
        data[0x0C] = self.index
        data[0x0D] = 0x01
        data[0x0F] = 0xA6

        data[0x1E] = 0x00
        data[0x2E] = 0x01

        data[0xD2] = 0x00

        data[0x1C] = 0x88

        # data = write_int(data, 0x7E, TypeSize.HALF_WORD, 0xF007, byteorder="big")
        # data = write_int(data, 0x80, TypeSize.HALF_WORD, 0x00F7, byteorder="big")
        # data = write_int(data, 0x82, TypeSize.HALF_WORD, 0x12FF, byteorder="big")

        data = write_int(data, 0xA0, TypeSize.WORD, self.handler_address)

        data = write_int(data, 0xBC, TypeSize.BYTE, self.glyph_id, byteorder="big")

        data = write_int(data, 0xC2, TypeSize.HALF_WORD, 0x2F00, byteorder="big")
        data = write_int(data, 0xC8, TypeSize.HALF_WORD, 0xFFD8)

        data = write_int(data, 0x30, TypeSize.WORD, self.position_x)
        data = write_int(data, 0x34, TypeSize.WORD, self.position_y)
        data = write_int(data, 0x38, TypeSize.WORD, self.position_z)

        return data


async def display_cube_message(psx: Emulator, message: str, is_cleared: bool = False) -> bool:
    """Spawns event char entities to display a text in cube event format"""
    char_count = len(message)
    if char_count > MAX_EVENT_MESSAGE_SIZE:
        message = message[:MAX_EVENT_MESSAGE_SIZE]

    slots = await psx.read_int(CHARACTER_SLOTS_COUNT, size=TypeSize.HALF_WORD)
    if slots < char_count:
        return False

    # Anything else being displayed ?
    if await EntityHandler.load_entities(psx, EVENT_CHAR_ADDRESS, EVENT_CHAR_COUNT, EVENT_CUBE_TYPE, is_occupied=True):
        return False

    await psx.write_memory(CHARACTER_SLOTS_COUNT, (slots - char_count).to_bytes(TypeSize.HALF_WORD, byteorder="little"))

    entity_address_pointer = await psx.read_int(CHARACTER_SLOTS_ADDRESSES, size=TypeSize.WORD, byteorder="little")
    await psx.write_memory(
        CHARACTER_SLOTS_ADDRESSES,
        (entity_address_pointer + char_count * TypeSize.WORD).to_bytes(TypeSize.WORD, byteorder="little"),
    )

    entity_address_array = await psx.read_memory_block(entity_address_pointer, size=char_count * TypeSize.WORD)

    start_x = await psx.read_int(EVENT_CHAR_START_X_ADDRESS, size=TypeSize.HALF_WORD)
    start_y = await psx.read_int(EVENT_CHAR_START_Y_ADDRESS, size=TypeSize.HALF_WORD)

    handler_base_address = await psx.read_int(EVENT_CHAR_HANDLER_ARRAY_ADDRESS, size=TypeSize.WORD)
    handler_address_offset = await psx.read_int(handler_base_address + 4, size=TypeSize.WORD)
    handler_address = handler_base_address + handler_address_offset

    lines = textwrap.wrap(message, width=MAX_EVENT_MESSAGE_LINE_SIZE)

    cleared_trigger = False

    index = 0
    target_y = -32
    for line in lines:
        width = 0
        for letter in line:
            if letter != " ":
                width += LETTER_WIDTH
            else:
                width += WHITESPACE_WIDTH

        target_x = -(width // 2) + (LETTER_WIDTH // 2)

        for line_index in range(len(line)):
            letter = line[line_index]
            if letter == " ":
                target_x += WHITESPACE_WIDTH
                continue

            entity_address = read_int(entity_address_array, index * TypeSize.WORD, TypeSize.WORD, byteorder="little")
            entity = EventCharacter(
                entity_address,
                letter,
                index,
                is_cleared=is_cleared,
                start_x=start_x,
                start_y=start_y,
                target_x=target_x,
                target_y=target_y,
            )
            entity.handler_address = handler_address

            data = entity.to_bytearray()

            if not cleared_trigger and is_cleared:
                data = write_int(data, 0xCE, TypeSize.HALF_WORD, 0x8000)
                cleared_trigger = True

            # print(f"Event address at: 0x{entity_address:04X}")
            # print(f"Event data: {data.hex().upper()}")

            await psx.write_memory(entity.address, data)

            target_x += LETTER_WIDTH
            index += 1

        target_y += LETTER_HEIGHT

    return True
