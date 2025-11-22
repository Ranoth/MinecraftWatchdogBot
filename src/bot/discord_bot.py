import logging
import discord
from discord.ext import commands

from bot.commands import CommandsCog
from bot.events import EventsCog
from container import Container


class DiscordBot:
    def __init__(self, envvars, container_configs):
        self.envvars = envvars
        self.container_configs = container_configs
        self.containers = []  # Will be populated in on_ready

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        self.bot.remove_command("help")

    async def initialize_containers(self):
        """Initialize containers after bot is ready"""
        logging.debug(f"Container configs: {self.container_configs}")
        for container_config in self.container_configs:
            logging.debug(f"Container : {container_config}")
            channel = await self.bot.fetch_channel(
                int(container_config.get("channel_id"))
            )
            container = await Container.create(
                name=container_config.get("name"),
                host=container_config.get("host"),
                rcon_port=container_config.get("rcon_port"),
                rcon_password=container_config.get("rcon_password"),
                channel=channel,
                log_path=container_config.get("log_path"),
            )
            self.containers.append(container)

    async def run(self):
        await self.bot.add_cog(
            EventsCog(self.bot, self.envvars, self)
        )
        await self.bot.add_cog(CommandsCog(self.bot, self.envvars, self))
        if self.envvars.discord_token is None:
            raise ValueError("DISCORD_TOKEN environment variable is not set")
        try:
            await self.bot.start(self.envvars.discord_token)
        finally:
            await self.bot.close()
