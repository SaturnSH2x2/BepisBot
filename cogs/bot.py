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
        self.kSpam = []
        super().__init__(bot)

    @commands.command()
    @commands.guild_only()
    async def setCommandEnable(self, ctx, passedCommand : str, enable : bool):
        "Disable a specific bot command. Requires the Manage Server permission."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to run " +
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
              
    @commands.command()
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
    
    @commands.command()
    @commands.guild_only()
    async def deleteMessages(self, ctx, number : int = 10):
        "Delete the number of messages specified."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_messages:
            await ctx.send("You need the \"Manage Messages\" permission " + 
                            "in order to run this command.")
            return

        await ctx.channel.purge(limit = number + 1)
        msg = await ctx.send("Deleted {} messages.".format(number))
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(pass_context = True)
    async def inviteLink(self, ctx):
        "DMs you an invite link for the bot."
        client_id = util.load_js("config.json")["client-id"]
        await ctx.author.send(
            "https://discordapp.com/oauth2/authorize?&client_id=" + 
            "{0}&scope=bot&permissions=0".format(client_id))

    @commands.command(pass_context = True)
    async def say(self, ctx, *, thing):
        "Have the bot say something."

        if ctx.message.author.id == self.bot.user.id:
            return

        await ctx.send(thing)
        
    @commands.command()
    @commands.guild_only()
    async def spam(self, ctx, number : int, *, thing : str):
        "Spam a message.  Use with caution."
        if ctx.message.author.id == self.bot.user.id:
            return
            
        if ctx.guild != None and str(ctx.guild.id) in self.kSpam:
            return			

        if len(ctx.message.role_mentions) > 0:
            await ctx.send("The bot cannot spam role mentions.")
            return

        await ctx.trigger_typing()
        
        if number > 100000000000000000000:
            await ctx.send("Are you fucking out of your mind?")
            return
        if number > 200:
            await ctx.send("Yeah, no.")
            return
        
        for i in range(number):
            if ctx.guild != None and str(ctx.guild.id) in self.kSpam:
                break
                
            await ctx.send(thing)
            
            if i == number - 1:
                pass
            else:
                await ctx.trigger_typing()
            await asyncio.sleep(0.75)

    @commands.command()
    @commands.guild_only()
    async def killSpam(self, ctx, seconds : int = 60):
        "Kills a previously-executed spam command for a certain amount of time."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_messages:
            await ctx.send("You need the \"Manage Messages\" permission " + 
                            "in order to run this command.")
            return

        # this is to make sure that the command isn't essentially rendered
        # useles by killSpam
        if seconds > 60 * 10:
            await ctx.send("Cannot kill spam for any length longer than " +
                            "10 minutes.")
            return

        self.kSpam.append(str(ctx.guild.id))
        await ctx.send("Spam killed.  All spam commands " +
                "will be ignored for the next %s seconds." % seconds)
        await asyncio.sleep(seconds)
        self.kSpam.remove(str(ctx.guild.id))

    @commands.command(pass_context = True)
    async def whisper(self, ctx, *, thing):
        "Make it so that it looks like the bot said something on its own."

        if ctx.message.author.id == self.bot.user.id:
            return
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(thing)
    
    @commands.command()
    async def poll(self, ctx, *, msg : str = None):
        "Have the bot create a poll, with reactions as votes."
        options = msg.split(" | ")
        try:
            await ctx.message.delete()
        except:
            pass  # apparently, the user was 2fast4us

        if len(options) < 1:
            await self.bot.say("Not enough parameters")
        else:
            emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']
            toReact = []
            question=options.pop(0)
            if len(options) > len(emoji):
                await ctx.send("Too many options")
            else:
                for i in range(len(options)):
                    toReact.append(emoji[i])
                    question += "\n" + options[i] + "\t" + emoji[i]
                postedMessage = await ctx.send(question)
                for reaction in toReact:
                    await postedMessage.add_reaction(reaction)

def setup(bot):
    bot.add_cog(BotCmd(bot))
