import asyncio
import discord
import requests
import random
import os
import time
import multiprocessing as mp
import util

from os.path import join as opj
from discord.ext import commands

from cogs.base import Base

class RandomStuff(Base):
    def __init__(self, bot):
        self.fanfics = util.load_js(opj("assets", "fanfics.json"))
        self.ramResponses = util.load_js(opj("assets", "ram.json"))
        super().__init__(bot)

    @commands.command()
    async def setRateRandomization(self, ctx, makeRandom : bool):
        "Determine how BepisBot assigns scores for the rate command."
        perms = ctx.author.permissions_in(ctx.channel)
        if not perms.manage_guild:
            await ctx.send("You need the \"Manage Server\" permission to" +
                            "run this command.")
            return

        key = "rateRandomized:%s" % ctx.guild.id

        if makeRandom:
            await self.bot.rconn.set(key, "1")
            await ctx.send("%srate will now use randomized scores." % 
                            self.bot.command_prefix)
        else:
            await self.bot.rconn.set(key, "0")
            await ctx.send("%srate will now use scores based on ASCII values." %
                            self.bot.command_prefix)

    @commands.command()
    async def rate(self, ctx, something : str):
        "Rate anything, on a scale from 0 to 10."
        rating = 0

        if self.bot.user in ctx.message.mentions:
            await ctx.send(":thinking: I'd give myself a 10 out of 10.")
            return

        key = "rateRandomized:%s" % ctx.guild.id
        randomizeScore = await self.bot.rconn.get(key)

        if randomizeScore == "1":
            rating = random.randint(0, 10)
        else:
            for char in something:
                a_value = ord(char) % 10
                rating += a_value
            rating %= 10

        highRatingsPeople = [
            "162357148540469250",
            "164761117544022016"
        ]

        # special cases
        for mention in ctx.message.mentions:
            if str(mention.id) in highRatingsPeople:
                rating = 10

        if rating == 8:
            word = "an"
        else:
            word = "a"

        await ctx.send(":thinking: I'd give %s %s %s out of 10." % \
                            (something, word, rating))

    # TODO: work on refactoring this, get around the character limit
    # This will also involved work on the JSON file.
    @commands.command()
    async def ship(self, ctx, mem1 : str, mem2 : str):
        "Ship two people together to create a fanfiction.  NSFW."
        fanfic = random.choice(self.fanfics)
        for fLine in fanfic:
            await ctx.trigger_typing()
            await asyncio.sleep(1.5)

            msgFormatted = fLine.format(mem1, mem2)
            await ctx.send(msgFormatted)    

    @commands.command()
    async def pat(self, ctx, member : discord.Member):
        "Pat someone on the head~"
        await ctx.trigger_typing()

        adjectives = ["gently", "lightly", "meekly"]
        adjToUse = random.choice(adjectives)

        if member == self.bot.user:
            await ctx.send("*pats myself on head*")
        else:
            await ctx.send("*%s pats %s on the head*" % \
                    (adjToUse, member.mention))

    @commands.command()
    async def downloadMoreRAM(self, ctx, memorySize : int = 16):
        "Slow computer? Just use this command to speed it up!"
        msg = await ctx.send(":thumbsup: Alright, downloading " + 
                            "{} GB of RAM...  0%".format(memorySize))
        for i in range(1, 100, 15):
            await msg.edit(content = (":thumbsup: Alright, downloading {}GB " +
             "of RAM...  {}%").format(memorySize, i))
            await asyncio.sleep(1)

        # we have a bunch of RAM flavor text stored in the JSON file
        text = random.choice(self.ramResponses)

        # this is to get the command to work in DMs
        if ctx.guild == None:
            identifier = ctx.author.id
        else:
            identifier = ctx.guild.id

        filename = opj(self.TEMP_PATH, "%s-%s.txt" % \
                    (identifier, time.time()))

        with open(filename, "w+") as f:
            f.write(text)
            f.close()

        with open(filename, "r+") as f:
            ram = discord.File(f, filename = "RAM.txt")
            await msg.edit(content = (":thumbsup: Alright, downloading {}GB " +
             "of RAM...  100%").format(memorySize))
            await ctx.send("OK, your RAM is ready!", file = ram)
            f.close()
        os.remove(filename)

    @commands.command()
    async def kill(self, ctx, member : str):
        "kill all of your friends"

        # The "@everyone" thing is a loophole left open for anyone who wants
        # to see the result of doing an @everyone without pinging the entire
        # server.  Don't change it, it's intentional.
        if ctx.message.mention_everyone or "@everyone" in ctx.message.content:
            await ctx.send(":boom::gun: Welp, %s killed everyone, the absolute \
                            madman." % (ctx.message.author.mention))
            return

        offender = ctx.author.mention
        victims = ctx.message.mentions

        if len(victims) == 0:
            raise commands.errors.BadArgument

        # special kill blacklist for Bepis, trainboy, and Dionicio3
        invincibles = ["162357148540469250", 
                        "191238543828451329", 
                        "172898048702283776"]

        for victim in victims:
            if ctx.message.author.id == victim.id:
                if random.randint(1, 100) == 42:
                    await ctx.send(":boom::gun: **%s**, you summoned your Persona!" \
                                    % (offender))
                else:
                    await ctx.send(":boom::gun: **%s**, you killed yourself!" \
                                    % (offender))
            elif victim.id == self.bot.user.id:
                await ctx.send(":boom::gun: **%s**, you killed me!  Not cool!" \
                                    % (offender))
            elif victim.id in invincibles:
                await ctx.send("Hey **%s**, can\'t touch this!" \
                                    % (offender))
            else:
                await ctx.send(":boom::gun: **%s**, you have been killed \
                                 by **%s**!" % (victim.mention, offender))

    @commands.command()
    async def soon(self, ctx):
        "Any year now. Really."
        if random.randint(1, 25) == 13:
            fil = "uu"
        else:
            fil = "oo"
            
        await ctx.send("S{}n:tm:".format(fil))

    @commands.command()
    async def no(self, ctx):
        "No."
        if random.randint(1, 25) == 13:
            fil = "no u"
        else:
            fil = "no"
            
        await ctx.send(fil)

    @commands.command()
    async def maybe(self, ctx):
        "Maybe."
        if random.randint(1, 1337) == 420:
            await ctx.send("most definitely")
        else:
            await ctx.send("maybe")
        
def setup(bot):
    bot.add_cog(RandomStuff(bot))
