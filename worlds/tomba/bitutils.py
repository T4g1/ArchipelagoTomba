from dataclasses import dataclass
from typing import Literal

ByteOrder = Literal["big", "little"]


class BitmaskAction(int):
    UNSET_UNCHECKED = 0
    SET_UNCHECKED = 1
    UNSET_CHECKED = 2


@dataclass
class Bitmask:
    """Maps a specific bit in RAM"""

    address: int
    mask: int

    # What to do with it:
    # True: set value if location is checked,
    # False: set value if location is unchecked
    on_checked: bool

    # False: Unset bit, True: Set bit
    target_value: bool

    def __init__(
        self,
        address: int,
        mask: int | None = None,
        position: int | None = None,
        on_checked: bool = False,
        target_value: bool = False,
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
