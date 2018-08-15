import asyncio
import discord

from discord.ext import commands
from cogs.base import Base

class MessageReactions(Base):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.add_listener(self.noOneCaresListen, "on_message")

    # listeners
    async def noOneCaresListen(self, message):
        if "no one cares" in message.content.lower():
            channel = message.channel
            await channel.send("oh wow %s that was kinda rude kys" % \
                            (message.author.mention))

    # commands
    @commands.command()

def setup(bot):
    bot.add_cog(MessageReactions(bot))