import asyncio
import discord
import util

from discord.ext import commands
from cogs.base import Base

from os.path import join as opj

# Class for handling reactions to specific messages that aren't commands.
# Keeping them here makes them easier to manage, and having listeners is
# useful for preventing the "on_message" function from getting clogged up
# with code for each reaction.

class MessageReactions(Base):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.add_listener(self.noOneCaresListen, "on_message")
        self.bot.add_listener(self.fListen, "on_message")

    # simple helper function to check if the member has the 
    # "Manager Server" permission
    def checkPerms(self, ctx):
        if ctx.guild != None:
            perms = ctx.author.permissions_in(ctx.channel)
            if not perms.manage_guild:
                return False
        return True

    # listeners
    async def noOneCaresListen(self, message):
        if message.guild == None:
            key = "noonecares:%s" % message.author.id
        else:
            key = "noonecares:%s" % message.guild.id

        noOneCaresEnabled = await self.bot.rconn.get(key)
        if not noOneCaresEnabled or noOneCaresEnabled == "0":
            return

        if "no one cares" in message.content.lower() or \
            "ñô öñé çãrës" in message.content.lower() or \
            "nobody gives a shit" in message.content.lower() or \
            "nobody cares" in message.content.lower() or \
            "stfu" in message.content.lower():
            channel = message.channel
            await channel.send("oh wow %s that was kinda rude kys" % \
                            (message.author.mention))

    async def fListen(self, message):
        if message.guild == None:
            key = "f:%s" % message.author.id
        else:
            key = "f:%s" % message.guild.id

        fEnabled = await self.bot.rconn.get(key)
        if not fEnabled or fEnabled == "0":
            return

        if message.content.lower() == "f":
            channel = message.channel
            with open(opj("assets", "f.jpg"), "rb") as f:
                fFile = discord.File(f)
                await channel.send(file = fFile)

    # commands
    @commands.command()
    async def noOneCaresSet(self, ctx, enabled : bool):
        "Enable/Disable the \"no one cares\" reaction."
        if ctx.guild == None:
            key = "noonecares:%s" % ctx.author.id
        else:
            key = "noonecares:%s" % ctx.guild.id

        if ctx.guild != None and not self.checkPerms(ctx):
            await ctx.send("The \"Manage Guild\" permission is required to " +
                            "run this command.")
            return

        if enabled:
            enStr = "enabled"
            await self.bot.rconn.set(key, "1")
        else:
            enStr = "disabled"
            await self.bot.rconn.set(key, "0")

        await ctx.send("The \"no one cares\" reaction has been %s here." \
                        % (enStr))

    @commands.command()
    async def fSet(self, ctx, enabled : bool):
        "Enable/Disable the image reactions to \"F\"."
        if ctx.guild == None:
            key = "f:%s" % ctx.author.id
        else:
            key = "f:%s" % ctx.guild.id

        if ctx.guild != None and not self.checkPerms(ctx):
            await ctx.send("The \"Manage Guild\" permission is required to " +
                            "run this command.")
            return

        if enabled:
            enStr = "enabled"
            await self.bot.rconn.set(key, "1")
        else:
            enStr = "disabled"
            await self.bot.rconn.set(key, "0")

        await ctx.send("The \"F\" reaction has been %s here." % enStr)

def setup(bot):
    bot.add_cog(MessageReactions(bot))