import asyncio
import logging
from init import init
from app import App


async def main():
    try:
        envvars, container_configs = init()

        logging.info("Starting Discord Bot...")
        app = App(envvars, container_configs)

        await app.run_discord_bot()
    except ValueError as e:
        logging.error(f"Initialization error: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
