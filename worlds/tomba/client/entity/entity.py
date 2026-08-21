from ..emulators.emulator import Emulator
from ...bitutils import TypeSize, read_int, write_int

GAME_ENTITY_ADDRESS = 0x0A5970
GAME_ENTITY_COUNT = 200

OBJECT_SLOTS_ADDRESS = 0x0A55C0
OBJECT_SLOTS_COUNT = 0x2D


class Entity:
    SIZE = 0xD4

    address: int

    occupied: int
    initialized: int
    param_1: int
    param_2: int
    status: int
    step: int
    type: int
    ttl: int

    raw: bytearray

    linked_entity: bytearray

    position_x: int
    position_y: int
    position_z: int

    translation_x: int
    translation_y: int
    translation_z: int

    rotation_x: int
    rotation_y: int
    rotation_z: int

    target_x: int
    target_y: int

    flags: bytearray

    texture_x_start: int
    texture_y_start: int
    texture_x_end: int
    texture_y_end: int

    addr_bc: int

    def __init__(self, address: int):
        self.address = address

        self.initialized = 0x00

        self.occupied = 0x00
        self.param_1 = 0x00
        self.param_2 = 0x00
        self.status = 0x00
        self.step = 0x00
        self.type = 0x00
        self.ttl = 0x00

        self.position_x = 0x00
        self.position_y = 0x00
        self.position_z = 0x00

        self.rotation_x = 0x00
        self.rotation_y = 0x00
        self.rotation_z = 0x00

        self.target_x = 0x00
        self.target_y = 0x00

        self.texture_x_start = 0x00
        self.texture_y_start = 0x00
        self.texture_x_end = 0x00
        self.texture_y_end = 0x00

        self.addr_bc = 0x00

        self.flags = bytearray(4)
        self.linked_entity = bytearray(4)

    def load(self, raw: bytearray):
        self.raw = raw.copy()

        self.occupied = raw[0]
        self.initialized = raw[1]
        self.param_1 = raw[2]
        self.param_2 = raw[3]
        self.status = raw[4]
        self.step = raw[5]
        self.type = read_int(raw, 0x08, TypeSize.HALF_WORD)
        self.flags = raw[0x0C:0x10]
        self.ttl = read_int(raw, 0x20, TypeSize.WORD)

        self.position_x = read_int(raw, 0x10, TypeSize.WORD)
        self.position_y = read_int(raw, 0x14, TypeSize.WORD)
        self.position_z = read_int(raw, 0x18, TypeSize.WORD)

        self.rotation_x = read_int(raw, 0x84, TypeSize.HALF_WORD)
        self.rotation_y = read_int(raw, 0x88, TypeSize.HALF_WORD)
        self.rotation_z = read_int(raw, 0x8C, TypeSize.HALF_WORD)

        self.target_x = read_int(raw, 0xC4, TypeSize.HALF_WORD, signed=True)
        self.target_y = read_int(raw, 0xC6, TypeSize.HALF_WORD, signed=True)

        self.texture_x_start = read_int(raw, 0x6C, TypeSize.HALF_WORD)
        self.texture_y_start = read_int(raw, 0x6E, TypeSize.HALF_WORD)
        self.texture_x_end = read_int(raw, 0x70, TypeSize.HALF_WORD)
        self.texture_y_end = read_int(raw, 0x72, TypeSize.HALF_WORD)

        self.addr_bc = read_int(raw, 0xBC, TypeSize.WORD)

        self.linked_entity = raw[0x94:0x98]

    def __str__(self):
        value = f"{hex(self.address)} - Occupied: {hex(self.occupied)}, "
        value += f"Param 1: {hex(self.param_1)}, "
        value += f"Param 2: {hex(self.param_2)}, "
        value += f"Status: {hex(self.status)}, "
        value += f"Type: {hex(self.type)}, "
        value += f"TTL: 0x{self.addr_bc:04X}, "
        value += f"Flags: {self.flags.hex()}, "
        value += f"BC: 0x{self.addr_bc:04X}, "
        value += f"Position: {hex(self.position_x)}, {hex(self.position_y)}, "
        # value += f"Linked to: {reverse(self.linked_entity.hex())}, "
        value += f"Texture: 0x{self.texture_x_start:04X}, 0x{self.texture_y_start:04X}, 0x{self.texture_x_end:04X}, 0x{self.texture_y_end:04X}, "
        # value += f"{self.raw.hex()}"
        return value

    def to_bytearray(self) -> bytearray:
        data = bytearray(Entity.SIZE)
        data[0x00] = self.occupied
        data[0x01] = self.initialized
        data[0x02] = self.param_1
        data[0x03] = self.param_2
        data[0x04] = self.status
        data[0x05] = self.step
        data = write_int(data, 0x08, TypeSize.HALF_WORD, self.type)

        data = write_int(data, 0x10, TypeSize.WORD, self.position_x)
        data = write_int(data, 0x14, TypeSize.WORD, self.position_y)
        data = write_int(data, 0x18, TypeSize.WORD, self.position_z)

        data = write_int(data, 0x20, TypeSize.WORD, self.ttl)

        data = write_int(data, 0x40, TypeSize.WORD, self.address + 0x10)
        data = write_int(data, 0x44, TypeSize.WORD, self.address + 0x18)

        data = write_int(data, 0x84, TypeSize.HALF_WORD, self.rotation_x)
        data = write_int(data, 0x88, TypeSize.HALF_WORD, self.rotation_y)
        data = write_int(data, 0x8C, TypeSize.HALF_WORD, self.rotation_z)

        data = write_int(data, 0xC4, TypeSize.HALF_WORD, self.target_x, signed=True)
        data = write_int(data, 0xC6, TypeSize.HALF_WORD, self.target_y, signed=True)

        return data


class EntityHandler:
    @staticmethod
    async def load_entities(
        psx: Emulator, address: int, count: int, type: int | None = None, size: int = Entity.SIZE
    ) -> list[Entity]:
        entities = []
        for _ in range(count):
            address = address + size
            entity_raw = await psx.read_memory_block(address, size)
            entity = Entity(address)
            entity.load(entity_raw)

            if entity.type == type or type is None:
                entities.append(entity)

        return entities

    @staticmethod
    async def disable(psx: Emulator, type: int, address: int = GAME_ENTITY_ADDRESS, count: int = GAME_ENTITY_COUNT):
        entities = await EntityHandler.load_entities(psx, address, count)
        for entity in entities:
            if entity.type == type:
                await psx.write_memory(entity.address, 0x00.to_bytes())
