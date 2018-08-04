import asyncio
import discord

from discord.ext import commands

class BepisBotClient(commands.Bot):
    async def on_ready(self):
        print("Login successful.")
        print("User Name:  %s" % self.user.name)
        print("User ID:    %s" % self.user.id)

    async def on_message(self, message):
        await self.process_commands(message)
