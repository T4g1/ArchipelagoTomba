import asyncio
from PIL import Image

from ..emulators.emulator import CORE_TYPE, EmulatorStatus, Emulator
from ..emulators.bizhawk import BizHawk
from ..handlers.popup import WFMPopup

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
    0x0000,
    0x0000,
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


class WFM(WFMPopup):
    WFM_HEADER_SIZE = 144

    dialogs: list[int] = []
    glyphs: list[int] = []

    def __str__(self):
        return (
            f"ADDRESS: 0x{self.address:X}\n" + f"DIALOG TABLE: 0x{self.dialog_table:X}\n"
            f"DIALOG COUNT: {len(self.dialogs)}\n"
            f"GLYPH COUNT: {len(self.glyphs)}\n"
        )

    async def load_metadata(self, psx: Emulator):
        dialog_count = int.from_bytes(await psx.read_memory_block(self.address + 12, 2), byteorder="little")
        glyph_count = int.from_bytes(await psx.read_memory_block(self.address + 14, 2), byteorder="little")

        glyph_table_address = self.address + self.WFM_HEADER_SIZE

        for i in range(dialog_count):
            self.dialogs.append(0)

        for i in range(glyph_count):
            # Glyph 1
            glyph_offset = await psx.read_int(glyph_table_address + i * 4, 2)

            self.glyphs.append(await self.load_glyph(psx, self.address + glyph_offset, i * 2))

            # Glyph 2
            glyph_offset = await psx.read_int(glyph_table_address + i * 4 + 2, 2)

            self.glyphs.append(await self.load_glyph(psx, self.address + glyph_offset, (i * 2) + 1))

    async def load_glyph(self, psx: Emulator, glyph_data_address: int, id: int) -> int:
        print(f"Loading glyph at: 0x{glyph_data_address:X}")

        # Amount of pixel per byte
        density = await psx.read_int(glyph_data_address, size=2)

        # In byte
        width = await psx.read_int(glyph_data_address + 2, size=2)
        height = await psx.read_int(glyph_data_address + 4, size=2)

        reserved = await psx.read_int(glyph_data_address + 6, size=2)

        print(f"Density: {density}")
        print(f"Width: {width}")
        print(f"Height: {height}")
        print(f"Reserved: {reserved}")

        pixels: list[tuple[int, int, int, int]] = []

        for i in range(width * height // density):
            data = await psx.read_int(glyph_data_address + 8 + i, size=1)

            pixel_1 = data & 0x0F
            pixel_2 = data >> 4

            pixels.append(to_color(dialog_clut[pixel_1]))
            pixels.append(to_color(dialog_clut[pixel_2]))

        image = Image.new("RGBA", (width, height))
        image.putdata(pixels)
        image = image.resize((width * 40, height * 40), resample=Image.Resampling.NEAREST)
        image.save(f"worlds/tomba/client/debug/wfm/dialog_glyph_{id}.png")

        return data


def to_color(clut_value: int, inverted: bool = False) -> tuple[int, int, int, int]:
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

    return (red, green, blue, alpha)


async def extract_wfm(psx: Emulator):
    wfm = WFM()
    if not await wfm.load(psx):
        print("Unable to load WFM")
        return

    await wfm.load_metadata(psx)

    print(wfm)


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
