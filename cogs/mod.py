import asyncio
import discord
import os
import hashlib
import time

import util
import cogs.base as base

import shutil

from discord.ext import commands
from datetime import datetime
from os.path import join as opj

class Moderator(base.Base):
    MAXWARNS = 3

    def __init__(self, bot, config):
        self.mod_roles = config["moderator-roles"]
        super().__init__(bot)

        # make sure this directory exists
        try:
            os.mkdir("warns")
        except FileExistsError:
            pass
        try:
            os.mkdir("notes")
        except FileExistsError:
            pass

    @commands.command()
    async def kick(self, ctx, member : discord.Member):
        "Kick a member from a server."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.kick_members:
            await ctx.send("You need the \"Kick Members\" permission to " + 
                            "run this command.")
            return

        try:
            await member.kick()
            await ctx.send("%s has been kicked from the server." % member.name)
        except:
            await ctx.send("Could not kick member.  This might be a " + 
                           "permissions issue with the bot.")

    @commands.command()
    async def ban(self, ctx, member : discord.Member):
        "Bans a member from a server."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.ban_members:
            await ctx.send("You need the \"Ban Members\" permission to " + 
                            "run this command.")
            return

        try:
            member.ban()
            await ctx.send("%s has been banned from the server." % member.name)
        except:
            await ctx.send("Could not ban member.  This might be a " + 
                           "permissions issue with the bot.")

    @commands.command(pass_context = True)
    async def unwarn(self, ctx, member : discord.Member):
        "Remove the most recent warn(s) from a member."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.ban_members:
            await ctx.send("You need the \"Ban Members\" permission to " + 
                            "run this command.")
            return

        path = opj(self.JSON_PATH, "%s-warns.json" % ctx.guild.id)
        
        serverWarnList = util.load_js(path)
        strID = str(member.id)
        
        # I feel this section could have been done a bit better
        if strID not in serverWarnList.keys():
            await ctx.send("%s does not have any warns." % member.name)
            return

        warns = serverWarnList[strID]
        warnCount = len(warns)

        if warnCount == 0:
            await ctx.send("%s does not have any warns." % member.name)
            return

        # check to see that the response is valid
        def responseCheck(message):
            if message.content.lower() == "cancel":
                return True

            try:
                choice = int(message.content)
                return (0 < choice <= self.MAXWARNS) and \
                        message.author == ctx.author
            except ValueError:
                return False

        eContent = ""
        for i in range(warnCount):
            eContent += "%i.  %s\n\n" % (i + 1, warns[i])
        e = discord.Embed()
        e.title = "Please type the index of the warn to remove, " + \
                    "or type \"cancel\" to cancel unwarn."
        e.description = eContent

        await ctx.send(embed = e)
        response = await self.bot.wait_for("message", check = responseCheck)

        if response.content.lower() == "cancel":
            await ctx.send("Unwarn cancelled.")
            return

        delWarn = int(response.content)

        del warns[delWarn - 1]
        await ctx.send("%s, you have had a warn removed. You now have %i warnings." % \
                (member.mention, len(warns)))
        util.save_js(path, serverWarnList)

    @commands.command(pass_context = True)
    async def warn(self, ctx, member : discord.Member, *, 
                        reason : str = "None"):
        "Warns a member. 3 warns results in a ban."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.ban_members:
            await ctx.send("You need the \"Ban Members\" permission to " + 
                            "run this command.")
            return

        path = opj(self.JSON_PATH, "%s-warns.json" % ctx.guild.id)
        serverWarnList = util.load_js(path)
        strID = str(member.id)

        # properly format the reason
        reasonFmt = time.strftime("%c, by ") + "%s: %s. Reason: %s" % \
                                (ctx.author.name, ctx.author.id, reason)

        if strID not in serverWarnList:
            serverWarnList[strID] = []
        serverWarnList[strID] += [reasonFmt]

        warns = len(serverWarnList[strID])
        warnMessage = "%s, you have been warned by %s." % \
                        (member.mention, util.getMemberName(ctx.author))
        if self.MAXWARNS - warns == 1:
            warnMessage += " This is your final warning. "
        else:
            warnMessage += " You have %i warnings left. " % \
                        (self.MAXWARNS - warns)
        warnMessage += "Reason given: %s" % reason
            
        util.save_js(path, serverWarnList)

        if warns >= self.MAXWARNS:
            await member.ban()
            await ctx.send("%s exceeded %i warnings, and has been banned." % \
                            (member.name, self.MAXWARNS))
        else:
            await ctx.send(warnMessage)

    @commands.command()
    async def listWarns(self, ctx, member : discord.Member = None):
        "List the warnings you or a given member has."
        if member != None and member != ctx.author:
            perms = ctx.author.permissions_in(ctx.channel)
            if not perms.ban_members:
                await ctx.send("You need the \"Ban Members\" permission to " + 
                            "run this command.")
                return

        if member == None:
            member = ctx.author

        path = opj(self.JSON_PATH, "%s-warns.json" % ctx.guild.id)
        name = util.getMemberName(member)
        strID = str(member.id)
        serverWarnList = util.load_js(path)

        if strID in serverWarnList.keys():
            nLine = "\n"
            eContent = "**%i** of **%i** warnings\n\n" % \
                (len(serverWarnList[strID]), self.MAXWARNS)
            warns = serverWarnList[strID]
            eContent += nLine.join(warns)
        else:
            eContent = "No warnings for %s." % name

        e = discord.Embed()
        e.title = "Warnings for %s" % name
        e.description = eContent

        await ctx.send("Warns: ", embed = e)

    @commands.command(pass_context=True)
    async def note(self, ctx, member : discord.Member, *, note : str = None):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        await self.bot.delete_message(ctx.message)
        if note==None:
            await self.bot.say("You didn't make a note.")
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        if member.id not in serverNoteList:
            serverNoteList[member.id]={'noteNum':0, 'name':{'1':''}, 'note':{'1':''},'time':{'1':''},'issuer':{'1':''},'issuerName':{'1':''}}
        serverNoteList[member.id]["noteNum"] += 1
        noteNum=str(serverNoteList[member.id]["noteNum"])
        serverNoteList[member.id]["note"][noteNum] = note
        serverNoteList[member.id]["name"][noteNum] = member.name
        serverNoteList[member.id]["time"][noteNum] = str(datetime.now())
        serverNoteList[member.id]["issuer"][noteNum] = ctx.message.author.id
        serverNoteList[member.id]["issuerName"][noteNum] = ctx.message.author.name
        util.save_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)), serverNoteList)
        await self.bot.say("Your note has been recorded")

    @commands.command(pass_context=True)
    async def listNote(self, ctx, member : discord.Member, *, note : str = None):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        if note==None:
            output="`"
            if member.id not in serverNoteList or serverNoteList[member.id]["noteNum"]==0:
                await self.bot.say("That user doesn't have any notes.")
                return
            noteNum=str(serverNoteList[member.id]["noteNum"])
            for i in range(1,int(noteNum)+1):
                output+=str(serverNoteList[member.id]["name"][str(i)]+" {} ".format(member.id)+str(serverNoteList[member.id]["time"][str(i)])+" "+str(serverNoteList[member.id]["issuerName"][str(i)])+" "+str(serverNoteList[member.id]["issuer"][str(i)])+" "+str(serverNoteList[member.id]["note"][str(i)]))+"\n"
            output=output[:-1]
            output+="`"
            await self.bot.say(output)
            return
        if member.id not in serverNoteList or serverNoteList[member.id]["noteNum"]==0:
            await self.bot.say("That user doesn't have any notes.")
            return
        try:
            loggedNote = serverNoteList[member.id]["note"][note]
            loggedName = serverNoteList[member.id]["name"][note]
            loggedTime = serverNoteList[member.id]["time"][note]
            loggedIssuer = serverNoteList[member.id]["issuer"][note]
            loggedIssuerName=serverNoteList[member.id]["issuerName"][note]
            await self.bot.say(loggedIssuerName+""" made a note about """+loggedName+""" on """+loggedTime+""" that said
`"""+loggedNote+"""`""")
        except KeyError:
            await self.bot.say("That note does not exist")


    @commands.command(pass_context=True)
    async def deleteNote(self, ctx, member : discord.Member, *, note : str = None):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        await self.bot.delete_message(ctx.message)
        if note == None:
            await self.bot.say("Please provide a note number.")
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        if member.id not in serverNoteList or serverNoteList[member.id]["noteNum"]==0:
            await self.bot.say("That user doesn't have any notes.")
            return
        noteNum=str(serverNoteList[member.id]["noteNum"])
        if note>noteNum:
            await self.bot.say("That user doesn't have that many notes.")
            return
        
        if serverNoteList[member.id]["noteNum"] <= 1:
            serverNoteList.pop(member.id, None)
            
        for i in range(int(note),serverNoteList[member.id]["noteNum"]):
            for key, item in serverNoteList[member.id].items():
                if key == "noteNum":
                    continue
                
                if serverNoteList[member.id]["noteNum"] == 1:
                    serverNoteList[member.id][key].pop(str(i), None)
                else:
                    serverNoteList[member.id][key][str(i)] = serverNoteList[member.id][key][str(i+1)]
        
        """
            try:
                
                serverNoteList[member.id]["note"][str(i)]=serverNoteList[member.id]["note"][str(i+1)]
                serverNoteList[member.id]["name"][str(i)]=serverNoteList[member.id]["name"][str(i+1)]
                serverNoteList[member.id]["time"][str(i)]=serverNoteList[member.id]["time"][str(i+1)]
                serverNoteList[member.id]["issuer"][str(i)]=serverNoteList[member.id]["issuer"][str(i+1)]
                serverNoteList[member.id]["issuerName"][str(i)]=serverNoteList[member.id]["issuerName"][str(i+1)]
            except KeyError:
                serverNoteList[member.id]["noteNum"]-=1
                util.save_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)), serverNoteList)
                return
        """
        util.save_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)), serverNoteList)

    @commands.command(pass_context=True)
    async def allNote(self,ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        
        noteStr = ""
        for item in serverNoteList:
            for i in range(0,serverNoteList[item]["noteNum"]):
                noteStr += "Note: " + serverNoteList[item]["note"][str(i+1)] + "\n" 
                noteStr += "Time: " + serverNoteList[item]["time"][str(i+1)] + "\n"
                noteStr += "Issuer: " + serverNoteList[item]["issuer"][str(i+1)] + "\n"
                noteStr += "Name: " + serverNoteList[item]["name"][str(i+1)] + "\n"
                noteStr += "Issuer Name: " + serverNoteList[item]["issuerName"][str(i+1)] + "\n"
                noteStr += "\n"
            noteStr += "\n"
            
        e = discord.Embed(title = "Note List", description = noteStr)
        await self.bot.say(embed = e)

    @commands.command(pass_context=True)
    async def backupNote(self, ctx, *, text : str = None):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        if text == None:
            await self.bot.upload(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        else:
            serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
            noteListRaw=[serverNoteList[i:i+1750] for i in range(0, len(serverNoteList), 1750)]
            for i in range(len(noteListRaw)):
                await self.bot.say(noteListRaw[i])
#        await self.bot.say(serverNoteList)

    @commands.command(pass_context=True)
    async def hashNote(self,ctx):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        hashed=hashlib.sha256(str(serverNoteList).encode("utf-8")).hexdigest()
        await self.bot.say(hashed)

    @commands.command(pass_context=True)
    async def wipeNote(self, ctx, *, confirm : str = None):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        key=hashlib.sha256(str(serverNoteList).encode("utf-8")).hexdigest()
        if confirm==key:
            await self.bot.say("Emergency note backup.")
            await self.bot.upload(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
            serverNoteList={}
            util.save_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)), serverNoteList)
            await self.bot.say("All notes have been wiped.")
            return
        else:
            await self.bot.say("To wipe the notes, you must enter the correct key.")
            return

    @commands.command(pass_context = True)
    async def poll(self, ctx, *, msg : str = None):
        util.nullifyExecute()
        options = msg.split(" | ")
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if len(options)<1:
            await self.bot.say("Not enough parameters")
        else:
            emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']
            toReact = []
            question=options.pop(0)
            if len(options)>len(emoji):
                await self.bot.say("Too many options")
            else:
                for i in range(len(options)):
                    toReact.append(emoji[i])
                    question+="\n"+options[i]+"\t"+emoji[i]
                postedMessage = await self.bot.say(question)
                for reaction in toReact:
                    await self.bot.add_reaction(postedMessage, reaction)

##    @commands.command(pass_context=True)
##    async def clearCache(self, ctx):
##        util.nullifyExecute()
##        perms = await util.check_perms(self, ctx)
##        if not perms:
##            return
##        if ctx.message.author.id == self.bot.user.id:
##            return
##        folder = 'cache'
##        print(os.listdir(folder))
##        for the_file in os.listdir(folder):
##            file_path = os.path.join(folder, the_file)
##            try:
##                if os.path.isfile(file_path):
##                    os.unlink(file_path)
##                elif os.path.isdir(file_path): shutil.rmtree(file_path)
##            except Exception as e:
##                await self.bot.say(e)
##        await self.bot.say("Done")
##        return


def setup(bot):
    config = util.load_js("config.json")
    bot.add_cog(Moderator(bot, config))
