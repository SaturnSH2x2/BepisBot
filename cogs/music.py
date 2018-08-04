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
    "Commands for playing music and audio from YouTube video links."
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

    # helper function to avoid repeating code for checking certain
    # command conditions
    async def checkPermissions(self, ctx):
        if self.voice == None:
            await ctx.send("Not currently in a voice channel.")
            return False
        if self.voice.channel != ctx.author.voice.channel:
            await ctx.send("I need to be in the same voice channel as you " +
                            "to do that!")
            return False

        return True

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel. You must be in VC for this to work."""
        util.nullifyExecute()
        if not await self._check_opus(ctx):
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
        if not await self.checkPermissions(ctx):
            return

        await self.voice.disconnect()
        await ctx.send("Left the voice channel.")
        
    @commands.command()
    async def play(self, ctx, ytLink : str):
        """Download and play a YouTube video. Direct links only, at the moment."""

        # sanity checks
        if not await self.checkPermissions(ctx):
            return
        elif self.voice.is_playing():
            await ctx.send("I'm already playing audio!")
            return

        # determine filename, start downloading the video
        filename = opj(self.TEMP_PATH, "%s-%f" % (ctx.guild.id, time.time()))
        process = mp.Process(target = downloadVideo, args = [ytLink, filename])
        process.start()

        await ctx.send("Please wait while I download the video for streaming...")

        # wait for the process to complete without holding up
        # the main process
        while process.is_alive():
            await asyncio.sleep(0.75)

        # load newly-downloaded file as AudioSource
        ffas = discord.FFmpegPCMAudio(filename + ".opus")
        self.voice.play(ffas)
        await ctx.send("Now playing.")

        # wait for the audio playback to stop
        while (self.voice.is_playing() or self.voice.is_paused()):
            await asyncio.sleep(0.75)
        await ctx.send("Playback stopped.")

        # the bot doesn't cache music files, so get rid of them
        # once we're done streaming the music
        os.remove(filename + ".opus")

    # the rest of these commands should be fairly self-explanatory
    @commands.command()
    async def stop(self, ctx):
        """Stop playback. Does nothing if not playing audio."""
        if not await self.checkPermissions(ctx):
            return
        elif not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        else:
            self.voice.stop()

    @commands.command()
    async def pause(self, ctx):
        """Pauses playback. Does nothing if not playing audio."""
        if not await self.checkPermissions(ctx):
            return
        elif not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        else:
            self.voice.pause()
            await ctx.send("Pausing audio playback.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes audio playback, if paused. Does nothing otherwise."""
        if not await self.checkPermissions(ctx):
            return
        elif not self.voice.is_paused():
            await ctx.send("Playback isn't paused!")
        else:
            self.voice.resume()
            await ctx.send("Resuming audio playback.")

def setup(bot):
    bot.add_cog(Music(bot))
