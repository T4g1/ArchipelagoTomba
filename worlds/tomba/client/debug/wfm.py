import asyncio
from dataclasses import dataclass
from PIL import Image

from ..emulators.emulator import CORE_TYPE, EmulatorStatus, Emulator
from ..emulators.bizhawk import BizHawk
from ..handlers.popup import WFMPopup

HALF_WORD_SIZE = 2
BYTE_SIZE = 1

dialog_clut: list[int] = [
    0x8000,
    0x0400,
    0x4E73,
    0x2529,
    0x35AD,
    0x4210,
    0x14A5,
    0x7E4D,
    0x03E0,
    0x421F,
    0x297F,
    0x5319,
    0x4674,
    0x3A11,
    0x8000,
    0x8000,
]

event_clut: list[int] = [
    0x01FF,
    0x8400,
    0x7FFF,
    0x3DEF,
    0x2529,
    0x56B5,
    0x00F0,
    0x0198,
    0x6739,
    0x0134,
    0x01FF,
    0x7C00,
    0x7C00,
    0x7C00,
    0x7C00,
    0x7C00,
]


@dataclass
class Pixel:
    red: int
    green: int
    blue: int
    alpha: int

    def tuple(self) -> tuple[int, int, int, int]:
        return (self.red, self.green, self.blue, self.alpha)


@dataclass
class Glyph:
    pixels: list[Pixel]
    width: int
    height: int

    def pixel_tuples(self) -> list[tuple[int, int, int, int]]:
        return [pixel.tuple() for pixel in self.pixels]


@dataclass
class Line:
    glyphs: list[Glyph]


@dataclass
class Dialog:
    lines: list[Line]


