import asyncio
import discord
import traceback
import util

from discord.ext import commands
from discord.ext.commands import errors

from os.path import join as opj

class BepisBotClient(commands.Bot):
    JSON_PATH = "jsondata"

    async def on_ready(self):
        print("Login successful.")
        print("User Name:  %s" % self.user.name)
        print("User ID:    %s" % self.user.id)

    async def on_message(self, message):
        if message.guild != None:
            disabledCommands = util.load_js(opj(self.JSON_PATH, 
                        "%s-disabled-commands.json" % message.guild.id))
            for command in disabledCommands:
                if "%s%s" % (self.command_prefix, command) in \
                    message.content:
                    await message.channel.send("That command is disabled for " + 
                                    "use in this server.")
                    return

        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        eType = type(exception)
        if (eType == errors.MissingRequiredArgument or \
           eType == errors.BadArgument):
            if ctx.command.hidden:
                return

            helpList = await self.formatter.format_help_for(ctx, ctx.command)

            for helpStr in helpList:
                await ctx.send(helpStr)
        elif eType == errors.CommandNotFound:
            pass
        elif eType == errors.NoPrivateMessage:
            await ctx.author.send("Sorry, but I can't do that command in DMs.")
        else:
            eText = ""
            eList = traceback.format_exception(None, exception, None)
            for line in eList:
                eText += line
            await ctx.send("```%s```" % eText)