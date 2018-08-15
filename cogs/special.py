import asyncio
import discord
import util

from discord.ext import commands
from cogs.base import Base

class Special(Base):
    @commands.command(pass_context = True)
    async def setAvatar(self, ctx, link : str):
        util.nullifyExecute()
        """Set the bot's avatar."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        await self.bot.send_typing(ctx.message.channel)
        image = requests.get(link)

        try:
            await self.bot.edit_profile(avatar = image.content)
            await self.bot.say("How do I look?")
        except discord.errors.InvalidArgument:
            await self.bot.say("That image type is unsupported!")
        except:
            await self.bot.say("Something went wrong.  Sorry.")

    @commands.command(pass_context = True)
    async def updateBot(self, ctx):
        util.nullifyExecute()
        """Update the bot to the latest version.  This requires special perms."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        await self.bot.say("Updating the bot...")
        os.system("git fetch origin")
        os.system("git checkout --force origin/bepisbot-mk3")
        await self.bot.say("Bot is updated!  Restarting...")
        await self.bot.close()
        os.system("python3.5 main.py")

    @commands.command(pass_context = True)
    async def shutdown(self, ctx):
        util.nullifyExecute()
        """Shutdown the bot.  Useful.  Occasionally."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
            
        await self.bot.say(":ballot_box_with_check: BepisBot is shutting down...")
        await asyncio.sleep(1)
        await self.bot.close()
        
    @commands.command(pass_context = True)
    async def restart(self, ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
            
        await self.bot.say(":ballot_box_with_check: BepisBot is restarting...")
        await asyncio.sleep(1)
        await self.bot.close()
        os.system("python3.5 main.py")

    @commands.command(pass_context = True)
    async def setPlaying(self, ctx, *, playing : str):
        util.nullifyExecute()
        "Set the bot's playing status."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        await self.bot.change_presence(game = discord.Game(name = playing))
        await self.bot.say("Now playing {}".format(playing))

    @commands.command(pass_context = True)
    async def listServers(self, ctx):
        util.nullifyExecute()
        perms = util.check_perms(self, ctx)
        if not perms:
            return
    
        e = discord.Embed()
        e.title = "List of Servers BepisBot is in:"
        
        serverList = ""
        
        for server in self.bot.servers:
            print(server.name)
            serverList += "* {}\n".format(server.name)
            
        e.description = serverList
        
        await self.bot.say(embed = e)
