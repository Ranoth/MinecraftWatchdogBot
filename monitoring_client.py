import asyncio
import aiofiles
from dotenv import load_dotenv
import os
import logging
import re

load_dotenv()
dev = os.getenv("DEV", "false") == "true"

# Global reference to docker monitor (will be set from main.py)
docker_monitor = None

def set_docker_monitor(monitor):
    """Set reference to docker monitor for communication"""
    global docker_monitor
    docker_monitor = monitor


async def monitor_server_logs(channel):
    """Monitor server logs and send alerts to Discord"""
    if dev:
        log_file = "./minecraftNewWorldData/logs/latest.log"
    else:
        log_file = "/data/latest.log"

    logging.info(f"Starting log monitoring for: {log_file}")

    while True:
        try:
            # Check if file exists
            if not os.path.exists(log_file):
                logging.warning(f"Log file {log_file} not found, waiting...")
                await asyncio.sleep(5)
                continue

            # Get initial file stats
            initial_stat = os.stat(log_file)
            current_position = 0

            async with aiofiles.open(log_file, mode="r") as f:
                # Move to end of existing content
                await f.seek(0, 2)
                current_position = await f.tell()
                logging.info(f"Started monitoring from position {current_position}")

                while True:
                    # Check if file still exists and hasn't been rotated
                    try:
                        current_stat = os.stat(log_file)

                        # Check if file was rotated (inode changed or size decreased)
                        if (
                            current_stat.st_ino != initial_stat.st_ino
                            or current_stat.st_size < current_position
                        ):
                            logging.info("Log file rotated, restarting monitoring...")
                            break

                    except FileNotFoundError:
                        logging.warning(
                            "Log file disappeared, restarting monitoring..."
                        )
                        break

                    line = await f.readline()
                    if line:
                        current_position = await f.tell()

                        # Check for important events
                        if "joined the game" in line:
                            player_name = extract_player_name_join(line)
                            await channel.send(f"🟢 **{player_name}** s'est connecté.")
                        elif "left the game" in line:
                            player_name = extract_player_name_leave(line)
                            await channel.send(
                                f"🔴 **{player_name}** s'est déconnecté."
                            )
                        elif is_chat_message(line):
                            player_name, message = extract_chat_message(line)
                            if player_name and message:
                                await channel.send(f"💬 **{player_name}**: {message}")
                        
                        # Check for server ready message
                        elif "Done (" in line and "For help, type" in line and "[Server thread/INFO]:" in line:
                            logging.info("Server startup complete detected from logs")
                            if docker_monitor:
                                await docker_monitor.notify_server_ready()

                        elif "WARN" in line or "ERROR" in line:
                            # await channel.send(f"⚠️ ```{line.strip()}```")
                            pass
                    else:
                        await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"Log monitoring error: {e}")
            await asyncio.sleep(5)  # Wait before retrying


def is_chat_message(log_line):
    """Check if the log line is a chat message"""
    try:
        # Look for chat message pattern: [timestamp] [Async Chat Thread - #X/INFO]: <PlayerName> message
        return (
            "<" in log_line
            and ">" in log_line
            and "Async Chat Thread" in log_line
            and "/INFO]:" in log_line
        )
    except:
        return False


def extract_chat_message(log_line):
    """Extract player name and message from chat log line"""
    try:
        # Format: [timestamp] [Async Chat Thread - #X/INFO]: <PlayerName> message
        pattern = r"\[.*?\] \[Async Chat Thread - #\d+/INFO\]: <(\w+)> (.*)"
        match = re.search(pattern, log_line.strip())

        if match:
            player_name = match.group(1)
            message = match.group(2)
            return player_name, message

        return None, None
    except Exception as e:
        logging.error(f"Error extracting chat message: {e}")
        return None, None


def extract_player_name_join(log_line):
    """Extract player name from join message"""
    try:
        # Format: [timestamp] [Server thread/INFO]: PlayerName joined the game
        parts = log_line.split(": ")
        if len(parts) >= 2:
            message = parts[1].strip()
            if " joined the game" in message:
                return message.replace(" joined the game", "")
        return "Unknown Player"
    except:
        return "Unknown Player"


def extract_player_name_leave(log_line):
    """Extract player name from leave message"""
    try:
        # Format: [timestamp] [Server thread/INFO]: PlayerName left the game
        parts = log_line.split(": ")
        if len(parts) >= 2:
            message = parts[1].strip()
            if " left the game" in message:
                return message.replace(" left the game", "")
        return "Unknown Player"
    except:
        return "Unknown Player"
