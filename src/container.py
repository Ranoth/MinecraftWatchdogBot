import logging
from docker_monitor import DockerMonitor
from log_monitor import LogMonitor
from rcon_client import RCONClient


class Container:
    def __init__(
        self,
        name,
        host,
        rcon_port=None,
        rcon_password=None,
        log_path=None,
        channel=None,
    ):
        self.name = name
        self.host = host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self.log_path = log_path
        self.channel = channel

        logging.debug(f"Initializing Container: {self.name} at {self.host}, log: {self.log_path}")

        self.docker_monitor = DockerMonitor(self.host, self.channel, self.name)
        self.log_monitor = LogMonitor(
            self.log_path, self.channel, self.docker_monitor, self.name
        )
        self.rcon_client = RCONClient(self.host, self.rcon_port, self.rcon_password)


    def start_monitors(self):
        import asyncio

        global log_monitor_task, docker_monitor_task

        self.log_monitor_task = asyncio.create_task(
            self.log_monitor.start_monitoring()
        )
        self.docker_monitor_task = asyncio.create_task(
            self.docker_monitor.start_monitoring()
        )

    @classmethod
    async def create(cls, *args, **kwargs):
        """Async factory: use await Container.create(...) instead of Container(...)"""
        inst = cls(*args, **kwargs)
        inst.start_monitors()
        return inst
