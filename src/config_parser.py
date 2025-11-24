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
            def __init__(self):
                self.discord_token = os.getenv("DISCORD_TOKEN")
                self.dev_mode = os.getenv("DEV", "false") == "true"
                self.log_update_interval = os.getenv("LOG_UPDATE_INTERVAL", 1)

                if self.discord_token == "" or self.discord_token is None:
                    raise ValueError("DISCORD_TOKEN environment variable is not set")

        return EnvConfig()

    def load_config(self):
        return self.containers
