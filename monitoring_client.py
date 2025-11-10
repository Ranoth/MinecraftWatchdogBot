import asyncio
import aiofiles
from dotenv import load_dotenv
import os
import logging
import re

load_dotenv()

class LogMonitor:
    UNKNOWN_PLAYER = "Unknown Player"
    
    def __init__(self, channel, docker_monitor=None):
        self.channel = channel
        self.docker_monitor = docker_monitor
        self.dev = os.getenv("DEV", "false") == "true"
        self.log_file = "./minecraftNewWorldData/logs/latest.log" if self.dev else "/data/latest.log"
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
                await self._monitor_log_file()
            except Exception as e:
                logging.error(f"Log monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def stop_monitoring(self):
        """Stop monitoring server logs"""
        self.monitoring = False
        
    async def _monitor_log_file(self):
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
                    await self._process_log_line(line.strip())
                else:
                    await asyncio.sleep(1)
                    
    async def _process_log_line(self, line):
        """Process a single log line for events"""
        # Check for important events
        if "joined the game" in line:
            player_name = self._extract_player_name_join(line)
            await self.channel.send(f"🟢 **{player_name}** s'est connecté.")
            
        elif "left the game" in line:
            player_name = self._extract_player_name_leave(line)
            await self.channel.send(f"🔴 **{player_name}** s'est déconnecté.")
            
        elif self._is_chat_message(line):
            player_name, message = self._extract_chat_message(line)
            if player_name and message:
                await self.channel.send(f"💬 **{player_name}**: {message}")
        
        # Check for server ready message
        elif "Done (" in line and "For help, type" in line and "[Server thread/INFO]:" in line:
            logging.info("Server startup complete detected from logs")
            if self.docker_monitor:
                await self.docker_monitor.notify_server_ready()
            
            # Always send ready message as fallback (in case Docker monitoring fails)
            await self.channel.send("🟢 **Le serveur Minecraft est prêt !**")
            logging.info("Server ready notification sent directly")

        elif "WARN" in line or "ERROR" in line:
            # Optionally send warning/error alerts
            pass
            
    def _is_chat_message(self, log_line):
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

    def _extract_chat_message(self, log_line):
        """Extract player name and message from chat log line"""
        try:
            pattern = r"\[.*?\] \[Async Chat Thread - #\d+/INFO\]: <(\w+)> (.*)"
            match = re.search(pattern, log_line)

            if match:
                player_name = match.group(1)
                message = match.group(2)
                return player_name, message

            return None, None
        except Exception as e:
            logging.error(f"Error extracting chat message: {e}")
    def _extract_player_name_join(self, log_line):
        """Extract player name from join message"""
        try:
            parts = log_line.split(": ")
            if len(parts) >= 2:
                message = parts[1].strip()
                if " joined the game" in message:
                    return message.replace(" joined the game", "")
            return self.UNKNOWN_PLAYER
        except Exception:
            return self.UNKNOWN_PLAYER
    def _extract_player_name_leave(self, log_line):
        """Extract player name from leave message"""
        try:
            parts = log_line.split(": ")
            if len(parts) >= 2:
                message = parts[1].strip()
                if " left the game" in message:
                    return message.replace(" left the game", "")
            return self.UNKNOWN_PLAYER
        except Exception:
            return self.UNKNOWN_PLAYER


# Legacy functions for backward compatibility (if needed)
def is_chat_message(log_line):
    """Legacy function - use LogMonitor._is_chat_message instead"""
    monitor = LogMonitor(None)
    return monitor._is_chat_message(log_line)

def extract_chat_message(log_line):
    """Legacy function - use LogMonitor._extract_chat_message instead"""
    monitor = LogMonitor(None)
    return monitor._extract_chat_message(log_line)

def extract_player_name_join(log_line):
    """Legacy function - use LogMonitor._extract_player_name_join instead"""
    monitor = LogMonitor(None)
    return monitor._extract_player_name_join(log_line)

def extract_player_name_leave(log_line):
    """Legacy function - use LogMonitor._extract_player_name_leave instead"""
    monitor = LogMonitor(None)
    return monitor._extract_player_name_leave(log_line)
