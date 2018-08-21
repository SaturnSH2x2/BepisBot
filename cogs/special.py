import asyncio
import discord
import util
import multiprocessing as mp
import subprocess
import os

from discord.ext import commands
from cogs.base import Base

from os.path import join as opj

class Special(Base):
    def __init__(self, bot):
        self.specialUsers = util.load_js(opj("config.json"))["special"]
        super().__init__(bot)

    # helper function to determine if the author is
    # a special user
    def specialCheck(self, user : discord.User):
        if str(user.id) in self.specialUsers:
            return True
        return False

    # helper function to download an image
    def dlImage(url : str, q : mp.Queue):
        image = requests.get(url)
        q.put(image.content)

    @commands.command(hidden = True)
    async def setAvatar(self, ctx, link : str):
        "Set the bot's avatar."
        perms = self.specialCheck(ctx.author)
        if not perms:
            return

        await ctx.trigger_typing()

        queue = mp.Queue()
        dlProcess = mp.Process(target=dlImage, args=(link, queue))
        
        while dlProcess.is_alive():
            asyncio.sleep(0.75)

        image = queue.get()

        try:
            await self.bot.edit_profile(avatar = image)
            await ctx.send("How do I look?")
        except discord.errors.InvalidArgument:
            await ctx.send("That image type is unsupported!")
        except:
            await ctx.send("Something went wrong. Sorry.")

    @commands.command(hidden = True)
    async def updateBot(self, ctx):
        "Update the bot to the latest version.  This requires special perms."
        perms = self.specialCheck(ctx.author)
        if not perms:
            return

        await ctx.send("Updating the bot...")
        os.system("git fetch origin")
        os.system("git checkout --force origin/bepisbot-mk3")
        await ctx.send("Bot is updated!  Restarting...")

        os.system("./run.sh")
        await self.bot.close()

    @commands.command(hidden = True)
    async def shutdown(self, ctx):
        "Shutdown the bot. Useful. Occasionally."
        perms = self.specialCheck(ctx.author)
        if not perms:
            return
            
        await ctx.send(":ballot_box_with_check: BepisBot is shutting down...")
        await asyncio.sleep(0.75)
        await self.bot.close()
        
    @commands.command(hidden = True)
    async def restart(self, ctx):
        "Restarts the bot."
        perms = self.specialCheck(ctx.author)
        if not perms:
            return
            
        await ctx.send(":ballot_box_with_check: BepisBot is restarting...")
        await asyncio.sleep(0.75)

        os.system("./run.sh &")
        await self.bot.close()

    @commands.command(hidden = True)
    async def setPlaying(self, ctx, *, playing : str):
        "Set the bot's playing status."
        perms = self.specialCheck(ctx.author)
        if not perms:
            return

        await self.bot.change_presence(game = discord.Game(name = playing))
        await ctx.send("Now playing:  %s" %  playing)

    @commands.command(hidden = True)
    async def listServers(self, ctx):
        "List all the servers BepisBot is currently in."
        perms = self.specialCheck(ctx.author)
        if not perms:
            return
    
        e = discord.Embed()
        e.title = "List of Servers BepisBot is in:"
        
        serverList = ""
        
        for server in self.bot.guilds:
            serverList += "- %s\n" % server.name
            
        e.description = serverList
        
        await ctx.send(embed = e)

def setup(bot):
    bot.add_cog(Special(bot))