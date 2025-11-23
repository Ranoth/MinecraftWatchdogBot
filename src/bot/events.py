import logging

from discord.ext import commands

import asyncio


class EventsCog(commands.Cog):
    def __init__(self, bot, envvars, discord_bot, health_check):
        self.bot = bot
        self.envvars = envvars
        self.discord_bot = discord_bot
        self.health_check = health_check

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}")
        logging.info("Bot is ready.")

        await asyncio.gather(self.discord_bot.initialize_containers())

        self.health_check.ready = True

        await self.bot.tree.sync()
        logging.info("Command tree synced.")

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)
