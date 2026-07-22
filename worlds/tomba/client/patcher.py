import pkgutil
from CommonClient import logger

from .compiler import Compiler
from .retroarch import RetroArch
from ..constants import Addresses

HANDLER_HOOK_ORIGINAL = "0800E003"
HANDLER_HOOK = "542C0008"


class PatchException(Exception):
    pass


class Patcher:
    def __init__(self, playstation: RetroArch):
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

        self.playstation.write_memory(Addresses.PATCH_ADD_ITEM, add_item_patch)
        self.playstation.write_memory(Addresses.PATCH_INTERFACE_HANDLER, interface_patch)
        self.playstation.write_memory(Addresses.PATCH_INTERFACE_HOOK, interface_hook)

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
