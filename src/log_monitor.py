import asyncio
import aiofiles
import discord
from dotenv import load_dotenv
import os
import logging

import death_messages

load_dotenv()


class LogMonitor:
    UNKNOWN_PLAYER = "Unknown Player"

    def __init__(self, log_file, channel, docker_monitor=None, friendly_name=None):
        self.channel = channel
        self.docker_monitor = docker_monitor
        self.dev = os.getenv("DEV", "false") == "true"
        self.log_file = log_file
        self.monitoring = False
        self.friendly_name = friendly_name

    def set_docker_monitor(self, docker_monitor):
        """Set reference to docker monitor for communication"""
        self.docker_monitor = docker_monitor

    async def start_monitoring(self):
        """Start monitoring server logs"""
        logging.info(
            f"Starting log monitoring for: {self.log_file} ({self.friendly_name})"
        )
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

        initial_stat = os.stat(self.log_file)
        current_position = 0

        async with aiofiles.open(self.log_file, mode="r") as f:
            await f.seek(0, 2)
            current_position = await f.tell()
            logging.info(f"Started monitoring from position {current_position}")

            while self.monitoring:
                try:
                    current_stat = os.stat(self.log_file)

                    if (
                        current_stat.st_ino != initial_stat.st_ino
                        or current_stat.st_size < current_position
                    ):
                        logging.info(
                            f"Log file rotated, restarting monitoring... ({self.log_file})"
                        )
                        break

                except FileNotFoundError:
                    logging.warning(
                        f"Log file disappeared, restarting monitoring... ({self.log_file})"
                    )
                    break

                try:
                    line = await f.readline()
                    if line is not None and line != "":
                        current_position = await f.tell()
                        logging.debug(f"Read log line: {line}, of type: {type(line)}")
                        message, info = self.cleanup_log_line(line)
                        await self.process_log_line(message, info)
                    else:
                        await asyncio.sleep(1)
                except Exception as e:
                    logging.debug(f"Error reading log line: {e}")
                    # await asyncio.sleep(1)
                    continue

    async def process_log_line(self, line, info):
        """Process a single log line for events"""

        if "joined the game" in line:
            player_name, _ = self.extract_player_name_and_message(line)

            embed = discord.Embed(
                color=0x00FF00,
                title=f"{player_name} s'est connecté.",
            )
            embed.set_footer(text=self.friendly_name)
            await self.channel.send(embed=embed)

        elif "left the game" in line:
            player_name, _ = self.extract_player_name_and_message(line)
            embed = discord.Embed(
                color=0xFF0000,
                title=f"{player_name} s'est déconnecté.",
            )
            embed.set_footer(text=self.friendly_name)
            await self.channel.send(embed=embed)

        elif self.is_chat_message(line):
            player_name, message = self.extract_player_name_and_message(line)
            if player_name.startswith("<") and player_name.endswith(">"):
                player_name = player_name[1:-1]
            embed = discord.Embed(
                color=0xFFFFFF,
                title=f"{player_name}: ",
                description=f"💬 {message}",
            )
            embed.set_footer(text=self.friendly_name)
            await self.channel.send(embed=embed)

        # [08:45:01] [Server thread/INFO]: Done (1.578s)! For help, type "help"
        # [06:45:48] [Server thread/INFO]: Done (22.025s)! For help, type "help"
        elif "Done (" in line and "For help, type" in line:
            logging.info("Server startup complete detected from logs")
            if self.docker_monitor:
                self.docker_monitor.notify_server_ready()

            embed = discord.Embed(
                color=0x00FF00,
                title="Le serveur est prêt.",
            )
            embed.set_footer(text=self.friendly_name)
            await self.channel.send(embed=embed)
            logging.info("Server ready notification sent directly")

        # Check is death message
        elif death_messages.is_death_message(line):
            player_name, message = self.extract_player_name_and_message(line)
            embed = discord.Embed(
                color=0x000000,
                title=f"💀 {player_name} est mort: ",
                description=f"{player_name} {message}",
            )
            embed.set_footer(text=self.friendly_name)
            await self.channel.send(embed=embed)

    def is_chat_message(self, log_line):
        """Check if the log line is a chat message"""
        if death_messages.is_death_message(log_line):
            return False
        
        if (
            log_line.startswith("<")
            and ">" in log_line
        ):
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
