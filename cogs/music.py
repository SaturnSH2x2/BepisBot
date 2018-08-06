import asyncio
import discord
import time
import io
import os
import queue
import multiprocessing as mp
import youtube_dl
import util

from ctypes.util import find_library
from discord.ext import commands
from cogs.base import Base
from os.path import join as opj

# function to download YouTube videos to stream as needed.
# Run as a separate process.
def downloadVideo(ytLink : str, filename : str, q : mp.Queue):
    opts = {
        "outtmpl" : filename,
        "postprocessors" : [{
            "key" : "FFmpegExtractAudio",
            "preferredcodec" : "opus",
            "preferredquality" : "192",
        }]
    }
    
    with youtube_dl.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(ytLink, download = False)
        q.put(info)
        ydl.download([ytLink])

# TODO: this code won't work on a per-server basis. Keep track of what VC
# the bot is in on by server (you may need to use dictionaries for this)
class Music(Base):
    "Commands for playing music and audio from YouTube video links."
    def __init__(self, bot):
        if discord.opus.is_loaded():
            pass
        else:
            discord.opus.load_opus(find_library("opus"))
            
        self.voice = None
        self.musicList = []
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
        "Joins a voice channel. You must be in VC for this to work."
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
        "Disconnects from a voice channel. Does nothing if not connected."
        if not await self.checkPermissions(ctx):
            return

        await self.voice.disconnect()
        await ctx.send("Left the voice channel.")
        
    @commands.command()
    async def play(self, ctx, ytLink : str):
        "Download and play a YouTube video. Direct links only, at the moment. \
        If a video is already playing, yours will be added to a queue."

        # sanity checks
        if not await self.checkPermissions(ctx):
            return

        # determine filename, start downloading the video
        filename = opj(self.TEMP_PATH, "%s-%f" % (ctx.guild.id, time.time()))
        vidInfoQueue = mp.Queue()
        process = mp.Process(target = downloadVideo, args = [ytLink, filename, vidInfoQueue])
        process.start()

        await ctx.send("Please wait while I download the video for streaming...")
        await ctx.trigger_typing()

        # wait for the process to complete without holding up
        # the main process
        while process.is_alive():
            await asyncio.sleep(0.75)

        vidInfo = vidInfoQueue.get()
        self.musicList += [[filename, vidInfo["title"]]]
    
        if self.voice.is_playing():
            await ctx.send("**%s** has been added to the queue (position in queue: %i)" % \
                    (vidInfo["title"], len(self.musicList)))
            return

        # playback everything in the list
        while len(self.musicList) > 0:
            listEntry = self.musicList[0]
            filename = listEntry[0]
            title = listEntry[1]

            ffas = discord.FFmpegPCMAudio(filename + ".opus")
            self.voice.play(ffas)
            await ctx.send("Now playing: **%s**" % (title))

            # wait for the audio playback to stop
            while (self.voice.is_playing() or self.voice.is_paused()):
                await asyncio.sleep(0.75)

            # the bot doesn't cache music files, so get rid of them
            # once we're done streaming the music
            os.remove(filename + ".opus")
            self.musicList.remove(listEntry)
        
        await ctx.send("Playback stopped.")

    # the rest of these commands should be fairly self-explanatory
    @commands.command()
    async def queue(self, ctx):
        "List all items in the current playback queue."
        queueString = ""

        queueString += "Now playing: **%s**\n\n" % (self.musicList[0][1])
        for i in range(1, len(self.musicList)):
            queueString += "%i.  **%s**\n" % (i + 1, self.musicList[i][1])
        await ctx.send(queueString)

    @commands.command()
    async def skip(self, ctx):
        "Skips the video currently playing in the queue."
        if not await self.checkPermissions(ctx):
            return
        elif not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        else:
            await ctx.send("Skipping: **%s**" % (self.musicList[0][1]))
            self.voice.stop()

    @commands.command()
    async def pause(self, ctx):
        "Pauses playback. Does nothing if not playing audio."
        if not await self.checkPermissions(ctx):
            return
        elif not self.voice.is_playing():
            await ctx.send("I'm not playing audio at the moment.")
        else:
            self.voice.pause()
            await ctx.send("Pausing audio playback.")

    @commands.command()
    async def resume(self, ctx):
        "Resumes audio playback, if paused. Does nothing otherwise."
        if not await self.checkPermissions(ctx):
            return
        elif not self.voice.is_paused():
            await ctx.send("Playback isn't paused!")
        else:
            self.voice.resume()
            await ctx.send("Resuming audio playback.")

def setup(bot):
    bot.add_cog(Music(bot))
