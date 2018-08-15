import asyncio
import discord
import requests
import util
import os
import subprocess

from discord.ext import commands
from cogs.base import Base

from os.path import join as opj

class BotCmd(Base):
    def __init__(self, bot):
        conf = util.load_js("config.json")
        self.okbLocation = conf["okaybot-location"]
        self.okbToken    = conf["okaybot-token"]
        self.mod_roles= conf["moderator-roles"]
        self.kSpam = False
        super().__init__(bot)

    @commands.command(pass_context = True)
    @commands.guild_only()
    async def setCommandEnable(self, ctx, passedCommand : str, enable : bool):
        "Disable a specific bot command. Requires the Manage Server permission."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the Manage Server permission to run " +
                            "this command.")
            return
            
        path = opj(self.JSON_PATH, "%s-disabled-commands.json" %
                                    ctx.guild.id)
        disabledCommands = util.load_js(path, returnListIfEmpty = True)
            
        cmd = self.bot.get_command(passedCommand)
        if cmd == self.setCommandEnable:
            await ctx.send("That command cannot be disabled.")
            return
        elif cmd == None:
            await ctx.send("The %s%s command does not exist!" % \
                    (self.bot.command_prefix, passedCommand))
            return
    
        if enable == False:
            if passedCommand in disabledCommands:
                await ctx.send("%s is already disabled." % passedCommand)
                return
            disabledCommands.append(passedCommand)
            await ctx.send("%s has been disabled for use in this server." % \
                            passedCommand)
        else:
            if passedCommand not in disabledCommands:
                await ctx.send("%s is already enabled." % passedCommand)
                return
            disabledCommands.remove(passedCommand)
            await ctx.send("%s has been enabled for use in this server." % \
                            passedCommand)

        util.save_js(path, disabledCommands)
              
    @commands.command(pass_context = True)
    @commands.guild_only()
    async def printDisabledCommands(self, ctx):
        "Print the commands that have been disabled for this server."
        disabledCommands = util.load_js(opj(self.JSON_PATH,
                                    "%s-disabled-commands.json" % ctx.guild.id))
        e = discord.Embed()
        eContent = ""
        for d in disabledCommands:
            eContent += "%s\n" % d
                
        if eContent == "":
            e.title = "No commands have been disabled for this server."
        else:
            e.title = "Here are the commands that have been disabled for this server."
        e.description = eContent
        
        await ctx.send(embed = e)
    
    @commands.command(pass_context = True)
    async def deleteMessages(self, ctx, number : int = 10):
        util.nullifyExecute()
        """Delete the number of messages specified.  Deletes 10 by default.  This requires special perms."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        await self.bot.purge_from(ctx.message.channel, limit = number)
        msg = await self.bot.say("Deleted {} messages.".format(number))
        await asyncio.sleep(5)
        await self.bot.delete_message(msg)

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
    async def setUsername(self, ctx, *, name : str):
        util.nullifyExecute()
        """Set the bot's username.  This requires special perms."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        try:
            await self.bot.edit_profile(username = name)
            await self.bot.say("Henceforth, I shall be known as {}!".format(name))
        except discord.errors.HTTPException:
            await self.bot.say("Hrm?  Something came up; the profile can't be set.")
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
    async def leaveServer(self, ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
            
        await self.bot.say("Leaving server.  Bye... :cry:")
        await self.bot.leave_server(ctx.message.server)

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

        if "emibot" in playing.lower():
            await self.bot.say("Haha.  Nice try there.")
            return

        if ( "clone" in playing.lower() ) and ( "bot" in playing.lower() ):
            await self.bot.say("Haha.  Nice try there.")
            return

        if ( "emily" in playing.lower() ) and ( "bot" in playing.lower() ):
            await self.bot.say("Haha.  Nice try there.")
            return

        await self.bot.change_presence(game = discord.Game(name = playing))
        await self.bot.say("Now playing {}".format(playing))

    @commands.command(pass_context = True)
    async def inviteLink(self, ctx):
        util.nullifyExecute()
        """Invite the bot to your own server!  Sends you a DM with the invite link."""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        client_id = util.load_js("config.json")["client-id"]
        await self.bot.whisper("https://discordapp.com/oauth2/authorize?&client_id={0}&scope=bot&permissions=0".format(client_id))

    @commands.command(pass_context = True)
    async def say(self, ctx, *, thing):
        util.nullifyExecute()
        """Have the bot say something.  Chances are, you're gonna make it say something stupid."""
        #thing = ctx.message.content[len(ctx.prefix) + len(ctx.command.name) + 1:]

        if ctx.message.author.id == self.bot.user.id:
            return

        await self.bot.say(thing)
        
    @commands.command()
    async def spam(self, ctx, *, number : int, thing : str):
        util.nullifyExecute()
        """Spam a message.  Use with caution."""
        if ctx.message.author.id == self.bot.user.id:
            return
            
        if self.kSpam == True:
            return			

        if len(ctx.message.role_mentions) > 0:
            await self.bot.say("The bot cannot spam role mentions.")
            return

        await self.bot.type()
        
        if number > 100000000000000000000:
            await self.bot.say("Are you fucking out of your mind?")
            return
        if number > 100:
            await self.bot.say("Yeah, no.")
            return
        
        for i in range(number):
            if self.kSpam == True:
                break
                
            await self.bot.say(thing)
            
            if i == number - 1:
                pass
            else:
                await self.bot.type()
            await asyncio.sleep(0.75)

    @commands.command(pass_context = True)
    async def killSpam(self, ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
            
        self.kSpam = True
        await self.bot.say("Spam killed.  All spam commands will be ignored for the next minute.")
        await asyncio.sleep(60)
        self.kSpam = False

    @commands.command(pass_context = True)
    async def whisper(self, ctx, *, thing):
        util.nullifyExecute()
        """Make it so that it looks like the bot said something on its own."""
        #thing = ctx.message.content[len(ctx.prefix) + len(ctx.command.name) + 1:]

        if ctx.message.author.id == self.bot.user.id:
            return
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        await self.bot.say(thing)
        
    @commands.command(pass_context = True)
    async def setNick(self, ctx, *, nick : str):
        util.nullifyExecute()
        """Nickname test"""
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        botMember = ctx.message.server.get_member(self.bot.user.id)
        await self.bot.change_nickname(botMember, nick)
        await self.bot.say("Set nickname to {}".format(nick))
        
    @commands.command(pass_context = True)
    async def enableLogging(self, ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
            
        logLog = util.load_js("logs/server-list.json")
        if len(logLog) == 0:
            logLog = []
            
        logLog.append(ctx.message.server.id)
        util.save_js("logs/server-list.json", logLog)
        
        await self.bot.say("Logging for this server has been enabled.")

    @commands.command(pass_context = True)
    async def disableLogging(self, ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
            
        logLog = util.load_js("logs/server-list.json")
        logLog.remove(ctx.message.server.id)
        util.save_js("logs/server-list.json", logLog)
        
        await self.bot.say("Logging for this server has been disabled.")
        
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
            
    
def setup(bot):
    bot.add_cog(BotCmd(bot))
