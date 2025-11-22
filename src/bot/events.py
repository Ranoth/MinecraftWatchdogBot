import logging

from discord.ext import commands


class EventsCog(commands.Cog):
    def __init__(self, bot, envvars, discord_bot):
        self.bot = bot
        self.envvars = envvars
        self.discord_bot = discord_bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}")
        logging.info("Bot is ready.")

        await self.discord_bot.initialize_containers()

        await self.bot.tree.sync()
        logging.info("Command tree synced.")

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)
