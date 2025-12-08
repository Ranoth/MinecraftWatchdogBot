import logging
import discord
from discord.ext import commands as cmds


class CommandsCog(cmds.Cog):
    def __init__(self, bot, envvars, discord_bot):
        self.bot = bot
        self.envvars = envvars
        self.discord_bot = discord_bot

    @cmds.command(name="list", brief="Liste les joueurs connectés au serveur.")
    async def list_players(self, ctx):
        # Use the first container's rcon_client, or iterate through all
        if not self.discord_bot.containers:
            await ctx.send("Aucun serveur configuré.")
            return
        container = self.discord_bot.containers[0]
        players = await container.rcon_client.send_command_wrapper(command="list")
        await ctx.send(players)

    @cmds.command(
        name="whitelist", brief="Ajoute un joueur à la whitelist du serveur."
    )
    async def whitelist_player(self, ctx, player_name: str):
        if not self.discord_bot.containers:
            await ctx.send("Aucun serveur configuré.")
            return
        container = self.discord_bot.containers[0]
        result = await container.rcon_client.send_command_wrapper(
            command=f"whitelist add {player_name}"
        )
        await ctx.send(result)

    @cmds.command(name="status", brief="Obtient le statut du serveur.")
    async def get_server_status(self, ctx):
        if not self.discord_bot.containers:
            await ctx.send("Aucun serveur configuré.")
            return
        container = self.discord_bot.containers[0]
        status = await container.rcon_client.send_command_wrapper(command="tick query")
        await ctx.send(status)

    @cmds.command(name="help", brief="Affiche la liste des commandes disponibles.")
    async def help(self, ctx):
        """Affiche la liste des commandes disponibles."""
        embed = discord.Embed(
            title="🤖 Commandes disponnibles: ",
            color=0x00FF00,
        )

        for command in self.bot.commands:
            signature = f"!{command.qualified_name}"
            if command.signature:
                signature += f" {command.signature}"

            description = command.brief or command.help or "No description available"
            embed.add_field(name=signature, value=description, inline=False)

        await ctx.send(embed=embed)

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
        
    @cmds.command(name="chaussette", brief="Envoie une photo aléatoire de Chaussette.")
    async def chaussette(self, ctx):
        logging.info("Commande chaussette appelée") 
        path = self.envvars.chaussette
        if not path:
            await ctx.send("Chemin de photos de Chaussette non configuré.")
            return

        chaussette_photos = await self.get_photo_random(path)
        if not chaussette_photos:
            await ctx.send("Aucune photo trouvée pour Chaussette.")
            return

        await ctx.send(file=discord.File(chaussette_photos))