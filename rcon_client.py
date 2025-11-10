import socket
import asyncio
import struct

class RCONClient:
    def __init__(self, host, port, password, discord_logger):
        self.host = host
        self.port = port
        self.password = password
        self.discord_logger = discord_logger
        self.socket = None
        self.request_id = 0

    async def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        await asyncio.get_event_loop().run_in_executor(
            None, self.socket.connect, (self.host, self.port)
        )
        return await self.authenticate()

    async def authenticate(self):
        try:
            auth_response = await self._send_packet(3, self.password)  # Type 3 = AUTH
            if auth_response is None:
                raise Exception("Authentication failed")
            self.discord_logger.debug("RCON connection established")
            return True
        except Exception as e:
            self.discord_logger.error(f"RCON connection failed: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False

    async def send_command(self, command):
        try:
            await self.connect()
            response = await self._send_packet(2, command)
            self.discord_logger.debug(f"RCON command executed: {command}")
            return response
        except Exception as e:
            self.discord_logger.error(f"RCON command failed: {e}")
            self.disconnect()
            return None

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    async def _send_packet(self, packet_type, data):
        """Send RCON packet and receive response"""
        if self.socket is None:
            return None

        self.request_id += 1

        data_bytes = data.encode("utf-8")
        packet_size = len(data_bytes) + 10
        packet = (
            struct.pack("<iii", packet_size, self.request_id, packet_type)
            + data_bytes
            + b"\x00\x00"
        )

        await asyncio.get_event_loop().run_in_executor(None, self.socket.send, packet)

        response_data = await asyncio.get_event_loop().run_in_executor(
            None, self.socket.recv, 4096
        )

        if len(response_data) < 12:
            return None

        response_size, response_id, _ = struct.unpack("<iii", response_data[:12])

        if packet_type == 3 and response_id != self.request_id:
            return None

        response_string = response_data[12 : 12 + response_size - 10].decode(
            "utf-8", errors="ignore"
        )
        return response_string.strip()
