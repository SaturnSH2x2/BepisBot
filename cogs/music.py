import asyncio
import discord
import time
import io
import os
import multiprocessing as mp
import youtube_dl
import util

from ctypes.util import find_library
from discord.ext import commands
from cogs.base import Base
from os.path import join as opj

# function to download YouTube videos to stream as needed.
# Run as a separate process.
def downloadVideo(ytLink : str, filename : str):
    opts = {
        "outtmpl" : filename,
        "postprocessors" : [{
            "key" : "FFmpegExtractAudio",
            "preferredcodec" : "opus",
            "preferredquality" : "192",
        }]
    }
    
    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([ytLink])

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
        vChannel = ctx.message.author.voice.channel
        if vChannel == None:
            await self.bot.say("You are not connected to a voice channel.  " + 
                "Connect first, then call this command.")
            return
            
        # connect to a voice channel. If bot is in another voice channel, switch
        # to the channel specified.
        try:
            self.voice = await vChannel.connect()
        except discord.ClientException:
            await self.voice.move_to(vChannel)

        await ctx.send("Ready!")

    @commands.command()
    async def leave(self, ctx):
        """Disconnects from a voice channel. Does nothing if not connected."""
        if self.voice == None:
            await ctx.send("Not currently in a voice channel.")
        elif self.voice.channel != ctx.author.voice.channel:
            await ctx.send("I need to be in the same voice channel as you " +
                            "to do that!")
            return

        await self.voice.disconnect()
        await ctx.send("Left the voice channel.")
        
    @commands.command()
    async def play(self, ctx, ytLink : str):
        """Download and play a YouTube video. Direct links only, at the moment."""
        if self.voice == None:
            await ctx.send("I need to be in a voice channel to do that!")
            return
        elif self.voice.is_playing():
            await ctx.send("I'm already playing audio!")
            return
        elif self.voice.channel != ctx.author.voice.channel:
            await ctx.send("I need to be in the same voice channel as you " + 
                            "to do that!")
            return

        filename = opj(self.TEMP_PATH, "%s-%f" % (ctx.guild.id, time.time()))
        process = mp.Process(target = downloadVideo, args = [ytLink, filename])
        process.start()

        await ctx.send("Please wait while I download the video for streaming...")

        while process.is_alive():
            await asyncio.sleep(0.75)

        ffas = discord.FFmpegPCMAudio(filename + ".opus")
        self.voice.play(ffas)
        await ctx.send("Now playing.")

        while (self.voice.is_playing()):
            await asyncio.sleep(0.75)

        await ctx.send("Playback stopped.")

        # the bot doesn't cache music files, so get rid of them
        # once we're done streaming the music
        os.remove(filename + ".opus")

    @commands.command()
    async def stop(self, ctx):
        """Stop playback. Does nothing if not playing audio."""
        if self.voice == None or \
            not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        elif self.voice.channel != ctx.author.voice.channel:
            await ctx.send("I'm not in the same voice channel as you are!")
        else:
            self.voice.stop()

    @commands.command()
    async def pause(self, ctx):
        """Pauses playback. Does nothing if not playing audio."""
        if self.voice == None or \
            not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        elif self.voice.is_paused():
            await ctx.send("Playback has already been paused!")
        elif self.voice.channel != ctx.author.voice.channel:
            await ctx.send("I'm not in the same voice channel as you are!")
        else:
            self.voice.pause()
            await ctx.send("Pausing audio playback.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes audio playback, if paused. Does nothing otherwise."""
        if self.voice == None or \
            not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        elif not self.voice.is_paused():
            await ctx.send("Playback isn't paused!")
        elif self.voice.channel != ctx.author.voice.channel:
            await ctx.send("I'm not in the same voice channel as you are!")
        else:
            self.voice.resume()
            await ctx.send("Resuming audio playback.")

def setup(bot):
    bot.add_cog(Music(bot))
