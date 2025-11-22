import logging
import os
import yaml


class ConfigParser:
    def __init__(self):
        with open("/app/config/config.yaml", "r") as file:
            containers = yaml.safe_load(file)
            self.containers = containers.get("containers", [])
            logging.debug(f"Loaded containers from config: {self.containers}")

    @staticmethod
    def load_env():
        class EnvConfig:
            discord_token = os.getenv("DISCORD_TOKEN")
            host = os.getenv("HOST", "localhost")
            rcon_port = int(os.getenv("RCON_PORT", 25575))
            rcon_password = os.getenv("RCON_PASSWORD")
            dev_mode = os.getenv("DEV", "false") == "true"

        return EnvConfig

    def load_config(self):
        return self.containers