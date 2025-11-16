import asyncio
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from rcon_client import RCONClient
from monitoring_client import LogMonitor
from docker_monitor import DockerMonitor

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
rcon_host = os.getenv("RCON_HOST", "localhost")
rcon_port = int(os.getenv("RCON_PORT", 25575))
rcon_password = os.getenv("RCON_PASSWORD")
dev_mode = os.getenv("DEV", "false") == "true"

# Ensure the data directory exists
os.makedirs("/app/data", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG if dev_mode else logging.INFO,
    handlers=[
        logging.FileHandler(filename="/app/data/discord.log", encoding="utf-8", mode="w"),
    ],
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
)
discord_logger = logging.getLogger("discord")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
rcon_client = RCONClient(rcon_host, rcon_port, rcon_password)

# Global variable to store task references
log_monitor_task = None
docker_monitor_task = None


@bot.event
async def on_ready():
    discord_logger.setLevel(logging.INFO)
    discord_logger.info(f"Logged in as {bot.user}")
    discord_logger.info("Bot is ready.")
    await bot.tree.sync()
    discord_logger.info("Command tree synced.")

    channel_id = int(os.getenv("CHANNEL_ID") or 0)
    channel = bot.get_channel(channel_id)

    if channel:
        # Create docker monitor
        docker_monitor = DockerMonitor("minecraftNewWorld", channel)

        # Create log monitor and connect it to docker monitor
        log_monitor = LogMonitor(channel, docker_monitor)

        # Start log monitoring - keep reference to prevent garbage collection
        global log_monitor_task, docker_monitor_task
        log_monitor_task = asyncio.create_task(log_monitor.start_monitoring())

        # Start Docker event monitoring - keep reference to prevent garbage collection
        docker_monitor_task = asyncio.create_task(docker_monitor.start_monitoring())
    else:
        discord_logger.error(f"Channel with ID {channel_id} not found")


@bot.event
async def on_message(message):
    # Only process commands in the designated channel
    channel_id = int(os.getenv("CHANNEL_ID") or 0)
    if message.channel.id == channel_id:
        await bot.process_commands(message)
    # If it's not the right channel, just ignore the message


async def send_command_wrapper(*, command: str):
    response = await rcon_client.send_command(command)

    # Check if response is an error message (starts with ❌)
    if response.startswith("❌"):
        return response  # Return error message as-is

    # Clean up the response and add proper line breaks
    cleaned_response = response.strip()

    # Generic approach: Add line breaks after sentences and common patterns
    import re

    # Split on periods followed by capital letters (sentence boundaries)
    cleaned_response = re.sub(r"\.(\s*)([A-Z])", r".\n\2", cleaned_response)

    # Split on colons followed by numbers or text (data labels)
    cleaned_response = re.sub(r":(\s*)([0-9A-Za-z])", r":\n\2", cleaned_response)

    # Clean up excessive whitespace and newlines
    cleaned_response = re.sub(
        r"\s+", " ", cleaned_response
    )  # Multiple spaces to single
    cleaned_response = re.sub(
        r" *\n *", "\n", cleaned_response
    )  # Clean around newlines
    cleaned_response = re.sub(
        r"\n{3,}", "\n\n", cleaned_response
    )  # Max 2 consecutive newlines

    if len(cleaned_response) > 1900:
        cleaned_response = cleaned_response[:1900] + "\n...[truncated]"
    return f"\n{cleaned_response}\n"


@bot.command()
async def list(ctx):
    """Liste les joueurs actuellement connectés au serveur."""
    await ctx.send(await send_command_wrapper(command="list"))


@bot.command()
async def whitelist(ctx, *, nom: str):
    """Ajoute un ami à la whitelist du serveur."""
    await ctx.send(await send_command_wrapper(command=f"whitelist add {nom}"))


@bot.command()
async def status(ctx):
    """Affiche le statut du serveur Minecraft."""
    await ctx.send(await send_command_wrapper(command="tick query"))


# Remove the default help command
bot.remove_command("help")


@bot.command(brief="Affiche la liste des commandes disponibles.")
async def help(ctx):
    """Affiche la liste des commandes disponibles."""
    embed = discord.Embed(
        title="🤖 Commandes disponnibles: ",
        color=0x00FF00,
    )

    for command in bot.commands:
        signature = f"!{command.qualified_name}"
        if command.signature:
            signature += f" {command.signature}"

        description = command.brief or command.help or "No description available"
        embed.add_field(name=signature, value=description, inline=False)

    await ctx.send(embed=embed)


if discord_token is None:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

bot.run(discord_token)
