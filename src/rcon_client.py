import socket
import asyncio
import struct
import logging


class RCONClient:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.request_id = 0

    async def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(30)  # Increased timeout for slow commands like locate
        await asyncio.get_event_loop().run_in_executor(
            None, self.socket.connect, (self.host, self.port)
        )
        return await self.authenticate()

    async def authenticate(self):
        try:
            auth_response = await self._send_packet(3, self.password)  # Type 3 = AUTH
            if auth_response is None:
                raise Exception("Authentication failed")
            logging.debug("RCON connection established")
            return True
        except Exception as e:
            logging.error(f"RCON connection failed: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False

    async def send_command(self, command):
        try:
            await self.connect()
            response = await self._send_packet(2, command)
            if response is not None:
                self.disconnect()
                logging.debug(f"RCON command executed: {command}")
                return response
            else:
                self.disconnect()
                error_msg = f"❌ Pas de réponse reçue pour la commande: `{command}`"
                logging.error(f"RCON command failed - no response: {command}")
                return error_msg
        except ConnectionRefusedError as e:
            self.disconnect()
            error_msg = "❌ Connection refusée, le serveur est peut-être hors ligne"
            logging.error(f"RCON connection refused for command '{command}': {e}")
            return error_msg
        except TimeoutError as e:
            self.disconnect()
            error_msg = "❌ Délai de connexion dépassé : le serveur ne répond pas"
            logging.error(f"RCON timeout for command '{command}': {e}")
            return error_msg
        except OSError as e:
            self.disconnect()
            error_msg = f"❌ Erreur réseau : {str(e)}"
            logging.error(f"RCON network error for command '{command}': {e}")
            return error_msg
        except Exception as e:
            self.disconnect()
            error_msg = f"❌ Erreur RCON : {str(e)}"
            logging.error(f"RCON command failed '{command}': {e}")
            return error_msg

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

    async def send_command_wrapper(self, *, command: str):
        response = await self.send_command(command)

        if response.startswith("❌"):
            return response

        cleaned_response = response.strip()

        import re

        cleaned_response = re.sub(r"\.(\s*)([A-Z])", r".\n\2", cleaned_response)

        cleaned_response = re.sub(r":(\s*)([0-9A-Za-z])", r":\n\2", cleaned_response)

        cleaned_response = re.sub(r"\s+", " ", cleaned_response)
        cleaned_response = re.sub(r" *\n *", "\n", cleaned_response)
        cleaned_response = re.sub(r"\n{3,}", "\n\n", cleaned_response)

        if len(cleaned_response) > 1900:
            cleaned_response = cleaned_response[:1900] + "\n...[truncated]"
        return f"\n{cleaned_response}\n"
