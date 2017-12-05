import asyncio
import discord
import os
from discord.ext import commands
from datetime import datetime
import hashlib

import util
import cogs.base as base

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

    @commands.command(pass_context = True)
    async def kick(self, ctx, member : discord.Member):
        """Kick a member from a server.  This requires special perms."""
        perms = await util.check_perms(self, ctx)
        print(perms)
        if (perms):
            try:
                await self.bot.kick(member)
                await self.bot.say("{} has been kicked from the server.".format(member.name))
            except:
                await self.bot.say("Could not kick member.  This might be a permissions issue.")

    @commands.command(pass_context = True)
    async def unwarn(self, ctx, member : discord.Member, amount : int = 1):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        serverWarnList = util.load_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)))
        if member.id not in serverWarnList or serverWarnList[member.id] <= 0:
            await self.bot.say("{} does not currently have any warns".format(member.name))
            return

        if amount > self.MAXWARNS:
            amount = self.MAXWARNS

        serverWarnList[member.id] -= amount
        await self.bot.say("<@!{}>, you have had {} warns removed.  {} warnings remain.".format(member.id, amount, self.MAXWARNS - serverWarnList[member.id]))
        util.save_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)), serverWarnList)

    @commands.command(pass_context = True)
    async def warn(self, ctx, member : discord.Member):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return

        serverWarnList = util.load_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)))

        if member.id not in serverWarnList:
            serverWarnList[member.id] = 0
        serverWarnList[member.id] += 1

        if self.MAXWARNS - serverWarnList[member.id] > 1:
            await self.bot.say("<@!{}>, you have been given a warning.  You have {} warnings left.".format(member.id, self.MAXWARNS - serverWarnList[member.id]))
        elif serverWarnList[member.id] >= self.MAXWARNS:
            pass
        else:
            await self.bot.say("<@!{}>, this is your final warning.  One more warn and you will be banned.".format(member.id))
        util.save_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)), serverWarnList)

        if serverWarnList[member.id] >= self.MAXWARNS:
            await self.bot.ban(member)
            await self.bot.say("<@!{}> has been banned from the server for getting {} warnings.".format(member.id, self.MAXWARNS))

    @commands.command(pass_context=True)
    async def listWarns(self, ctx, member : discord.Member):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        serverWarnList = util.load_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)))
        if member.id not in serverWarnList or serverWarnList[member.id]==0:
            await self.bot.say("<@!{}> does not currently have any warns.".format(member.id))
        elif serverWarnList[member.id]>=self.MAXWARNS:
            await self.bot.say("<@!{}> recieved ".format(member.id)+str(self.MAXWARNS)+" warnings and was banned.")
        else:
            await self.bot.say("<@!{}> currently has ".format(member.id)+str(serverWarnList[member.id])+" warnings. They will be banned if they recieve "+str(self.MAXWARNS-serverWarnList[member.id])+" more.")


    @commands.command(pass_context=True)
    async def note(self, ctx, member : discord.Member, *, note : str = None):
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
                output+="<@!{}> ".format(member.id)+str(serverNoteList[member.id]["time"][str(i)])+" "+str(serverNoteList[member.id]["issuer"][str(i)])+" "+str(serverNoteList[member.id]["note"][str(i)])+"\n"
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
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        await self.bot.delete_message(ctx.message)
        if note == None:
            await self.bot.say("Please provide a note number.")
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        if member.id not in serverNoteList or serverNoteList[member.id]["noteNum"]==0:
            await self.bot.say("That user doesn't have any notes.")
            return
        noteNum=str(serverNoteList[member.id]["noteNum"])
        if note>noteNum:
            await self.bot.say("That user doesn't have that many notes.")
            return
        for i in range(int(note),serverNoteList[member.id]["noteNum"]):
            try:
                serverNoteList[member.id]["note"][i]=serverNoteList[member.id]["note"][i+1]
                serverNoteList[member.id]["name"][i]=serverNoteList[member.id]["name"][i+1]
                serverNoteList[member.id]["time"][i]=serverNoteList[member.id]["time"][i+1]
                serverNoteList[member.id]["issuer"][i]=serverNoteList[member.id]["issuer"][i+1]
                serverNoteList[member.id]["issuerName"][i]=serverNoteList[member.id]["issuerName"][i+1]
            except KeyError:
                serverNoteList[member.id]["noteNum"]-=1
                util.save_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)), serverNoteList)
                return

    @commands.command(pass_context=True)
    async def allNote(self,ctx):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        for item in serverNoteList:
            await self.bot.say(str(item))
            for i in range(1,serverNoteList[item]["noteNum"]+1):
                await self.bot.say(serverNoteList[member.id]["name"][i])
                await self.bot.say(serverNoteList[member.id]["time"][i])
                await self.bot.say(serverNoteList[member.id]["issuerName"][i])
                await self.bot.say(serverNoteList[member.id]["issuer"][i])
                await self.bot.say(serverNoteList[member.id]["note"][i])
                await self.bot.say()
            await self.bot.say()

    @commands.command(pass_context=True)
    async def backupNote(self,ctx):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        await self.bot.say(serverNoteList)

    @commands.command(pass_context=True)
    async def hashNote(self,ctx):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
        hashed=hashlib.sha256(str(serverNoteList).encode("utf-8")).hexdigest()
        await self.bot.send(hashed)

    @commands.command(pass_context=True)
    async def wipeNote(self, ctx, *, confirm : str = None):
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        if ctx.message.author.id == self.bot.user.id:
            return
        serverNoteList = load_js(os.path.join("notes", "{}.json".format(x)))
        key=hashlib.sha256(str(serverNoteList).encode("utf-8")).hexdigest()
        if confirm==key:
            serverNoteList={}
            save_js(os.path.join("notes", "{}.json".format(x)), serverNoteList)
            await self.bot.say("All notes have been wiped.")
            return
        else:
            await self.bot.say("To wipe the notes, you must enter the correct key.")
            return


def setup(bot):
    config = util.load_js("config.json")
    bot.add_cog(Moderator(bot, config))
