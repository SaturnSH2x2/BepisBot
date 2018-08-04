import asyncio
import discord
import util

from ctypes.util import find_library
from discord.ext import commands
from cogs.base import Base

class Music(Base):
    def __init__(self, bot):
        if discord.opus.is_loaded():
            pass
        else:
            discord.opus.load_opus(find_library("opus"))
            
        self.voice = None
        super().__init__(bot)
        
    # helper function to test if Opus is loaded
    async def _check_opus(self, ctx):
        if discord.opus.is_loaded():
            return True
        else:
            await ctx.send("The Opus Library is not loaded.  " + 
                "Voice commands are not available at this time.")
            return False

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel. You must be in VC for this to work."""
        util.nullifyExecute()
        if not self._check_opus(ctx):
            return
            
        # get the voice channel the user is currently in
        vChannel = ctx.message.guild.get_member(ctx.message.author.id).voice.channel
        if vChannel == None:
            await self.bot.say("You are not connected to a voice channel.  " + 
                "Connect first, then call this command.")
            return
            
        try:
            self.voice = await vChannel.connect()
            await ctx.say("Ready!")
        except discord.ClientException:
            await self.voice.move_to(vChannel)

    @commands.command()
    async def leave(self, ctx):
        """Disconnects from a voice channel. Does nothing if not connected."""
        if self.voice == None:
            await ctx.send("Not currently in a voice channel.")

        # failsafe to make sure that BepisBot isn't instructed
        # to leave a voice channel from an entirely different
        # server
        elif self.voice.channel not in \
                ctx.guild.voice_channels:
            await ctx.send("Not currently in a voice channel.")
        else:
            await self.voice.disconnect()
            await ctx.send("Left the voice channel.")
        
def setup(bot):
    bot.add_cog(Music(bot))
