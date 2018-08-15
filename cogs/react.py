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

    def getReactPath(self, ctx : commands.Context = None, \
                            message : discord.Message = None):
        if ctx != None:
            if ctx.guild != None:
                return opj(self.JSON_PATH, "%s-react.json" % \
                                            ctx.guild.id)
            else:
                return opj(self.JSON_PATH, "%s-react.json" % \
                                            ctx.author.id)
        if message != None:
            if message.guild != None:
                return opj(self.JSON_PATH, "%s-react.json" % \
                                            message.guild.id)
            else:
                return opj(self.JSON_PATH, "%s-react.json" % \
                                            message.author.id)

    # listeners
    async def noOneCaresListen(self, message):
        reactDict = util.load_js(self.getReactPath(message = message))
        if "no-one-cares" not in reactDict.keys() or \
            not reactDict["no-one-cares"]:
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
        reactDict = util.load_js(self.getReactPath(message = message))
        if "f" not in reactDict.keys() or \
            not reactDict["f"]:
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
        path = self.getReactPath(ctx = ctx)

        reactDict = util.load_js(path)
        reactDict["no-one-cares"] = enabled
        util.save_js(path, reactDict)

        if enabled:
            enStr = "enabled"
        else:
            enStr = "disabled"

        await ctx.send("The \"no one cares\" reaction has been %s here." \
                        % (enStr))

    @commands.command()
    async def fSet(self, ctx, enabled : bool):
        "Enable/Disable the image reactions to \"F\"."
        path = self.getReactPath(ctx = ctx)

        reactDict = util.load_js(path)
        reactDict["f"] = enabled
        util.save_js(path, reactDict)

        if enabled:
            enStr = "enabled"
        else:
            enStr = "disabled"

        await ctx.send("The \"F\" reaction has been %s here." % enStr)

def setup(bot):
    bot.add_cog(MessageReactions(bot))