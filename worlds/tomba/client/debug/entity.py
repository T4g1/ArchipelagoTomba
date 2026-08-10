from ..emulators.emulator import Emulator
from ...bitutils import reverse


class Entity:
    address: int

    occupied: int
    uvar1: int
    type: int
    item_id: int
    status: int

    raw: bytearray

    linked_entity: bytearray

    x: int
    y: int
    z: int

    flags: bytearray

    def __init__(self, raw: bytearray, address: int):
        self.address = address
        self.raw = raw.copy()

        self.occupied = raw[0]
        self.uvar1 = raw[1]
        self.type = raw[2]
        self.item_id = raw[3]
        self.status = raw[4]
        self.flags = raw[0x0C:0x10]

        self.linked_entity = raw[0x94:0x98]

        self.x = int.from_bytes(raw[0x10:0x14])
        self.y = int.from_bytes(raw[0x14:0x18])
        self.z = int.from_bytes(raw[0x18:0x1C])

    def __str__(self):
        value = f"{hex(self.address)} - Occupied: {hex(self.occupied)}, "
        value += f"?: {hex(self.uvar1)}, "
        value += f"Type: {hex(self.type)}, "
        value += f"Item ID: {hex(self.item_id)}, "
        value += f"Status: {hex(self.status)}, "
        value += f"Flags: {self.flags.hex()}, "
        value += f"Coord: {hex(self.x)}, {hex(self.y)}, {hex(self.z)}, "
        value += f"Linked to: {reverse(self.linked_entity.hex())}, "
        value += f"{self.raw.hex()}"
        return value


disabled = [
    0x14,  # VFX Light
    0x24,  # VFX foreground
]


class EntityHandler:
    ENTITY_ARRAY = 0x0A5970
    ENTITY_MAX_COUNT = 200
    ENTITY_SIZE = 0xD4

    @staticmethod
    async def load_entities(psx: Emulator, disabled: list[int] = disabled) -> list[Entity]:
        entities = []
        for i in range(EntityHandler.ENTITY_MAX_COUNT):
            address = EntityHandler.ENTITY_ARRAY + (i * EntityHandler.ENTITY_SIZE)
            entity_raw = await psx.read_memory_block(address, EntityHandler.ENTITY_SIZE)
            entity = Entity(entity_raw, address)

            if entity.type in disabled:
                await psx.write_memory(address, 0x00.to_bytes())

            else:
                entities.append(entity)
        return entities

    @staticmethod
    async def disable(psx: Emulator, type: int):
        return await EntityHandler.load_entities(psx, [type])
