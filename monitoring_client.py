import asyncio
import aiofiles
from dotenv import load_dotenv
import os
import logging
import re

import death_messages

load_dotenv()


class LogMonitor:
    UNKNOWN_PLAYER = "Unknown Player"

    def __init__(self, channel, docker_monitor=None):
        self.channel = channel
        self.docker_monitor = docker_monitor
        self.dev = os.getenv("DEV", "false") == "true"
        self.log_file = (
            "./minecraftNewWorldData/logs/latest.log"
            if self.dev
            else "/data/latest.log"
        )
        self.monitoring = False

    def set_docker_monitor(self, docker_monitor):
        """Set reference to docker monitor for communication"""
        self.docker_monitor = docker_monitor

    async def start_monitoring(self):
        """Start monitoring server logs"""
        logging.info(f"Starting log monitoring for: {self.log_file}")
        self.monitoring = True

        while self.monitoring:
            try:
                await self.monitor_log_file()
            except Exception as e:
                logging.error(f"Log monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop_monitoring(self):
        """Stop monitoring server logs"""
        self.monitoring = False

    async def monitor_log_file(self):
        """Monitor a single log file cycle"""
        # Check if file exists
        if not os.path.exists(self.log_file):
            logging.warning(f"Log file {self.log_file} not found, waiting...")
            await asyncio.sleep(5)
            return

        # Get initial file stats
        initial_stat = os.stat(self.log_file)
        current_position = 0

        async with aiofiles.open(self.log_file, mode="r") as f:
            # Move to end of existing content
            await f.seek(0, 2)
            current_position = await f.tell()
            logging.info(f"Started monitoring from position {current_position}")

            while self.monitoring:
                # Check if file still exists and hasn't been rotated
                try:
                    current_stat = os.stat(self.log_file)

                    # Check if file was rotated (inode changed or size decreased)
                    if (
                        current_stat.st_ino != initial_stat.st_ino
                        or current_stat.st_size < current_position
                    ):
                        logging.info("Log file rotated, restarting monitoring...")
                        break

                except FileNotFoundError:
                    logging.warning("Log file disappeared, restarting monitoring...")
                    break

                line = await f.readline()
                if line:
                    current_position = await f.tell()
                    await self.process_log_line(line.strip())
                else:
                    await asyncio.sleep(1)

    async def process_log_line(self, line):
        """Process a single log line for events"""
        # Check for important events
        if "joined the game" in line:
            player_name, _ = self.extract_player_name_and_message(line)
            await self.channel.send(f"🟢 **{player_name}** s'est connecté.")

        elif "left the game" in line:
            player_name, _ = self.extract_player_name_and_message(line)
            await self.channel.send(f"🔴 **{player_name}** s'est déconnecté.")

        elif self.is_chat_message(line):
            player_name, message = self.extract_player_name_and_message(line)
            if player_name and message:
                # Remove < and > from player name if present
                if player_name.startswith("<") and player_name.endswith(">"):
                    player_name = player_name[1:-1]
                await self.channel.send(f"💬 **{player_name}**: {message}")

        # Check for server ready message
        elif (
            "Done (" in line
            and "For help, type" in line
            and "[Server thread/INFO]:" in line
        ):
            logging.info("Server startup complete detected from logs")
            if self.docker_monitor:
                self.docker_monitor.notify_server_ready()

            # Always send ready message as fallback (in case Docker monitoring fails)
            await self.channel.send("🟢 **Le serveur est prêt !**")
            logging.info("Server ready notification sent directly")

        # Check is death message
        elif death_messages.is_death_message(self.cleanup_log_line(line)):
            # Extract the actual message part from the log line
            player_name, message = self.extract_player_name_and_message(line)
            await self.channel.send(f"💀 **{player_name}** {message}")

        elif "WARN" in line or "ERROR" in line:
            # Optionally send warning/error alerts
            pass

    def is_chat_message(self, log_line):
        """Check if the log line is a chat message"""
        try:
            return (
                "<" in log_line
                and ">" in log_line
                and "Async Chat Thread" in log_line
                and "/INFO]:" in log_line
            )
        except Exception:
            return False

    def extract_player_name_and_message(self, log_line):
        """Extract player name and message from log line"""
        clean_log = self.cleanup_log_line(log_line)
        if clean_log:
            player_name = clean_log.split()[0]
            message = " ".join(clean_log.split()[1:])
            print(message)
            return player_name, message
        return self.UNKNOWN_PLAYER, None

    def cleanup_log_line(self, log_line):
        """Clean up log line by removing player names"""
        parts = log_line.split(": ")
        if len(parts) >= 2:
            message = parts[1].strip()
            return message
        return None
