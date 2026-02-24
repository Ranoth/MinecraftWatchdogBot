import logging

import discord
from discord.ext import commands

import asyncio


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = discord.Object(id=int(self.bot.envvars.guild_id))

    @property
    def app(self):
        return self.bot.app

    @property
    def envvars(self):
        return self.bot.envvars

    @property
    def health_check(self):
        return self.bot.health_check

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}")
        logging.info("Bot is ready")

        await self.app.initialize_containers()

        self.health_check.ready = True

        try:
            logging.info(f"Syncing commands to guild {self.guild.id}...")
            synced = await self.bot.tree.sync(guild=self.guild)
            logging.info(
                f"Guild command tree synced. {len(synced)} commands registered"
            )
            
            if self.envvars.dev_mode:
                logging.info("Clearing global command tree...")
                await self.bot.tree.sync()
                logging.info("Global command tree cleared")
        except Exception as e:
            logging.error(f"Failed to sync command tree: {e}")


async def setup(bot):
    """Load the EventsCog into the bot."""
    await bot.add_cog(EventsCog(bot))
