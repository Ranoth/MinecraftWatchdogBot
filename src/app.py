import logging
import discord
from discord.ext import commands
import asyncio
from typing import Optional

from container import Container
from health_check import HealthCheck


class AppBot(commands.Bot):
    """Custom Bot class with app dependencies"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app: Optional["App"] = None
        self.envvars = None
        self.health_check: Optional[HealthCheck] = None


class App:
    def __init__(self, envvars, container_configs):
        self.envvars = envvars
        self.container_configs = container_configs
        self.containers = []

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = AppBot(command_prefix="!", intents=intents)

        self.bot.remove_command("help")

    async def initialize_containers(self):
        """Initialize containers after bot is ready"""
        logging.debug(f"Container configs: {self.container_configs}")

        for container_config in self.container_configs:
            logging.debug(f"Container : {container_config}")
            channel = await self.bot.fetch_channel(
                int(container_config.get("channel_id"))
            )
            container = Container.create(
                envvars=self.envvars,
                name=container_config.get("name"),
                host=container_config.get("host"),
                rcon_port=container_config.get("rcon_port"),
                rcon_password=container_config.get("rcon_password"),
                channel=channel,
                log_path=container_config.get("log_path"),
            )
            self.containers.append(container)

        await asyncio.gather(
            *[container.wait_until_ready() for container in self.containers]
        )
        logging.info("All containers ready")

        return self.containers

    async def run_discord_bot(self):
        """Run the Discord bot"""
        health_check = HealthCheck()
        await health_check.start_server()

        self.bot.app = self
        self.bot.envvars = self.envvars
        self.bot.health_check = health_check

        await self.bot.load_extension("cogs.events")
        await self.bot.load_extension("cogs.commands")

        try:
            await self.bot.start(self.envvars.discord_token)
        finally:
            await self.bot.close()
