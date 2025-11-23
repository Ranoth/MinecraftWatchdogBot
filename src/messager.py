import discord


class Messager:

    def __init__(self, channel):
        self.channel = channel
        self.kept_messages = []

    async def send_embed(
        self, title="", description="", footer="", color=0x0000FF, keep=False
    ):
        """Send an embed message to a Discord channel or modify the last kept message."""
        if keep and self.kept_messages:
            last_message = self.kept_messages[-1]
            embed = self.modify_embed(
                last_message.embeds[0],
                title=title,
                description=description,
                footer=footer,
                color=color,
            )
            await last_message.edit(embed=embed)
            return

        embed = discord.Embed(
            color=color,
            title=title,
            description=description,
        )
        embed.set_footer(text=footer)
        message = await self.channel.send(embed=embed)
        if keep:
            self.kept_messages.append(message)

    async def send_message(self, text):
        """Send a text message to a Discord channel."""
        await self.channel.send(text)

    def clear_kept_messages(self):
        """Clear the list of kept messages."""
        self.kept_messages = []

    def modify_embed(self, embed, title="", description="", footer="", color=0x0000FF):
        """Modify an existing embed with new values."""
        if title != "":
            embed.title = title
        if description != "":
            embed.description = description
        if footer != "":
            embed.set_footer(text=footer)
        if color != 0x0000FF:
            embed.color = color
        return embed

    async def modify_message(self, message, new_content):
        """Modify the content of an existing text message."""
        await message.edit(content=new_content)
        return message
