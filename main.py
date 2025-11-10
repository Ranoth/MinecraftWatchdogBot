import asyncio
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from rcon_client import RCONClient
from monitoring_client import monitor_server_logs, set_docker_monitor
from docker_monitor import DockerMonitor

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
rcon_host = os.getenv("RCON_HOST", "localhost")
rcon_port = int(os.getenv("RCON_PORT", 25575))
rcon_password = os.getenv("RCON_PASSWORD")
dev_mode = os.getenv("DEV", "false") == "true"

logging.basicConfig(
    level=logging.DEBUG if dev_mode else logging.INFO,
    handlers=[
        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w"),
    ],
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
)
discord_logger = logging.getLogger("discord")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
rcon_client = RCONClient(rcon_host, rcon_port, rcon_password, discord_logger)


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

        # Connect docker monitor to log monitor
        set_docker_monitor(docker_monitor)

        # Start log monitoring
        asyncio.create_task(monitor_server_logs(channel))

        # Start Docker event monitoring
        asyncio.create_task(docker_monitor.start_monitoring())
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
    try:
        response = await rcon_client.send_command(command)
        if response:
            if len(response) > 1900:
                response = response[:1900] + "\n...[truncated]"
            return f"\n{response}\n"
        else:
            discord_logger.error(f"Failed to execute RCON command: {command}")
            return "Failed to execute RCON command."
    except Exception as e:
        discord_logger.error(f"Error in rcon command: {e}")
        return "Error connecting to Minecraft server."


@bot.command()
async def list(ctx):
    """Liste les joueurs actuellement connectés au serveur."""
    await ctx.send(await send_command_wrapper(command="list"))


@bot.command()
async def whitelist(ctx, *, command: str):
    """Ajoute un ami à la whitelist du serveur."""
    await ctx.send(await send_command_wrapper(command=f"whitelist add {command}"))


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
