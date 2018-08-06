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


    @commands.command(pass_context=True)
    async def hug(self, ctx, *, target : str = ""):
        await self.bot.send_typing(ctx.message.channel)
        """Hug ya friends"""
        ctx=util.execute(self,ctx)
        titles = ["hugs", "aww", "yay", "huggie hug"]
        pics = util.load_js(os.path.join("assets", "hug.json"))
        memberID = target.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        member = ctx.message.server.get_member(memberID)
        if member != None:
            target = member.name

        if self.bot.user.id==ctx.message.author.id:
            d = "I hugged myself!"
        elif ctx.message.author.id == memberID:
            d = "{} hugged themselves.".format(target)
        elif self.bot.user.id == memberID:
            d = "{} hugged me!".format(ctx.message.author.name)
        elif member == None and target == "":
            d = "hugs"
        else:
            d = "{} got hugged by {}.".format(target, ctx.message.author.name)
        i=random.randint(0,len(pics)-1)
        urlText = pics[i]
        titleText = random.choice(titles)
        if urlText=="https://i.imgur.com/oQ8J3Za.gif":
            titleText="oops"
            if self.bot.user.id==ctx.message.author.id:
                d = "I got pizza!"
            elif ctx.message.author.id == memberID:
                d = "{} got pizza.".format(target)
            elif self.bot.user.id == memberID:
                d = "{} gave me pizza!".format(ctx.message.author.name)
            elif member == None and target == "":
                d = "pizza"
            else:
                d = "{} gave {} pizza.".format(ctx.message.author.name, target)
        if urlText=="https://i.imgur.com/MnszwT3.gif":
            titleText="no"
            if self.bot.user.id==ctx.message.author.id:
                d = "I didn't want to hug myself"
            elif ctx.message.author.id == memberID:
                d = "{} didn't want the hug.".format(target)
            elif self.bot.user.id == memberID:
                d = "{} didn't want my hugs! ;-;".format(ctx.message.author.name)
            elif member == None and target == "":
                d = "no"
            else:
                d = "{} didn't want {}'s hug.".format(target, ctx.message.author.name)
        e = discord.Embed(title=titleText, description = d)
        e.set_image(url=urlText)
        await self.bot.say(embed = e)

    @commands.command(pass_context=True)
    async def addHug(self, ctx, *, url : str = ""):
        util.nullifyExecute()
        perms = await util.check_perms(self, ctx)
        if not perms:
            return
        pics = util.load_js(os.path.join("assets", "hug.json"))
        if url == "":
            await self.bot.say("Please provide a url.")
        elif not url.startswith("http"):
            await self.bot.say("Please provide a valid url.")
        elif url.startswith("https://i.imgur.com/"):
            pics.append(url)
            util.save_js("assets/hug.json",pics)
            await self.bot.say("Successfully added "+link+" to hugs.json")
        else:
            try:
                payload={"image":url,"type":"URL"}
                headers = {"Authorization": "Client-ID 2397de93cc488b8"}
                r=requests.post("https://api.imgur.com/3/image",headers=headers,data=payload)
                link=r.json()["data"]["link"]
                pics.append(link)
                util.save_js("assets/hug.json",pics)
                await self.bot.say("Successfully added "+link+" to hugs.json")
            except:
                await self.bot.say("nope")


    
    @commands.command(pass_context = True)
    async def beanUnregister(self, ctx):
        util.nullifyExecute()
        if os.path.isfile(os.path.join("assets","bean.json")):
            beanlist = util.load_js(os.path.join("assets", "bean.json"))
        else:
            await self.bot.say("**{}**, you aren't on the beanlist.".format(ctx.message.author.mention))
            return
        for user in beanlist:
            if str(ctx.message.author.id) == str(user["id"]):
                beanlist.remove(user)
                util.save_js("assets/bean.json", beanlist)
                await self.bot.say("**{}**, you have been removed from beanlist.".format(ctx.message.author.mention))
                return
        await self.bot.say("{}, you aren't on the beanlist.".format(ctx.message.author.name))

    @commands.command(pass_context = True)
    async def beanRegister(self, ctx):
        util.nullifyExecute()
        if os.path.isfile(os.path.join("assets","bean.json")):
            beanlist = util.load_js(os.path.join("assets", "bean.json"))
        else:
            beanlist=[]
        for user in beanlist:
            if str(ctx.message.author.id) == str(user["id"]):
                await self.bot.say("{} is already in the beanlist.".format(ctx.message.author.name))
                return
        beanlist.append( {"id" : ctx.message.author.id} )
        util.save_js("assets/bean.json", beanlist)
        await self.bot.say("**{}**, you have been added to the beanlist.".format(ctx.message.author.mention))
        
    @commands.command(pass_context = True)
    async def bean(self, ctx, *, user : str = ""):
        await self.bot.send_typing(ctx.message.channel)
        ctx=util.execute(self,ctx)
        whitelist=[]
        beans=False
        imageUrl="https://i.imgur.com/sncYgfx.png"
        memberID = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        member = ctx.message.server.get_member(memberID)
        if os.path.isfile(os.path.join("assets","bean.json")):
            beanlist = util.load_js(os.path.join("assets", "bean.json"))
            beans=True
        else:
            beans=False
        if member:
            if beans:
                for userList in beanlist:
                    if str(memberID) == str(userList["id"]):
                        imageUrl="https://i.imgur.com/oBadUcY.gif"
            user=member.name
            if self.bot.user.id==ctx.message.author.id:
                title = "I beaned myself"
                description = "Why did I do that?"
            elif member is ctx.message.author:
                title = "Ya done beaned urself"
                description = "{} beaned themselves!".format(ctx.message.author.name)
            elif self.bot.user.id == memberID:
                title = "aw  :("
                description = "{} beaned me.".format(ctx.message.author.name)
            else:
                title = "Uh oh!"
                description = "{} got beaned by {}!".format(user, ctx.message.author.name)
        else:
            title = "Uh oh!"
            description = "{} got beaned by {}!".format(user, ctx.message.author.name)
        embed = discord.Embed()
        embed.title = title
        embed.description = description
        embed.set_image(url = imageUrl)
        await self.bot.say(embed=embed)
        
    
    
    @commands.command(pass_context = True)
    async def pat(self, ctx, member : discord.Member):
        util.nullifyExecute()
        await self.bot.send_typing(ctx.message.channel)
        adjectives = ["gently", "lightly", "meekly"]
        adjToUse = random.choice(adjectives)
        if member == self.bot.user:
            await self.bot.say("*pats myself on head*")
        else:
            await self.bot.say("*{} pats <@!{}> on the head*".format(adjToUse, member.id))
    


    @commands.command(pass_context = True, hidden = True)
    async def quote(self, ctx):
        util.nullifyExecute()
        "Chary's server only.  Picks a quote from TempGenie.  Used when TempGenie is down."
        if ctx.message.server.id != "329063968570081281":
            return
    
        data = requests.get("https://raw.githubusercontent.com/gnmmarechal/TempGenie/master/quotes.txt").content

        # properly format the data, then split it into a list of quotes
        data = str(data)
        data = data.replace("\\r", "")
        data = data.split("\\n")
    
        # pick a quote
        chosenQuote = random.choice(data)        
        await self.bot.say(chosenQuote)



    @commands.command(pass_context = True)
    async def rate(self, ctx):
        ctx=util.execute(self,ctx)
        await self.bot.send_typing(ctx.message.channel)
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

        await self.bot.say(":thinking: I'd give {} {} {} out of 10.".format(thing, word, rating))

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
    async def downloadMoreRAM(self, memorySize : int = 16):
        util.nullifyExecute()
        msg = await self.bot.say(":thumbsup: Alright, downloading {}GB of RAM...  0%".format(memorySize))
        for i in range(1, 100, 15):
            await self.bot.edit_message(msg, ":thumbsup: Alright, downloading {}GB of RAM...  {}%".format(memorySize, i))
            asyncio.sleep(1)

        await self.bot.edit_message(msg, ":thumbsup: Alright, downloading {}GB of RAM...  100%".format(memorySize))
        await self.bot.say("OK, your RAM is ready!")
        await self.bot.upload( os.path.join("assets", "RAM") )  

    @commands.command()
    async def dioTest(self):
        util.nullifyExecute()
        await self.bot.say("Just a test -Dionicio3")

    @commands.command(pass_context = True)
    async def kill(self, ctx, member = None):
        """kys"""
        backup=ctx.message.author.mention
        ctx=util.execute(self,ctx)
        if ctx.message.mention_everyone and self.bot.user.id==ctx.message.author.id or "@everyone" in ctx.message.content and self.bot.user.id==ctx.message.author.id:
            await self.bot.say(":boom::gun: I just killed everyone! Does that really suprise anyryone?")
        elif ctx.message.mention_everyone or "@everyone" in ctx.message.content:
            await self.bot.say(":boom::gun: Welp, {} killed everyone, the absolute madman.".format(ctx.message.author.mention))
            return

        if member == None:
            if self.bot.user.id==ctx.message.author.id:
                await self.bot.say(":boom::gun: **{}**, you have been killed by me!".format(backup.message.author.mention))
            await self.bot.say("Please specify a member!")
            return

        offender = ctx.message.author.mention
        victims = ctx.message.mentions

        for victim in victims:
            if self.bot.user.id==ctx.message.author.id:
                if ctx.message.author.id == victim.id:
                    if random.randint(1, 100) == 42:
                        await self.bot.say(":boom::gun: I summoned your Persona!")
                    else:
                        await self.bot.say(":boom::gun: I killed myself!")
                elif victim.id == "162357148540469250":
                    await self.bot.say("I can\'t touch this, **{}**!".format(backup))
                elif victim.id == "191238543828451329":
                    await self.bot.say("I can\'t touch this, **{}**!".format(backup))
                elif victim.id == "172898048702283776":
                    await self.bot.say("I can\'t touch this, **{}**!".format(backup))
                else:
                    await self.bot.say(":boom::gun: **{}**, you have been killed by me!".format(victim.mention))
            elif ctx.message.author.id == victim.id:
                if random.randint(1, 100) == 42:
                    await self.bot.say(":boom::gun: **{}**, you summoned your Persona!".format(offender))
                else:
                    await self.bot.say(":boom::gun: **{}**, you killed yourself!".format(offender))
            elif victim.id == self.bot.user.id:
                await self.bot.say(":boom::gun: **{}**, you killed me!  Not cool bro".format(offender))
            elif victim.id == "162357148540469250":
                await self.bot.say("Hey **{}**, can\'t touch this!".format(offender))
            elif victim.id == "191238543828451329":
                await self.bot.say("Hey **{}**, can\'t touch this!".format(offender))
            elif victim.id == "172898048702283776":
                await self.bot.say("Hey **{}**, can\'t touch this!".format(offender))
            else:
                await self.bot.say(":boom::gun: **{}**, you have been killed by **{}**!".format(victim.mention, offender))

    @commands.command()
    async def soon(self):
        util.nullifyExecute()
        """shitty hacker meme"""
        if random.randint(1, 25) == 13:
            fil = "uu"
        else:
            fil = "oo"
            
        await self.bot.say("S{}n:tm:".format(fil))

    @commands.command()
    async def no(self):
        util.nullifyExecute()
        """no"""
        if random.randint(1, 25) == 13:
            fil = "no u"
        else:
            fil = "no"
            
        await self.bot.say(fil)

    @commands.command()
    async def maybe(self):
        util.nullifyExecute()
        if random.randint(1, 1337) == 420:
            await self.bot.say("most definitely")
        else:
            await self.bot.say("maybe")

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
