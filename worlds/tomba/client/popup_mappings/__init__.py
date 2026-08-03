from ...sections import Sections
from .village_of_all_beginning import CHARMAP as MAPPING_AREA_0
from .forest_of_100_flowers import CHARMAP as MAPPING_AREA_1
from .dwarf_village import CHARMAP as MAPPING_AREA_2
from .stormy_mountains import CHARMAP as MAPPING_AREA_3

DEFAULT_CHARMAP = MAPPING_AREA_1

DEBUG_CHARMAPS: dict[str, int] = {
    # Uppercase letters
    "A": 0x8000,
    "B": 0x8001,
    "C": 0x8002,
    "D": 0x8003,
    "E": 0x8004,
    "F": 0x8005,
    "G": 0x8006,
    "H": 0x8007,
    "I": 0x8008,
    "J": 0x8009,
    "K": 0x800A,
    "L": 0x800B,
    "M": 0x800C,
    "N": 0x800D,
    "O": 0x800E,
    "P": 0x800F,
    "Q": 0x8010,
    "R": 0x8011,
    "S": 0x8012,
    "T": 0x8013,
    "U": 0x8014,
    "V": 0x8015,
    "W": 0x8016,
    "X": 0x8017,
    "Y": 0x8018,
    "Z": 0x8019,
    # Lowercase letters
    "a": 0x801A,
    "b": 0x801B,
    "c": 0x801C,
    "d": 0x801D,
    "e": 0x801E,
    "f": 0x801F,
    "g": 0x8020,
    "h": 0x8021,
    "i": 0x8022,
    "j": 0x8023,
    "k": 0x8024,
    "l": 0x8025,
    "m": 0x8026,
    "n": 0x8027,
    "o": 0x8028,
    "p": 0x8029,
    "q": 0x802A,
    "r": 0x802B,
    "s": 0x802C,
    "t": 0x802D,
    "u": 0x802E,
    "v": 0x802F,
    "w": 0x8030,
    "x": 0x8031,
    "y": 0x8032,
    "z": 0x8033,
    "0": 0x8034,
    "1": 0x8035,
    "2": 0x8036,
    "3": 0x8037,
    "4": 0x8038,
    "5": 0x8039,
    "6": 0x803A,
    "7": 0x803B,
    "8": 0x803C,
    "9": 0x803D,
    # Math
    "*": 0x803E,
    "+": 0x803F,
    # Punctuation and Space
    "!": 0x8040,
    "?": 0x8041,
    ".": 0x8042,
    " ": 0x8043,
    ",": 0x8044,
    "'": 0x8045,
    "/": 0x8046,
}

CHARMAPS: dict[int, dict[str, int]] = {
    Sections.VILLAGE_OF_ALL_BEGINNING.area_id: MAPPING_AREA_0,
    Sections.FOREST_OF_100_FLOWERS.area_id: MAPPING_AREA_1,
    Sections.DWARF_VILLAGE.area_id: MAPPING_AREA_2,
    Sections.STORMY_MOUNTAINS.area_id: MAPPING_AREA_3,
    0x04: MAPPING_AREA_1,  # Haunted Mansion
    0x07: MAPPING_AREA_1,  # Haunted Mansion Purified
}
