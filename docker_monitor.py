import asyncio
import json
import logging
import docker
from docker.errors import DockerException


class DockerMonitor:
    def __init__(self, container_name, discord_channel):
        self.container_name = container_name
        self.channel = discord_channel
        self.client = None
        self.waiting_for_startup = False  # Flag to track if we're waiting for server ready
        
    async def start_monitoring(self):
        """Start monitoring Docker events"""
        while True:
            try:
                # Initialize Docker client using the socket
                self.client = docker.from_env()
                logging.info(f"Starting Docker event monitoring for {self.container_name}")
                
                # Listen for container events in a loop
                for event in self.client.events(decode=True, filters={
                    'container': self.container_name,
                    'event': ['start', 'die']
                }):
                    await self.handle_docker_event(event)
                    
            except DockerException as e:
                logging.error(f"Docker client error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                logging.error(f"Docker monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

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

    async def notify_server_ready(self):
        """Called by log monitor when server is ready"""
        logging.info(f"notify_server_ready called - waiting_for_startup: {self.waiting_for_startup}")
        if self.waiting_for_startup:
            # Don't send message here since log monitor will send it anyway
            # Just update the flag
            self.waiting_for_startup = False
            logging.info("Server startup flag cleared (message sent by log monitor)")
        else:
            logging.info("Server ready notification skipped - not waiting for startup")
