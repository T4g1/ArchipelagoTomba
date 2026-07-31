import pkgutil
from CommonClient import logger

from .compiler import Compiler
from .emulators.emulator import Emulator
from ..constants import Addresses

HANDLER_HOOK_ORIGINAL = "0800E003"
HANDLER_HOOK = "542C0008"
PATCH_FLOWER_TEARS = "08000601"
PATCH_YANS_LUNCH_BOX = "FFFF00FF"


class PatchException(Exception):
    pass


class Patcher:
    def __init__(self, playstation: Emulator):
        self.playstation = playstation

        interface_file = pkgutil.get_data(__name__, "asm/interface.asm")
        add_item_file = pkgutil.get_data(__name__, "asm/add_item.asm")

        if interface_file is None or add_item_file is None:
            raise PatchException("Unable to load required ASM files")

        try:
            compiler = Compiler()
            # Patch a custom handler triggerred on game sprite updates
            self.interface_patch = compiler.compile(interface_file.decode())

            # Hook to call the custom handler
            self.handler_hook = HANDLER_HOOK

            # Patch receive item method to create a list of found items in game instead
            self.add_item_patch = compiler.compile(add_item_file.decode())
        except Exception as e:
            logger.critical(e)
            raise PatchException("Unable to initialize the patching interface")

    async def patch_game(self):
        """Patch a custom method to play SFX on demand"""
        if await self.is_patched_or_unloaded():
            return

        logger.info("Patching custom methods...")

        add_item_patch = bytes.fromhex(self.add_item_patch)
        interface_patch = bytes.fromhex(self.interface_patch)
        interface_hook = bytes.fromhex(self.handler_hook)

        await self.playstation.write_memory(Addresses.PATCH_ADD_ITEM, add_item_patch)
        await self.playstation.write_memory(Addresses.PATCH_INTERFACE_HANDLER, interface_patch)
        await self.playstation.write_memory(Addresses.PATCH_INTERFACE_HOOK, interface_hook)

        # Allows Tomba to grab pants he already owns
        # Allows the method to reach the add to inventory method
        # await self.playstation.write_memory(Addresses.PATCH_PANTS_PICKUP, bytes.fromhex("00000000"))

        # Patch display popup method
        # Do not append text on "Acquired!" case
        # await self.playstation.write_memory(Addresses.PATCH_POPUP, bytes.fromhex("00000000"))

        logger.info("Game patched")

    async def is_patched_or_unloaded(self) -> bool:
        """Loads the handler hook address to see if the code is:
        * altered: We have already patched the game
        * unaltered: The game should be patched
        * none: The game is not yet loaded"""
        hook_value = await self.playstation.read_memory_block(Addresses.PATCH_INTERFACE_HOOK, 4)
        return hook_value != bytearray.fromhex(HANDLER_HOOK_ORIGINAL)

    async def is_patched(self) -> bool:
        hook_value = await self.playstation.read_memory_block(Addresses.PATCH_INTERFACE_HOOK, 4)
        return hook_value == bytearray.fromhex(HANDLER_HOOK)

    async def is_inventory_flower_tears_patched(self) -> bool:
        value = await self.playstation.async_read_memory(Addresses.PATCH_FLOWER_TEARS)
        return value == bytearray.fromhex("00")

    async def patch_inventory_flower_tears(self):
        """This changes the script to check Flower Tears usability from inventory"""
        await self.playstation.write_memory(Addresses.PATCH_FLOWER_TEARS, bytes.fromhex("00"))

    async def patch_inventory_yans_lunch_box(self):
        """Prevent Yan's Lunch Box to be eaten by using the always False script"""
        await self.playstation.write_memory(Addresses.PATCH_YANS_LUNCH_BOX, bytes.fromhex("00"))
