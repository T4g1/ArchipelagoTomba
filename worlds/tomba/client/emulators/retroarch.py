import asyncio
import re
import select
import socket
from socket import socket as SocketType

from CommonClient import logger

from .emulator import EmulatorStatus, Emulator, BadEmulatorResponse
from ... import options


def status_from_string(value):
    match value:
        case "PAUSED":
            return EmulatorStatus.PAUSED
        case "PLAYING":
            return EmulatorStatus.PLAYING
        case "CONTENTLESS":
            return EmulatorStatus.CONTENTLESS
        case _:
            return EmulatorStatus.UNKNOWN


class RetroArch(Emulator):
    ID: int = options.Emulator.option_retroarch
    name: str = "RetroArch"

    socket: SocketType

    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        assert self.socket
        self.socket.setblocking(False)

    def send(self, b):
        # logger.debug(f"> {b}")
        if type(b) is str:
            b = b.encode("ascii")
        self.socket.sendto(b, (self.address, self.port))

    def recv(self):
        select.select([self.socket], [], [])
        response, _ = self.socket.recvfrom(4096)
        # logger.debug(f"< {response}")
        return response

    async def async_recv(self, timeout=1.0):
        response = await asyncio.wait_for(asyncio.get_running_loop().sock_recv(self.socket, 4096), timeout)
        return response

    async def send_command(self, command, timeout=1.0):
        self.send(f"{command}\n")
        response_str = await self.async_recv()
        self.check_command_response(command, response_str)
        return response_str.rstrip()

    def check_command_response(self, command: str, response: bytes):
        if command == "VERSION":
            ok = re.match(r"\d+\.\d+\.\d+", response.decode("ascii")) is not None
        else:
            ok = response.startswith(command.encode())
        if not ok:
            logger.warning(f"Bad response to command {command} - {response}")
            raise BadEmulatorResponse()

    async def get_version(self):
        version = await self.send_command("VERSION")
        return version.decode("ascii", errors="replace")

    async def get_status(self):
        status = await self.send_command("GET_STATUS")
        if status.count(b" ") < 2:
            return (EmulatorStatus.UNKNOWN, "", "", "")

        _, status, info = status.split(b" ", 2)
        status = status_from_string(status.decode("ascii", errors="replace"))

        if info.count(b",") < 2:
            return (status, "", "", "")

        core_type, rom_name, rom_crc = info.split(b",", 2)

        return (
            status,
            core_type.decode("ascii", errors="replace"),
            rom_name.decode("ascii", errors="replace"),
            rom_crc,
        )

    async def async_read_memory(self, address, size=1):
        command = "READ_CORE_MEMORY"

        self.send(f"{command} {hex(address)} {size}\n")
        response = await self.async_recv()
        self.check_command_response(command, response)
        response = response[:-1]
        splits = response.decode().split(" ", 2)
        try:
            response_addr = int(splits[1], 16)
        except ValueError:
            raise BadEmulatorResponse()

        if response_addr != address:
            raise BadEmulatorResponse()

        ret = bytearray.fromhex(splits[2])
        if len(ret) > size:
            raise BadEmulatorResponse()
        return ret

    async def write_memory(self, address, bytes: bytearray | bytes):
        command = "WRITE_CORE_MEMORY"

        self.send(f'{command} {hex(address)} {" ".join(hex(b) for b in bytes)}')
        select.select([self.socket], [], [])
        response, _ = self.socket.recvfrom(4096)
        self.check_command_response(command, response)
        splits = response.decode().split(" ", 3)

        assert splits[0] == command

        if splits[2] == "-1":
            logger.info(splits[3])
