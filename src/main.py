import asyncio
from init import init
from bot.discord_bot import DiscordBot

async def main():
	envvars, container_configs = init()

	print("Starting Discord Bot...")
	bot = DiscordBot(envvars, container_configs)

	await bot.run()

if __name__ == "__main__":
	asyncio.run(main())