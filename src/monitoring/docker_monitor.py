import asyncio
import logging
import docker
from docker.errors import DockerException
from concurrent.futures import ThreadPoolExecutor
from messager import Messager
from monitoring.turn_manager import TurnManager


class DockerMonitor:
    def __init__(
        self,
        container_name,
        channel,
        friendly_name,
        ready_event,
        messager: Messager,
    ):
        self.container_name = container_name
        self.channel = channel
        self.friendly_name = friendly_name
        self.ready_event = ready_event
        self.messager = messager
        self.client = None
        self.waiting_for_startup = False
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.loop = None
        self.turn_manager = None

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
                "Le serveur s'arrête.",
                description="",
                footer=self.friendly_name,
                color=0xFF0000,
                keep=True,
            )
            logging.info(f"Container {container_name} stopped")
            self.waiting_for_startup = False
            # Remove from turn rotation if it was in startup
            if self.turn_manager:
                TurnManager.remove_manager(self.turn_manager)
                logging.info(
                    f"Removed {self.friendly_name} from turn rotation on container stop"
                )
            # self.messager.clear_kept_messages()

        elif action == "start":
            await self.messager.send_embed(
                "Le serveur démarre.",
                footer=self.friendly_name,
                color=0xFFFF00,
                keep=True,
            )
            logging.info(f"Container {container_name} started")
            self.waiting_for_startup = True
            self.turn_manager = TurnManager()

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
