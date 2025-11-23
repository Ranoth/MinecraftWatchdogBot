import logging
import asyncio

from monitoring.docker_monitor import DockerMonitor
from monitoring.log_monitor import LogMonitor
from rcon_client import RCONClient
from messager import Messager

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
        self.log_monitors_ready = asyncio.Event()
        self.docker_monitors_ready = asyncio.Event()

        logging.debug(
            f"Initializing Container: {self.name} at {self.host}, log: {self.log_path}"
        )
        
        self.messager = Messager(self.channel)

        self.docker_monitor = DockerMonitor(
            self.host, self.channel, self.name, self.docker_monitors_ready, self.messager
        )
        self.log_monitor = LogMonitor(
            self.log_path,
            self.channel,
            self.docker_monitor,
            self.name,
            self.host,
            self.log_monitors_ready,
            self.messager
        )
        self.rcon_client = RCONClient(self.host, self.rcon_port, self.rcon_password)

    def start_monitors(self):
        global log_monitor_task, docker_monitor_task

        self.log_monitor_task = asyncio.create_task(self.log_monitor.start_monitoring())
        self.docker_monitor_task = asyncio.create_task(
            self.docker_monitor.start_monitoring()
        )

    async def wait_until_ready(self):
        """Wait until monitors signal they're ready"""
        await asyncio.gather(
            self.log_monitors_ready.wait(), self.docker_monitors_ready.wait()
        )

    @classmethod
    def create(cls, *args, **kwargs):
        """Factory: creates and starts monitors, but doesn't wait for ready"""
        inst = cls(*args, **kwargs)
        inst.start_monitors()
        return inst
