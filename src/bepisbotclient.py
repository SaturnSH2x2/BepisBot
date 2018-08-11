import asyncio
import discord
import traceback

from discord.ext import commands
from discord.ext.commands import errors

class BepisBotClient(commands.Bot):
    async def on_ready(self):
        print("Login successful.")
        print("User Name:  %s" % self.user.name)
        print("User ID:    %s" % self.user.id)

    async def on_message(self, message):
        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        eType = type(exception)
        if eType == errors.MissingRequiredArgument:
            helpList = await self.formatter.format_help_for(ctx, ctx.command)

            print(helpList)
            for helpStr in helpList:
                await ctx.send(helpStr)
        elif eType == errors.CommandNotFound:
            pass
        else:
            eText = ""
            eList = traceback.format_exception(None, exception, None)
            for line in eList:
                eText += line
            await ctx.send("```%s```" % eText)
            # raise exception