import asyncio
import discord
import requests
import random
import os
import time
import multiprocessing as mp
import util

from os.path import join as opj

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from discord.ext import commands

from cogs.base import Base

class RandomStuff(Base):
    @commands.command(pass_context = True)
    async def rate(self, ctx):
        """Rate anything, on a scale frrom 0 to 10."""
        rating = 0

        thing = ctx.message.content[len(ctx.prefix) + len(ctx.command.name) + 1:]
        for char in thing:
            a_value = ord(char) % 10
            rating += a_value
        rating %= 10

        # special cases
        if "162357148540469250" in thing.lower():
            rating = 420
        elif "persona 3" in thing.lower():
            rating = 10
        elif "kingy" in thing.lower():
            rating = "gey"
        elif "197244770626568193" in thing.lower():
            rating = "gey"
        elif "164761117544022016" in thing.lower():
            rating = 69
        elif "gnmmarechal" in thing.lower():
            rating = 69
        elif "gnmpolicemata" in thing.lower():
            rating = 69

        if rating == 8:
            word = "an"
        else:
            word = "a"

        await self.bot.say(":thinking: I'd give %s %s %s out of 10." % \
                            (thing, word, rating))

    @commands.command()
    async def ship(self, mem1 : str, mem2 : str):
        util.nullifyExecute()
        """Ship two people together to create a fanfiction.  Slightly disturbing material may arise out of this.  You have been warned."""
        fanfics = util.load_js("cogs/fanfics.json")

        message = fanfics[random.randint(0, len(fanfics) - 1)]
        msgFormatted = message.format(mem1, mem2)
        print(msgFormatted)
        await self.bot.say(msgFormatted)

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
        ramList = util.load_js(opj("assets", "ram.json"))
        text = random.choice(ramList)

        filename = opj(self.TEMP_PATH, "%s-%s.txt" % \
                    (ctx.guild.id, time.time()))

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
    async def kill(self, ctx, member : discord.Member):
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
        
def setup(bot):
    bot.add_cog(RandomStuff(bot))
