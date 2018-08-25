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
        super().__init__(bot)

        # make sure this directory exists
        try:
            os.mkdir("notes")
        except FileExistsError:
            pass

    @commands.command()
    @commands.guild_only()
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
    @commands.guild_only()
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

    @commands.command()
    @commands.guild_only()
    async def unwarn(self, ctx, member : discord.Member):
        "Remove the most recent warn(s) from a member."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.ban_members:
            await ctx.send("You need the \"Ban Members\" permission to " + 
                            "run this command.")
            return

        key = "warns:%s:%s" % (ctx.guild.id, member.id)
        sw = await self.bot.rconn.lrange(key)
        warnList = []
        for s in sw:
            item = await s
            warnList.append(item)
        strID = str(member.id)
        
        # I feel this section could have been done a bit better
        if len(warnList) == 0:
            await ctx.send("%s does not have any warns." % member.name)
            return

        warnCount = len(warnList)

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
            eContent += "%i.  %s\n\n" % (i + 1, warnList[i])
        e = discord.Embed()
        e.title = "Please type the index of the warn to remove, " + \
                    "or type \"cancel\" to cancel unwarn."
        e.description = eContent

        await ctx.send(embed = e)
        response = await self.bot.wait_for("message", check = responseCheck)

        if response.content.lower() == "cancel":
            await ctx.send("Unwarn cancelled.")
            return

        delWarn = int(response.content) - 1

        await self.bot.rconn.lrem(key, value = warnList[delWarn])
        await ctx.send("%s, you have had a warn removed. You now have %i warnings." % \
                (member.mention, len(warnList) - 1))
        #util.save_js(path, warnList)

    @commands.command()
    @commands.guild_only()
    async def warn(self, ctx, member : discord.Member, *, 
                        reason : str = "None"):
        "Warns a member. 3 warns results in a ban."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.ban_members:
            await ctx.send("You need the \"Ban Members\" permission to " + 
                            "run this command.")
            return

        key = "warns:%s:%s" % (ctx.guild.id, member.id)
        sw = await self.bot.rconn.lrange(key)
        warnList = []
        for s in sw:
            item = await s
            warnList.append(item)
        strID = str(member.id)
        print(warnList)

        # properly format the reason
        reasonFmt = time.strftime("%c, by ") + "%s: %s. Reason: %s" % \
                                (ctx.author.name, ctx.author.id, reason)

        # increment warncount by 1 to keep things accurate
        warns = len(warnList) + 1

        warnMessage = "%s, you have been warned by %s." % \
                        (member.mention, util.getMemberName(ctx.author))
        if self.MAXWARNS - warns == 1:
            warnMessage += " This is your final warning. "
        else:
            warnMessage += " You have %i warnings left. " % \
                        (self.MAXWARNS - warns)
        warnMessage += "Reason given: %s" % reason
            
        if warns >= self.MAXWARNS:
            await member.ban()
            await ctx.send("%s exceeded %i warnings, and has been banned." % \
                            (member.name, self.MAXWARNS))
            await self.bot.rconn.delete(key)
        else:
            await self.bot.rconn.lpush(key, [reasonFmt])
            await ctx.send(warnMessage)

        #util.save_js(path, warnList)

    @commands.command()
    @commands.guild_only()
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

        key = "warns:%s:%s" % (ctx.guild.id, member.id)
        name = util.getMemberName(member)
        strID = str(member.id)
        sw = await self.bot.rconn.lrange(key)
        warnList = []
        for s in sw:
            item = await s
            warnList.append(item)
        print(warnList)

        if len(warnList) > 0:
            nLine = "\n"
            eContent = "**%i** of **%i** warnings\n\n" % \
                (len(warnList), self.MAXWARNS)
            eContent += nLine.join(warnList)
        else:
            eContent = "No warnings for %s." % name

        e = discord.Embed()
        e.title = "Warnings for %s" % name
        e.description = eContent

        await ctx.send(embed = e)

    @commands.command()
    @commands.guild_only()
    async def giveRole(self, ctx, member : discord.Member, role : discord.Role):
        "Give someone a role.  This requires the role to be mentionable."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to " + 
                            "run this command.")
            return

        try:
            await member.add_roles(role)
            await ctx.send("%s has been given the %s role." % \
                    (member.mention, role.name))
        except:
            await ctx.send("Could not add role. This might be a permissions issue.")

    @commands.command()
    @commands.guild_only()
    async def revokeRole(self, ctx, member : discord.Member, role : discord.Role):
        "Revoke a role from someone.  This requires special perms."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to " + 
                            "run this command.")
            return	

        try:
            await member.remove_roles(role)
            await ctx.send("%s has had the %s role revoked." % \
                    (member.mention, role.name))
        except:
            await ctx.send("Could not revoke role. This might be a permissions issue.")

    @commands.command()
    @commands.guild_only()
    async def setBlacklist(self, ctx, member : discord.Member, isBlacklist : bool):
        "Blacklist a user from using the bot in this guild."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to " + 
                            "run this command.")
            return

        path = opj(self.JSON_PATH, "blacklist-%s.json" % ctx.guild.id)
        blacklistDict = util.load_js(path, returnListIfEmpty=True)

        strMemberID = str(member.id)

        if isBlacklist:
            if strMemberID in blacklistDict:
                await ctx.send("%s is already on the blacklist for this server." % \
                                    util.getMemberName(member))
                return
            blacklistDict.append(strMemberID)
            await ctx.send("%s, you have been added to this server's blacklist." % \
                            member.mention)
        else:
            if strMemberID not in blacklistDict:
                await ctx.send("%s is not on the blacklist for this server." % \
                                    util.getMemberName(member))
                return
            blacklistDict.remove(strMemberID)
            await ctx.send("%s, you have been removed from this server's blacklist." \
                            % member.mention)
        
        util.save_js(path, blacklistDict)
        self.bot.blacklist[str(ctx.guild.id)] = blacklistDict

    @commands.command()
    @commands.guild_only()
    async def getBlacklist(self, ctx):
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to " + 
                            "run this command.")
            return

        path = opj(self.JSON_PATH, "blacklist-%s.json" % ctx.guild.id)
        blacklistDict = util.load_js(path, returnListIfEmpty=True)

        e = discord.Embed()
        memberList = []
        for member in blacklistDict:
            aMember = ctx.guild.get_member(int(member))

            memberList.append(util.getMemberName(aMember))

        nl = "\n"
        if len(memberList) == 0:
            e.title = "There are no blacklists for this server."
        else:
            e.title = "Here is a list of blacklisted members for this server:"
            e.description = nl.join(memberList)

        await ctx.send(embed = e)

    @commands.command(pass_context=True)
    async def note(self, ctx, member : discord.Member, *, note : str = None):
        "Make a note of a member. Used for moderation purposes."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to " + 
                            "run this command.")
            return

        await ctx.message.delete()

        if note == None:
            await ctx.send("You didn't make a note.")
            return

        path = opj(self.JSON_PATH, "note-%s.json" % ctx.message.guild.id)
        serverNoteList = util.load_js(path)

        strID = str(member.id)
        if strID not in serverNoteList:
            serverNoteList[strID] = {
                'noteNum' : 0, 
                'name' : { '1' : ' '}, 
                'note' : { '1' : '' },
                'time' : { '1' : '' },
                'issuer' : { '1' : ' '},
                'issuerName' : { '1' : '' }
            }
        serverNoteList[strID]["noteNum"] += 1
        noteNum=str(serverNoteList[strID]["noteNum"])
        serverNoteList[strID]["note"][noteNum] = note
        serverNoteList[strID]["name"][noteNum] = member.name
        serverNoteList[strID]["time"][noteNum] = str(datetime.now())
        serverNoteList[strID]["issuer"][noteNum] = str(ctx.author.id)
        serverNoteList[strID]["issuerName"][noteNum] = ctx.author.name
        util.save_js(path, serverNoteList)
        await ctx.send("Your note has been recorded.")

    @commands.command(pass_context=True)
    async def listNote(self, ctx, member : discord.Member, *, note : str = None):
        "Lists all notes for a given user."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to " + 
                            "run this command.")
            return

        path = opj(self.JSON_PATH, "note-%s.json" % ctx.guild.id)
        serverNoteList = util.load_js(path)
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
            await self.bot.say(loggedIssuerName+" made a note about "+loggedName+" on "+loggedTime+" that said"+loggedNote+"`")
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

def setup(bot):
    config = util.load_js("config.json")
    bot.add_cog(Moderator(bot, config))
