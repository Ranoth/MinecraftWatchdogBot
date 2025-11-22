import logging
import os

from config_parser import ConfigParser


def init():
    envvars = ConfigParser().load_env()
    container_configs = ConfigParser().load_config()

    os.makedirs("/app/logs", exist_ok=True)
    os.makedirs("/app/config", exist_ok=True)
    os.makedirs("/app/monitoring", exist_ok=True)

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    root_level = logging.DEBUG if envvars.dev_mode else logging.INFO
    root.setLevel(root_level)

    fmt = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")

    fh = logging.FileHandler("/app/logs/discord.log", encoding="utf-8", mode="a")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(sh)

    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(root_level)
    discord_logger.propagate = True

    aiohttp_logger = logging.getLogger("aiohttp.access")
    aiohttp_logger.setLevel(logging.DEBUG if envvars.dev_mode else logging.WARNING)

    if envvars.discord_token is None:
        raise ValueError("DISCORD_TOKEN environment variable is not set")

    return envvars, container_configs