class WFM(WFMPopup):
    WFM_HEADER_SIZE = 144

    dialogs: list[Dialog] = []
    glyphs: list[Glyph] = []

    def __str__(self):
        return (
            f"ADDRESS: 0x{self.address:X}\n" + f"DIALOG TABLE: 0x{self.dialog_table:X}\n"
            f"DIALOG COUNT: {len(self.dialogs)}\n"
            f"GLYPH COUNT: {len(self.glyphs)}\n"
        )

    async def load_dialogs(self, psx: Emulator, save: bool = False):
        dialog_count = int.from_bytes(await psx.read_memory_block(self.address + 12, 2), byteorder="little")
        print(f"Dialog count: {dialog_count}")

        start_dialog = 0x00
        for dialog_id in range(start_dialog, dialog_count):
            self.dialogs.append(await self.load_dialog(psx, dialog_id, save=save))

    async def load_glyphs(self, psx: Emulator, save: bool = False):
        glyph_count = int.from_bytes(await psx.read_memory_block(self.address + 14, 2), byteorder="little")
        print(f"Glyph count: {glyph_count}")

        self.glyphs = []
        for glyph_id in range(glyph_count):
            self.glyphs.append(await self.load_glyph(psx, glyph_id, save=save))

    async def load_glyph(self, psx: Emulator, id: int, save: bool = False) -> Glyph:
        glyph_table_address = self.address + self.WFM_HEADER_SIZE
        glyph_offset = await psx.read_int(glyph_table_address + id * HALF_WORD_SIZE, 2)
        glyph_data_address = self.address + glyph_offset

        print(f"Loading glyph {id} (0x{id:02X}) at: 0x{glyph_data_address:X}")

        mode = await psx.read_int(glyph_data_address, size=HALF_WORD_SIZE)

        # In byte
        height = await psx.read_int(glyph_data_address + 2, size=HALF_WORD_SIZE)
        width = await psx.read_int(glyph_data_address + 4, size=HALF_WORD_SIZE)

        _ = await psx.read_int(glyph_data_address + 6, size=HALF_WORD_SIZE)

        print(f"Mode: {mode}")
        print(f"Width: {width}")
        print(f"Height: {height}")

        pixels: list[Pixel] = []

        raw = await psx.read_memory_block(glyph_data_address + 8, size=width * height)
        for i in range(width * height // 2):
            data = int.from_bytes(raw[i : i + BYTE_SIZE], byteorder="little")

            pixel_1 = data & 0x0F
            pixel_2 = data >> 4

            pixels.append(get_pixel(dialog_clut[pixel_1]))
            pixels.append(get_pixel(dialog_clut[pixel_2]))

        if mode == 3:
            if width == 10:
                width = 12
        elif mode != 2:
            raise Exception(f"Unknown mode {mode}")

        glyph = Glyph(pixels, width, height)

        if save:
            image = Image.new("RGBA", (glyph.width, glyph.height))
            image.putdata(glyph.pixel_tuples())
            image = image.resize((glyph.width * 40, glyph.height * 40), resample=Image.Resampling.NEAREST)
            image.save(f"worlds/tomba/client/debug/wfm/dialog_glyph_{id:02}_0x{id:02X}.png")

        return glyph

    async def load_dialog(self, psx: Emulator, id: int, save: bool = False) -> Dialog:
        dialog_offset = await psx.read_int(self.dialog_table + id * HALF_WORD_SIZE, size=HALF_WORD_SIZE)
        data_address = self.dialog_table + dialog_offset

        if len(self.glyphs) <= 0:
            await self.load_glyphs(psx, save=False)

        print(f"Loading dialog {id} (0x{id:02X}) at: 0x{data_address:X}")

        finished = False
        index = 0
        glyph_height = 0
        dialog = Dialog([])

        while not finished:
            line = Line([])

            while not finished:
                data = await psx.read_int(data_address + (index * HALF_WORD_SIZE), size=HALF_WORD_SIZE)
                if data == 0xFFFF or data == 0xFFFE:
                    finished = True
                    break

                # Box init
                elif data == 0xFFFA:
                    # Skip box dimension
                    index += 3
                    continue

                # Wait for user input
                elif data == 0xFFFC:
                    pass

                # Color
                elif data == 0xFFF7:
                    index += 2
                    continue

                # Unknown ?
                elif data == 0xFFF6:
                    index += 3
                    continue

                # Pause
                elif data == 0xFFF9:
                    index += 2
                    continue

                # New line
                elif data == 0xFFFD or data == 0xFFF8 or data == 0xFFFB:
                    dialog.lines.append(line)
                    line = Line([])

                elif data >> 8 == 0x80 or data >> 8 == 0xC0:
                    glyph_id = data & 0xFF
                    glyph = self.glyphs[glyph_id]

                    if glyph_height == 0:
                        glyph_height = glyph.height
                    elif glyph_height != glyph.height:
                        print(f"Unuspported glyph height: {glyph.height}, first was: {glyph_height}")

                    if glyph_height == glyph.height:
                        line.glyphs.append(glyph)
                else:
                    print(f"Unuspported entry: 0x{data:04X}")

                index += 1

        if save and len(dialog.lines):
            height = glyph_height * len(dialog.lines)
            width = 0
            for line in dialog.lines:
                line_width = sum([glyph.width for glyph in line.glyphs])
                if width < line_width:
                    width = line_width

            if width > 0:
                image = Image.new("RGBA", (width, height))

                for line_index, line in enumerate(dialog.lines):
                    y = line_index * glyph_height

                    x = 0
                    for glyph in line.glyphs:
                        glyph_image = Image.new("RGBA", (glyph.width, glyph.height))
                        glyph_image.putdata(glyph.pixel_tuples())
                        image.paste(glyph_image, (x, y))

                        x += glyph.width

                image = image.resize((width * 40, height * 40), resample=Image.Resampling.NEAREST)
                image.save(f"worlds/tomba/client/debug/wfm/dialog_{id:02}_0x{id:02X}.png")

        return dialog


def get_pixel(clut_value: int, inverted: bool = False) -> Pixel:
    red = (clut_value >> 0) & 0x1F
    green = (clut_value >> 5) & 0x1F
    blue = (clut_value >> 10) & 0x1F
    alpha = (clut_value >> 15) & 0x01

    red = (red * 255) // 31
    green = (green * 255) // 31
    blue = (blue * 255) // 31
    alpha = (1 - alpha) * 255

    if inverted:
        red = 255 - red
        green = 255 - green
        blue = 255 - blue

    return Pixel(red, green, blue, alpha)


async def extract_wfm(psx: Emulator):
    wfm = WFM()
    if not await wfm.load(psx):
        print("Unable to load WFM")
        return

    print(wfm)

    await wfm.load_glyphs(psx, save=True)
    await wfm.load_dialogs(psx, save=True)
    # await wfm.load_glyph(psx, 0x39, save=True)
    # await wfm.load_dialog(psx, 0x54, save=True)


async def main():
    emulator_address = "127.0.0.1"
    emulator_port = 55355

    emulator = BizHawk(emulator_address, emulator_port)

    print("Waiting on connection to emulator...")

    while True:
        try:
            if not await emulator.connect():
                continue

            _ = await emulator.get_version()
            status, core_type, _, _ = await emulator.get_status()

            if (status == EmulatorStatus.PAUSED or status == EmulatorStatus.PLAYING) and core_type == CORE_TYPE:
                break
        except (BlockingIOError, TimeoutError, ConnectionResetError):
            await asyncio.sleep(1.0)
            pass

    await extract_wfm(emulator)


if __name__ == "__main__":
    asyncio.run(main())
