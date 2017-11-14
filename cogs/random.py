import asyncio
import discord
import requests
import random
import os
import util

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from discord.ext import commands

from cogs.base import Base

class RandomStuff(Base):
    @commands.command(pass_context = True)
    async def art(self, ctx, member : discord.Member):
        """?"""

        await self.bot.send_typing(ctx.message.channel)

        finalImage = Image.new("RGBA", (811, 444), "white")
        frameImage = Image.open(os.path.join("assets", "Art.png"))

        url = member.avatar_url
        if url == "":
            url = member.default_avatar_url

        print(url)
        data = requests.get(url)

        with open(os.path.join("cache", "{}.webp".format(member.id)), "wb+") as f:
            f.write(data.content)
            f.close()

        profileImage = Image.open(os.path.join("cache", "{}.webp".format(member.id)))
        profileImage = profileImage.resize((300,300))

        finalImage.paste(profileImage, (290,155))
        finalImage.paste(frameImage, (0,0), frameImage)
        finalImage.save("temp.png", "PNG")

        await self.bot.send_file(ctx.message.channel, "temp.png")
    
    @commands.command(pass_context = True)
    async def wanted(self, ctx, member : discord.Member, text : str = "5000"):
        """?"""

        await self.bot.send_typing(ctx.message.channel)
        glitcher=False

        finalImage = Image.new("RGBA", (764, 997), "white")
        frameImage = Image.open(os.path.join("assets", "wanted.png")).convert("RGBA")
        if text == None:
            text="5,000"
        text=text.replace(",", "")
        try:
            x=int(text)
            if x<1000000 and x>-100000:
                text="{:,}".format(int(text))
            else:
                glitcher=True
                text="999,999"
        except:
            glitcher=True
            print(text+" NO")
            text="999,999"
        line="$"+text+" REWARD"
        font  = ImageFont.truetype(os.path.join("assets","RodeoClown.ttf"), 83)
        url = member.avatar_url
        if url == "":
            url = member.default_avatar_url

        print(url)
        if glitcher==True:
            url=ctx.message.author.avatar_url
        data = requests.get(url)

        with open(os.path.join("cache", "{}.webp".format(member.id)), "wb+") as f:
            f.write(data.content)
            f.close()

        profileImage = Image.open(os.path.join("cache", "{}.webp".format(member.id)))
        profileImage = profileImage.resize((500,500))

        finalImage.paste(frameImage, (0,0), frameImage)
        finalImage.paste(profileImage, (123,298))
        draw  = ImageDraw.Draw(finalImage)
        w,h=draw.textsize(line, font=font)
        draw.multiline_text((((681-w)/2)+42, 806), line, (0, 0, 0), font=font, align="left")
        finalImage.save("wantedTemp.png", "PNG")

        await self.bot.send_file(ctx.message.channel, "wantedTemp.png")

    @commands.command(pass_context = True, hidden = True)
    async def quote(self, ctx):
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
    async def fidgetSpinner(self, ctx, *, line : str = None):
        """hahaha dead meme"""
        # font found here: http://www.fontspace.com/jake-luedecke-motion-and-graphic-design/ldfcomicsans
        # code based off this: https://stackoverflow.com/questions/25255206/alternatives-to-pil-pillow-for-overlaying-an-image-with-text#25255348
        await self.bot.send_typing(ctx.message.channel)
        POSSIBLE_LINES = [    "vsssssssssshhhhhhh",
                    "spinning to winning",
                    "end my life",
                    "God is dead and we killed him",
                    "go away mom i'm FIDGET SPINNING",
                    "download FidgetSpinner3DS by B_E_P_I_S_M_A_N",
                    "cancer",
                    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                ]
        if line == None:
            line = POSSIBLE_LINES[random.randint(0, len(POSSIBLE_LINES) - 1)]

        image = Image.open(os.path.join("assets", "fidgetspinner.jpg"))
        draw  = ImageDraw.Draw(image)
        font  = ImageFont.truetype(os.path.join("assets","comicsans.ttf"), 50)

        draw.text((10, 10), line, (0, 255, 0), font=font)
        image.save("fidgetspinner.png")

        await self.bot.upload("fidgetspinner.png")

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

        if rating == 8:
            word = "an"
        else:
            word = "a"

        await self.bot.say(":thinking: I'd give {} {} {} out of 10.".format(thing, word, rating))

    @commands.command()
    async def ship(self, mem1 : str, mem2 : str):
        """Ship two people together to create a fanfiction.  Slightly disturbing material may arise out of this.  You have been warned."""
        fanfics = util.load_js("cogs/fanfics.json")

        message = fanfics[random.randint(0, len(fanfics) - 1)]
        msgFormatted = message.format(mem1, mem2)
        print(msgFormatted)
        await self.bot.say(msgFormatted)

    @commands.command()
    async def downloadMoreRAM(self, memorySize : int = 16):
        msg = await self.bot.say(":thumbsup: Alright, downloading {}GB of RAM...  0%".format(memorySize))
        for i in range(1, 100, 15):
            await self.bot.edit_message(msg, ":thumbsup: Alright, downloading {}GB of RAM...  {}%".format(memorySize, i))
            asyncio.sleep(1)

        await self.bot.edit_message(msg, ":thumbsup: Alright, downloading {}GB of RAM...  100%".format(memorySize))
        await self.bot.say("OK, your RAM is ready!")
        await self.bot.upload( os.path.join("assets", "RAM") )  

    @commands.command()
    async def dioTest(self):
        await self.bot.say("Just a test -Dionicio3")

    @commands.command(pass_context = True)
    async def kill(self, ctx, member = None):
        """kys"""
        if ctx.message.mention_everyone or "@everyone" in ctx.message.content:
            await self.bot.say(":boom::gun: Welp, {} killed everyone, the absolute madman.".format(ctx.message.author.mention))
            return

        if member == None:
            await self.bot.say("Please specify a member!")
            return

        offender = ctx.message.author.mention
        victims = ctx.message.mentions

        for victim in victims:
            if ctx.message.author.id == victim.id:
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
            else:
                await self.bot.say(":boom::gun: **{}**, you have been killed by **{}**!".format(victim.mention, offender))

    @commands.command()
    async def soon(self):
        """shitty hacker meme"""
        if random.randint(1, 25) == 13:
            fil = "uu"
        else:
            fil = "oo"
            
        await self.bot.say("S{}n:tm:".format(fil))



    @commands.command()
    async def wantedTest(self, ctx, member : discord.Member, text : str = "5000"):
        """?"""
        await self.bot.send_typing(ctx.message.channel)
        glitcher=False
        reasonBool=False
        finalImage = Image.new("RGBA", (764, 997), "white")
        frameImage = Image.open(os.path.join("assets", "wanted.png")).convert("RGBA")
        if text == None:
            text="5,000"
        splitter=text.split(" ",1)
        text=splitter[0]
        try:
            reason=splitter[1]
            reasonBool=true
        except:
            reasonBool=False
        text=text.replace(",", "")
        try:
            x=int(text)
            if x<1000000 and x>-100000:
                text="{:,}".format(int(text))
            else:
                glitcher=True
                text="999,999"
        except:
            glitcher=True
            print(text+" NO")
            text="999,999"
            reason="Trying to break the system."
            reasonBool=True
        line="$"+text+" REWARD"
        fontA  = ImageFont.truetype(os.path.join("assets","RodeoClown.ttf"), 83)
        fontB  = ImageFont.truetype(os.path.join("assets","Nashville.ttf"), 44)
        url = member.avatar_url
        if url == "":
            url = member.default_avatar_url

        print(url)
        if glitcher==True:
            url=ctx.message.author.avatar_url
        data = requests.get(url)

        with open(os.path.join("cache", "{}.webp".format(member.id)), "wb+") as f:
            f.write(data.content)
            f.close()

        profileImage = Image.open(os.path.join("cache", "{}.webp".format(member.id)))
        profileImage = profileImage.resize((500,500))

        finalImage.paste(frameImage, (0,0), frameImage)
        if reasonBool==True:
            finalImage.paste(profileImage, (123,277))
        else:
            finalImage.paste(profileImage, (123,298))
        draw  = ImageDraw.Draw(finalImage)
        draw2=ImageDraw.Draw(finalImage)
        w,h=draw.textsize(line, font=font)
        if reasonBool==True:
            w2,h2=draw.textsize(reason, font=fontB)
            draw.multiline_text((((681-w)/2)+42, 785), line, (0, 0, 0), font=fontA, align="left")
            draw2.multiline_text((((681-w2)/2)+42, 865), reason, (0, 0, 0), font=fontB, align="left")
        else:
            draw.multiline_text((((681-w)/2)+42, 806), line, (0, 0, 0), font=fontA, align="left")

        finalImage.save("wantedTemp.png", "PNG")

        await self.bot.send_file(ctx.message.channel, "wantedTemp.png")
        
        
def setup(bot):
    bot.add_cog(RandomStuff(bot))
