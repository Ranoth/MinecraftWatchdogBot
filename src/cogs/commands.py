import logging
import discord
import docker
import docker.errors
from discord.ext import commands
from discord import app_commands


def requires_container():
    """Check if containers are configured before running a command."""

    async def predicate(interaction: discord.Interaction) -> bool:
        cog = interaction.client.get_cog("CommandsCog")  # type: ignore
        if not cog or not cog.app.containers:
            await interaction.response.send_message(
                "Aucun serveur configuré.", ephemeral=True
            )
            return False
        return True

    return app_commands.check(predicate)


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._set_guild_for_commands()

    @property
    def app(self):
        return self.bot.app

    @property
    def envvars(self):
        return self.bot.envvars

    def _set_guild_for_commands(self):
        """Set the guild ID for all app commands based on envvars."""
        if self.envvars.guild_id:
            guild = discord.Object(id=int(self.envvars.guild_id))
            for command in self.get_app_commands():
                if hasattr(command, "_guild_ids"):
                    command._guild_ids = [guild.id]

    def get_container_by_name(self, server_name: str):
        """Helper to get a container by its name."""
        for container in self.app.containers:
            if container.name == server_name:
                return container
        return None

    async def server_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for server selection - shows available servers."""
        if not self.app.containers:
            return []
        return [
            app_commands.Choice(name=container.name, value=container.name)
            for container in self.app.containers
            if current.lower() in container.name.lower()
        ]

    async def locate_target_type_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for locate command target type selection - show available types."""
        options = ["structure", "biome", "poi"]
        return [
            app_commands.Choice(name=option, value=option)
            for option in options
            if current.lower() in option.lower()
        ]

    async def player_name_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for player name selection - shows online players."""
        # Namespace is an object, not a dict; access attributes safely.
        server_name = getattr(interaction.namespace, "server", None)
        container = self.get_container_by_name(server_name)  # type: ignore
        if not container:
            return []
        players_response = await container.rcon_client.send_command_wrapper(
            command="list"
        )
        # Extract player names from the response (assuming format "There are X of a max Y players online: player1, player2, ...")
        if ":" in players_response:
            players_list = players_response.split(":")[1].strip().split(", ")
            return [
                app_commands.Choice(name=player, value=player)
                for player in players_list
                if current.lower() in player.lower()
            ]
        return []

    @app_commands.command(
        name="list", description="Liste les joueurs connectés au serveur."
    )
    @app_commands.autocomplete(server=server_autocomplete)
    @requires_container()
    async def list_players(self, interaction: discord.Interaction, server: str):
        """Liste les joueurs connectés au serveur."""
        container = self.get_container_by_name(server)
        if not container:
            await interaction.response.send_message(
                f"Serveur '{server}' introuvable.", ephemeral=True
            )
            return
        players = await container.rcon_client.send_command_wrapper(command="list")
        await interaction.response.send_message(players)

    @app_commands.command(
        name="whitelist", description="Ajoute un joueur à la whitelist du serveur."
    )
    @app_commands.autocomplete(server=server_autocomplete)
    @requires_container()
    async def whitelist_player(
        self, interaction: discord.Interaction, server: str, player_name: str
    ):
        """Ajoute un joueur à la whitelist du serveur."""
        container = self.get_container_by_name(server)
        if not container:
            await interaction.response.send_message(
                f"Serveur '{server}' introuvable.", ephemeral=True
            )
            return
        result = await container.rcon_client.send_command_wrapper(
            command=f"whitelist add {player_name}"
        )
        await interaction.response.send_message(result)

    @app_commands.command(name="status", description="Obtient le statut du serveur.")
    @app_commands.autocomplete(server=server_autocomplete)
    @requires_container()
    async def get_server_status(self, interaction: discord.Interaction, server: str):
        """Obtient le statut du serveur."""
        container = self.get_container_by_name(server)
        if not container:
            await interaction.response.send_message(
                f"Serveur '{server}' introuvable.", ephemeral=True
            )
            return
        status = await container.rcon_client.send_command_wrapper(command="tick query")
        await interaction.response.send_message(status)

    async def get_photo_random(self, path_to_file):
        import os
        import random

        files = [
            f
            for f in os.listdir(path_to_file)
            if os.path.isfile(os.path.join(path_to_file, f))
        ]
        if not files:
            return None
        selected_file = random.choice(files)
        return os.path.join(path_to_file, selected_file)

    @app_commands.command(
        name="locate", description="Localise un joueur sur la carte du serveur."
    )
    @app_commands.autocomplete(
        server=server_autocomplete, target_type=locate_target_type_autocomplete
    )
    @requires_container()
    async def locate(
        self,
        interaction: discord.Interaction,
        server: str,
        target_type: str,
        target: str,
    ):
        """Localise une structure, un biome ou un point d'intérêt"""
        container = self.get_container_by_name(server)
        if not container:
            await interaction.response.send_message(
                f"Serveur '{server}' introuvable.", ephemeral=True
            )
            return

        # Defer response since locate can take a long time
        await interaction.response.defer()

        result = await container.rcon_client.send_command_wrapper(
            command=f"locate {target_type} {target}"
        )
        await interaction.followup.send(result)

    @app_commands.command(
        name="tp",
        description="Téléporte une entitée à des coordonnées spécifiques ou une autre entitée.",
    )
    @app_commands.autocomplete(server=server_autocomplete)
    @requires_container()
    async def tp(
        self, interaction: discord.Interaction, server: str, target: str, location: str
    ):
        """Téléporte une entitée à des coordonnées spécifiques ou une autre entitée."""
        container = self.get_container_by_name(server)
        if not container:
            await interaction.response.send_message(
                f"Serveur '{server}' introuvable.", ephemeral=True
            )
            return
        result = await container.rcon_client.send_command_wrapper(
            command=f"tp {target} {location}"
        )
        await interaction.response.send_message(result)

    @app_commands.command(name="restart", description="Redémarre le serveur Minecraft")
    @app_commands.autocomplete(server=server_autocomplete)
    @requires_container()
    async def restart_minecraft_server_container(
        self, interaction: discord.Interaction, server: str
    ):
        """Redémarre le serveur Minecraft."""
        container = self.get_container_by_name(server)
        if not container:
            await interaction.response.send_message(
                f"Serveur '{server}' introuvable.", ephemeral=True
            )
            return

        client = docker.from_env()
        try:
            docker_container = client.containers.get(container.host)
            docker_container.restart()
        except docker.errors.NotFound:
            await interaction.response.send_message(
                f"Conteneur Docker pour le serveur '{server}' introuvable."
            )
            return
        except docker.errors.APIError as e:
            await interaction.response.send_message(
                f"Erreur lors du redémarrage du serveur '{server}': {e}"
            )
            return
        await interaction.response.send_message("Redémarrage du serveur...")

    @app_commands.command(
        name="chaussette", description="Envoie une photo aléatoire de Chaussette."
    )
    async def chaussette(self, interaction: discord.Interaction):
        """Envoie une photo aléatoire de Chaussette."""
        path = self.envvars.chaussette
        if not path:
            await interaction.response.send_message(
                "Chemin de photos de Chaussette non configuré."
            )
            return

        chaussette_photos = await self.get_photo_random(path)
        if not chaussette_photos:
            await interaction.response.send_message(
                "Aucune photo trouvée pour Chaussette."
            )
            return

        await interaction.response.send_message(file=discord.File(chaussette_photos))

    @app_commands.command(name="help", description="Affiche l'aide pour les commandes disponibles.")
    async def help(self, interaction: discord.Interaction):
        """Affiche l'aide pour les commandes disponibles."""
        embed = discord.Embed(
            title="📖 Commandes Disponibles",
            description="Voici la liste de toutes les commandes disponibles :",
            color=discord.Color.blue()
        )
        
        for command in self.get_app_commands():
            params = []
            for param in command.parameters: # type: ignore
                if param.required:
                    params.append(f"<{param.name}>")
                else:
                    params.append(f"[{param.name}]")
            
            if params:
                command_usage = f"`/{command.name} {' '.join(params)}`"
            else:
                command_usage = f"`/{command.name}`"
            
            embed.add_field(
                name=command_usage,
                value=command.description or "Pas de description disponible.",
                inline=False
            )
        
        embed.set_footer(text="<> = requis | [] = optionnel")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
async def setup(bot):
    """Load the CommandsCog into the bot."""
    await bot.add_cog(CommandsCog(bot))
