import asyncio
import logging
import docker
from docker.errors import DockerException
from concurrent.futures import ThreadPoolExecutor
from messager import Messager


class DockerMonitor:
    def __init__(
        self,
        container_name,
        discord_channel,
        friendly_name,
        ready_event,
        messager: Messager,
    ):
        self.container_name = container_name
        self.channel = discord_channel
        self.friendly_name = friendly_name
        self.client = None
        self.waiting_for_startup = False
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.loop = None
        self.ready_event = ready_event
        self.messager = messager

    async def start_monitoring(self):
        """Start monitoring Docker events"""
        self.loop = asyncio.get_event_loop()

        if self.loop:
            await self.loop.run_in_executor(self.executor, self._monitor_docker_events)

    def _monitor_docker_events(self):
        """Monitor Docker events in a separate thread"""
        while True:
            try:
                self.client = docker.from_env()
                logging.info(
                    f"Starting Docker event monitoring for {self.container_name}"
                )
                if self.ready_event:
                    self.ready_event.set()

                for event in self.client.events(
                    decode=True,
                    filters={
                        "container": self.container_name,
                        "event": ["start", "die"],
                    },
                ):
                    if self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.handle_docker_event(event), self.loop
                        )

            except DockerException as e:
                logging.error(f"Docker client error: {e}")
                import time

            except Exception as e:
                logging.error(f"Docker monitoring error: {e}")
                import time

    async def handle_docker_event(self, event):
        """Handle Docker container events"""
        action = event.get("Action", "")
        container_name = event.get("Actor", {}).get("Attributes", {}).get("name", "")

        if container_name != self.container_name:
            return

        if action == "die":
            await self.messager.send_embed(
                "Le serveur s'arrête.", footer=self.friendly_name, color=0xFF0000
            )
            logging.info(f"Container {container_name} stopped")
            self.waiting_for_startup = False
            self.messager.clear_kept_messages()

        elif action == "start":
            await self.messager.send_embed(
                "Le serveur démarre.",
                footer=self.friendly_name,
                color=0xFFFF00,
                keep=True,
            )
            logging.info(f"Container {container_name} started")
            self.waiting_for_startup = True

    def notify_server_ready(self):
        """Called by log monitor when server is ready"""
        logging.info(
            f"notify_server_ready called - waiting_for_startup: {self.waiting_for_startup}"
        )
        if self.waiting_for_startup:
            self.waiting_for_startup = False
            logging.info("Server startup flag cleared (message sent by log monitor)")
        else:
            logging.info("Server ready notification skipped - not waiting for startup")
