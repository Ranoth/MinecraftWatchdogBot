import discord
from discord.ext import commands
from rcon_client import RCONClient


class CommandsCog(commands.Cog):
    def __init__(self, bot, rcon_client: RCONClient):
        self.rcon_client = rcon_client
        self.bot = bot
    @commands.command(name="list", brief="Liste les joueurs connectés au serveur.")
    async def list_players(self, ctx):
        players = await self.rcon_client.send_command_wrapper(command="list")
        await ctx.send(players)

    @commands.command(name="whitelist", brief="Ajoute un joueur à la whitelist du serveur.")
    async def whitelist_player(self, ctx, player_name: str):
        result = await self.rcon_client.send_command_wrapper(
            command=f"whitelist add {player_name}"
        )
        await ctx.send(result)

    @commands.command(name="status", brief="Obtient le statut du serveur.")
    async def get_server_status(self, ctx):
        status = await self.rcon_client.send_command_wrapper(command="tick query")
        await ctx.send(status)

    @commands.command(name="help", brief="Affiche la liste des commandes disponibles.")
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
