import asyncio
import aiofiles
import os
import logging

import monitoring.death_messages as death_messages
from messager import Messager


class LogMonitor:
    UNKNOWN_PLAYER = "Unknown Player"

    def __init__(
        self,
        log_file,
        channel,
        docker_monitor,
        friendly_name,
        host,
        ready_event,
        messager: Messager,
    ):
        self.channel = channel
        self.docker_monitor = docker_monitor
        self.log_file = log_file
        self.monitoring = False
        self.messager = messager
        self.friendly_name = friendly_name
        self.host = host
        self.ready_event = ready_event
        self.last_startup_log = None
        self.last_update_time = 0
        self.startup_update_task = None

    def set_docker_monitor(self, docker_monitor):
        """Set reference to docker monitor for communication"""
        self.docker_monitor = docker_monitor

    async def start_monitoring(self):
        """Start monitoring server logs"""
        logging.info(f"Starting log monitoring for: {self.log_file} ({self.host})")
        self.monitoring = True

        while self.monitoring:
            try:
                await self.monitor_log_file()
            except Exception as e:
                logging.error(f"Log monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def stop_monitoring(self):
        """Stop monitoring server logs"""
        self.monitoring = False

    async def monitor_log_file(self):
        """Monitor a single log file cycle"""
        # Check if file exists
        if not os.path.exists(self.log_file):
            logging.warning(f"Log file {self.log_file} not found, waiting...")
            await asyncio.sleep(5)
            return

        initial_stat = os.stat(self.log_file)
        current_position = 0

        async with aiofiles.open(self.log_file, mode="r") as f:
            await f.seek(0, 2)
            current_position = await f.tell()
            logging.info(
                f"Started monitoring from position {current_position} in {self.log_file} on host {self.host}"
            )
            if self.ready_event:
                self.ready_event.set()

            while self.monitoring:
                try:
                    current_stat = os.stat(self.log_file)

                    if (
                        current_stat.st_ino != initial_stat.st_ino
                        or current_stat.st_size < current_position
                    ):
                        logging.info(
                            f"Log file rotated, restarting monitoring... ({self.log_file}) on host {self.host}"
                        )
                        break

                except FileNotFoundError:
                    logging.warning(
                        f"Log file disappeared, restarting monitoring... ({self.log_file}) on host {self.host}"
                    )
                    break

                try:
                    line = await f.readline()
                    if line is not None and line != "":
                        current_position = await f.tell()
                        logging.debug(f"{self.host}: {line}")
                        logging.debug(self.channel)
                        message, _ = self.cleanup_log_line(line)
                        await self.process_log_line(message, line)
                    else:
                        await asyncio.sleep(1)
                except Exception as e:
                    logging.debug(f"Error reading log line: {e}")
                    # await asyncio.sleep(1)
                    continue

    async def process_log_line(self, clean_line, full_line=""):
        """Process a single log line for events"""

        if "joined the game" in clean_line:
            player_name, _ = self.extract_player_name_and_message(clean_line)
            logging.debug(f"Player joined detected: {player_name}")

            await self.messager.send_embed(
                title=f"{player_name} s'est connecté.",
                footer=self.friendly_name,
                color=0x00FF00,
            )

        elif "left the game" in clean_line:
            player_name, _ = self.extract_player_name_and_message(clean_line)
            await self.messager.send_embed(
                title=f"{player_name} s'est déconnecté.",
                footer=self.friendly_name,
                color=0xFF0000,
            )
        elif self.is_chat_message(clean_line):
            player_name, message = self.extract_player_name_and_message(clean_line)
            if player_name.startswith("<") and player_name.endswith(">"):
                player_name = player_name[1:-1]
            await self.messager.send_embed(
                title=f"{player_name}: ",
                description=f"💬 {message}",
                footer=self.friendly_name,
                color=0xFFFFFF,
            )

        # [08:45:01] [Server thread/INFO]: Done (1.578s)! For help, type "help"
        # [06:45:48] [Server thread/INFO]: Done (22.025s)! For help, type "help"
        elif "Done (" in clean_line and "For help, type" in clean_line:
            logging.info("Server startup complete detected from logs")
            if self.docker_monitor:
                self.docker_monitor.notify_server_ready()

            await self.messager.send_embed(
                title="Le serveur démarre.",
                description=full_line,
                footer=self.friendly_name,
                color=0xFFFF00,
                keep=True,
            )

            await self.messager.send_embed(
                title="Le serveur est prêt.",
                footer=self.friendly_name,
                color=0x00FF00,
            )

            self.messager.clear_kept_messages()

            logging.info("Server ready notification sent directly")

        # Check is death message
        elif death_messages.is_death_message(clean_line):
            player_name, message = self.extract_player_name_and_message(clean_line)
            await self.messager.send_embed(
                title=f"💀 {player_name} est mort: ",
                description=f"{player_name} {message}",
                footer=self.friendly_name,
                color=0x000000,
            )

        if self.docker_monitor.waiting_for_startup:
            self.last_startup_log = full_line
            current_time = asyncio.get_event_loop().time()

            if current_time - self.last_update_time >= 4:
                self.last_update_time = current_time
                await self.messager.send_embed(
                    title="Le serveur démarre.",
                    description=full_line,
                    footer=self.friendly_name,
                    color=0xFFFF00,
                    keep=True,
                )

    def is_chat_message(self, log_line):
        """Check if the log line is a chat message"""
        if death_messages.is_death_message(log_line):
            return False

        if log_line.startswith("<") and ">" in log_line:
            return True
        return False

    def extract_player_name_and_message(self, log_line):
        """Extract player name and message from log line"""
        if log_line:
            player_name = log_line.split()[0]
            message = " ".join(log_line.split()[1:])
            print(message)
            return player_name, message
        return self.UNKNOWN_PLAYER, None

    def cleanup_log_line(self, log_line):
        """Clean up log line by removing io infos"""

        parts = str(log_line).strip().split(": ")
        if len(parts) >= 2:
            message = parts[1]
            info = parts[0]
            return message, info
        return None, None
