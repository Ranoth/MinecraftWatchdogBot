import asyncio
import json
import logging
import docker
from docker.errors import DockerException
import threading
from concurrent.futures import ThreadPoolExecutor


class DockerMonitor:
    def __init__(self, container_name, discord_channel):
        self.container_name = container_name
        self.channel = discord_channel
        self.client = None
        self.waiting_for_startup = False  # Flag to track if we're waiting for server ready
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.loop = None
        
    async def start_monitoring(self):
        """Start monitoring Docker events"""
        self.loop = asyncio.get_event_loop()
        
        # Run Docker monitoring in a separate thread to avoid blocking
        if self.loop:
            await self.loop.run_in_executor(self.executor, self._monitor_docker_events)
        
    def _monitor_docker_events(self):
        """Monitor Docker events in a separate thread"""
        while True:
            try:
                # Initialize Docker client using the socket
                self.client = docker.from_env()
                logging.info(f"Starting Docker event monitoring for {self.container_name}")
                
                # Listen for container events
                for event in self.client.events(decode=True, filters={
                    'container': self.container_name,
                    'event': ['start', 'die']
                }):
                    # Schedule the event handling in the main asyncio loop
                    if self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.handle_docker_event(event), 
                            self.loop
                        )
                    
            except DockerException as e:
                logging.error(f"Docker client error: {e}")
                import time
                time.sleep(5)  # Wait before retrying
            except Exception as e:
                logging.error(f"Docker monitoring error: {e}")
                import time
                time.sleep(5)  # Wait before retrying

    async def handle_docker_event(self, event):
        """Handle Docker container events"""
        action = event.get("Action", "")
        container_name = event.get("Actor", {}).get("Attributes", {}).get("name", "")

        if container_name != self.container_name:
            return

        if action == "die":
            await self.channel.send("🔴 **Le serveur Minecraft s'arrête...**")
            logging.info(f"Container {container_name} stopped")
            self.waiting_for_startup = False

        elif action == "start":
            await self.channel.send(
                "🟡 **Début de la séquence de démarrage du serveur...**"
            )
            logging.info(f"Container {container_name} started")
            self.waiting_for_startup = True  # Set flag for log monitor to pick up

    def notify_server_ready(self):
        """Called by log monitor when server is ready"""
        logging.info(f"notify_server_ready called - waiting_for_startup: {self.waiting_for_startup}")
        if self.waiting_for_startup:
            # Don't send message here since log monitor will send it anyway
            # Just update the flag
            self.waiting_for_startup = False
            logging.info("Server startup flag cleared (message sent by log monitor)")
        else:
            logging.info("Server ready notification skipped - not waiting for startup")
