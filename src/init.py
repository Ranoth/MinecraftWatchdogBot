import logging
import os
import gzip
import shutil
from datetime import datetime
from logging.handlers import RotatingFileHandler

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

    # Rotate log file when it reaches 10MB, keep 5 backup files
    fh = RotatingFileHandler("/app/logs/discord.log", encoding="utf-8", mode="a", maxBytes=10*1024*1024, backupCount=1)
    
    # Compress rotated log files with gzip and add timestamp
    def namer(name: str) -> str:
        # Convert discord.log.1 to discord.log.YYYYMMDD_HHMMSS.gz
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = name.rsplit(".", 1)[0]  # Remove the rotation number
        return f"{base}.{timestamp}.gz"
    
    def rotator(source: str, dest: str) -> None:
        with open(source, "rb") as f_in, gzip.open(dest, "wb", compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(source)
    
    fh.namer = namer
    fh.rotator = rotator
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
