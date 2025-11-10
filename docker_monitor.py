import asyncio
import json
import logging

class DockerMonitor:
    def __init__(self, container_name, discord_channel):
        self.container_name = container_name
        self.channel = discord_channel
        self.process = None
        self.waiting_for_startup = False  # Flag to track if we're waiting for server ready
        
    async def start_monitoring(self):
        """Start monitoring Docker events"""
        logging.info(f"Starting Docker event monitoring for {self.container_name}")
        
        while True:
            try:
                # Start docker events process
                self.process = await asyncio.create_subprocess_exec(
                    'docker', 'events', '--filter', 'event=start', '--filter', 'event=die',
                    '--filter', f'container={self.container_name}', '--format', '{{json .}}',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                async for line in self.process.stdout:
                    try:
                        event = json.loads(line.decode())
                        await self.handle_docker_event(event)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse Docker event: {e}")
                        
            except Exception as e:
                logging.error(f"Docker monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def handle_docker_event(self, event):
        """Handle Docker container events"""
        action = event.get('Action', '')
        container_name = event.get('Actor', {}).get('Attributes', {}).get('name', '')
        
        if container_name != self.container_name:
            return
            
        if action == 'die':
            await self.channel.send("🔴 **Le serveur Minecraft s'arrête...**")
            logging.info(f"Container {container_name} stopped")
            self.waiting_for_startup = False
            
        elif action == 'start':
            await self.channel.send("🟡 **Début de la séquence de démarrage du serveur...**")
            logging.info(f"Container {container_name} started")
            self.waiting_for_startup = True  # Set flag for log monitor to pick up
            
    async def notify_server_ready(self):
        """Called by log monitor when server is ready"""
        if self.waiting_for_startup:
            await self.channel.send("🟢 **Le serveur Minecraft est prêt !**")
            self.waiting_for_startup = False
            logging.info("Server startup complete notification sent")