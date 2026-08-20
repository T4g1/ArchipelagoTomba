from dataclasses import dataclass
from typing import Literal

ByteOrder = Literal["big", "little"]


class BitmaskAction(int):
    UNSET_UNCHECKED = 0
    SET_UNCHECKED = 1
    UNSET_CHECKED = 2


class TypeSize(int):
    WORD = 4
    HALF_WORD = 2
    BYTE = 1


def read_int(
    data: bytearray, start: int, size: int, byteorder: Literal["little", "big"] = "little", signed: bool = False
) -> int:
    return int.from_bytes(data[start : start + size], byteorder=byteorder, signed=signed)


def write_int(
    data: bytearray,
    start: int,
    size: int,
    value: int,
    byteorder: Literal["little", "big"] = "little",
    signed: bool = False,
) -> bytearray:
    value = min(value, (1 << (8 * size)) - 1)

    data[start : start + size] = value.to_bytes(size, byteorder=byteorder, signed=signed)
    return data


@dataclass
class Bitmask:
    """Maps a specific bit in RAM"""

    address: int
    mask: int

    # What to do with it:
    # True: set value if mask is checked,
    # False: set value if mask is unchecked
    on_checked: bool

    # False: Unset bit, True: Set bit
    target_value: bool

    def __init__(
        self,
        address: int,
        mask: int | None = None,
        position: int | None = None,
        on_checked: bool = True,
        target_value: bool = True,
    ):
        assert mask is not None or position is not None

        self.address = address

        if mask is not None:
            self.mask = mask
        elif position is not None:
            self.mask = Bitmask.from_bit(position)

        self.on_cheked = on_checked
        self.target_value = target_value

    @staticmethod
    def from_bit(position: int, bitorder: ByteOrder = "little"):
        """Create a mask for the given bit in a byte
        * big: The bit position is from left to right
        ie: bit 0 = mask 0x80
        * little: The bit position is from right to left
        ie: bit 0 = mask 0x01"""
        position = max(0, min(position, 7))

        if bitorder == "big":
            return 1 << (7 - position)

        return 1 << position

    def __hash__(self) -> int:
        return hash((self.address, self.mask))


def reverse(hex: str) -> str:
    """Reverse HEX string"""
    return "".join([hex[i : i + 2] for i in range(0, len(hex), 2)][::-1])
