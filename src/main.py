import asyncio
import logging
from init import init
from bot.discord_bot import DiscordBot


async def main():
    try:
        envvars, container_configs = init()

        logging.info("Starting Discord Bot...")
        bot = DiscordBot(envvars, container_configs)

        await bot.run()
    except ValueError as e:
        logging.error(f"Initialization error: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
