import logging
import discord
from discord.ext import commands
import asyncio

from bot.commands import CommandsCog
from bot.events import EventsCog
from container import Container
from health_check import HealthCheck


class DiscordBot:
    def __init__(self, envvars, container_configs):
        self.envvars = envvars
        self.container_configs = container_configs
        self.containers = []

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        self.bot.remove_command("help")

    async def initialize_containers(self):
        """Initialize containers after bot is ready"""
        logging.debug(f"Container configs: {self.container_configs}")
        
        # Create all containers concurrently (without waiting)
        for container_config in self.container_configs:
            logging.debug(f"Container : {container_config}")
            channel = await self.bot.fetch_channel(
                int(container_config.get("channel_id"))
            )
            container = Container.create(
                envvars = self.envvars,
                name=container_config.get("name"),
                host=container_config.get("host"),
                rcon_port=container_config.get("rcon_port"),
                rcon_password=container_config.get("rcon_password"),
                channel=channel,
                log_path=container_config.get("log_path"),
            )
            self.containers.append(container)
        
        # Wait for all containers to be ready concurrently
        await asyncio.gather(*[container.wait_until_ready() for container in self.containers])
        logging.info("All containers ready")
        
        return self.containers

    async def run(self):
        """Run the Discord bot"""
        health_check = HealthCheck()
        await health_check.start_server()
        
        await self.bot.add_cog(EventsCog(self.bot, self.envvars, self, health_check))
        await self.bot.add_cog(CommandsCog(self.bot, self.envvars, self))

        try:
            await self.bot.start(self.envvars.discord_token)
        finally:
            await self.bot.close()
