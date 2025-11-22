import discord
from discord.ext import commands

from bot.commands import CommandsCog
from bot.events import EventsCog


class DiscordBot:
    def __init__(self, envvars, container_configs):
        self.envvars = envvars
        self.container_configs = container_configs

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        self.bot.remove_command("help")

    async def run(self):
        await self.bot.add_cog(
            EventsCog(self.bot, self.envvars, self.container_configs)
        )
        await self.bot.add_cog(CommandsCog(self.bot, self.envvars))
        if self.envvars.discord_token is None:
            raise ValueError("DISCORD_TOKEN environment variable is not set")
        try:
            await self.bot.start(self.envvars.discord_token)
        finally:
            await self.bot.close()
