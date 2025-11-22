import logging

from discord.ext import commands
from container import Container


class EventsCog(commands.Cog):
    def __init__(self, bot, envvars, container_configs):
        self.bot = bot
        self.envvars = envvars
        self.container_configs = container_configs

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}")
        logging.info("Bot is ready.")

        logging.debug(f"Container configs: {self.container_configs}")
        for container in self.container_configs:
            logging.debug(f"Container : {container}")
            channel = await self.bot.fetch_channel(
                int(container.get("channel_id"))
            )
            await Container.create(
                name=container.get("name"),
                host=container.get("host"),
                rcon_port=container.get("rcon_port"),
                rcon_password=container.get("rcon_password"),
                channel=channel,
                log_path=container.get("log_path"),
            )

        await self.bot.tree.sync()
        logging.info("Command tree synced.")

    @commands.Cog.listener()
    async def on_message(self, message):
        channel_id = int(self.envvars.channel_id or 0)
        if message.channel.id == channel_id:
            await self.bot.process_commands(message)
