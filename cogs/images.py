import asyncio
import discord
import requests
import os
import time
import random
import multiprocessing as mp
import util

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from discord.ext import commands
from cogs.base import Base
from os.path import join as opj

class Images(Base):
    def __init__(self, bot):
        self.slapPics = util.load_js(opj("assets", "slap.json"))
        self.punchPics = util.load_js(opj("assets", "punch.json"))
        self.hugPics = util.load_js(opj("assets", "hug.json"))

        self.slapTitles =  ["oof", "ouch", "owie", "ouchie ouch", "ow"]

        super().__init__(bot)

    # Helper function for downloading a Discord member's avatar.
    # Used for some image commands.
    def getMemberAvatar(self, member : discord.Member = None, url : str = None):
        if url == None:
            url = member.avatar_url
            if url == "":
                url = member.default_avatar_url

        data = requests.get(url)
        path = opj(self.TEMP_PATH, "%s.webp" % (member.id))

        with open(path, "wb+") as f:
            f.write(data.content)
            f.close()

        return path

    # Helper function for determining temporary file names.
    # Used to get certain commands to work in DMs.
    def getIdentifier(self, ctx):
        if ctx.guild == None:
            return ctx.author.id
        else:
            return ctx.guild.id

    # Helper functions for processing images.  Run as separate processes
    # to prevent the bot from being bogged down in other channels/servers.
    def artProcess(self, member : discord.Member, filename : str):
        finalImage = Image.new("RGBA", (811, 444), "white")
        frameImage = Image.open(opj("assets", "Art.png"))

        data = requests.get(member.avatar_url)

        with open(opj(self.TEMP_PATH, "%s.webp" % (member.id)), "wb+") as f:
            f.write(data.content)
            f.close()

        avPath = self.getMemberAvatar(member = member)
        profileImage = Image.open(avPath)
        profileImage = profileImage.resize((300,300))

        finalImage.paste(profileImage, (290,155))
        finalImage.paste(frameImage, (0,0), frameImage)
        finalImage.save(filename, "PNG")

        os.remove(avPath)

    def wantedProcess(self, member : discord.Member, ctx : commands.Context, 
                            amount : int, reason : str, filename : str, 
                            backup : str):
        finalImage = Image.new("RGBA", (764, 997), "white")
        frameImage = Image.open(os.path.join("assets", "wanted.png")).convert("RGBA")
        draw = ImageDraw.Draw(finalImage)
        
        fontA  = ImageFont.truetype(opj("assets","RodeoClown.ttf"), 83)
        fontB  = ImageFont.truetype(opj("assets","Nashville.ttf"), 44)

        url = None

        # make sure the user isn't entering in an ungodly amount
        if not (-100000 < amount < 1000000):
            url = ctx.author.avatar_url
            amount = 999999
            reason = "trying to break the system"

        # make sure the reason provided isn't too long
        elif reason != None:
            reason = reason.lower()
            w2,h2 = draw.textsize(reason, font=fontB)
            if w2 > 670:
                url = ctx.author.avatar_url
                amount = 999999
                reason = "Giving a long reason"

        # in case the user is trying to frame the bot
        elif self.bot.user == member:
            url = ctx.author.avatar_url
            amount = 999999
            reason = "Trying to frame me!"
            
        line = "$%i REWARD" % (amount)
        avPath = self.getMemberAvatar(member, url)
        profileImage = Image.open(avPath)
        profileImage = profileImage.resize((500,500))

        finalImage.paste(frameImage, (0,0), frameImage)
        finalImage.paste(profileImage, (123,277))
        draw = ImageDraw.Draw(finalImage)
        
        w,h = draw.textsize(line, font=fontA)
        draw.multiline_text((((681-w)/2)+42, 785), line, (0, 0, 0), \
                font = fontA, align = "left")
        if reason != None:
            w2,h2=draw.textsize(reason, font = fontB)
            draw.multiline_text((((681-w2)/2)+42, 865), reason, (0, 0, 0), \
                    font = fontB, align = "left")

        finalImage.save(filename, "PNG")
        os.remove(avPath)

    def fsProcess(self, line : str, filename : str):
        # font found here: 
        # http://www.fontspace.com/jake-luedecke-motion-and-graphic-design/ldfcomicsans
        # code based off this: 
        # https://stackoverflow.com/questions/25255206/alternatives-to-pil-pillow-for-overlaying-an-image-with-text#25255348
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

        image = Image.open(opj("assets", "fidgetspinner.jpg"))
        draw  = ImageDraw.Draw(image)
        font  = ImageFont.truetype(opj("assets","comicsans.ttf"), 50)

        draw.text((10, 10), line, (0, 255, 0), font=font)
        image.save(filename)

    # end of helper functions

    @commands.command()
    async def art(self, ctx, member : discord.Member):
        "Turns any profile picture into a work of art."

        await ctx.trigger_typing()
        url = member.avatar_url
        identifier = self.getIdentifier(ctx)
        filename = opj(self.TEMP_PATH, "art-%s-%s-%s.png" % (member.id, time.time(), \
                        identifier))
        
        process = mp.Process(target=self.artProcess, \
                        args=(member, filename))
        process.start()

        while process.is_alive():
            await asyncio.sleep(0.75)

        with open(filename, "rb") as file:
            image = discord.File(file)
            await ctx.send(file=image)
        os.remove(filename)

    @commands.command()
    async def wanted(self, ctx, member : discord.Member, amount : int = 5000, 
                        *, reason : str = None):
        "Make any server member the most wanted Discord user in the West."
        await ctx.trigger_typing()
        backup = ctx.message.author.avatar_url
        identifier = self.getIdentifier(ctx)
        filename = opj(self.TEMP_PATH, "wanted-%s-%s-%s.png" % \
                        (member.id, time.time(), identifier))

        process = mp.Process(target=self.wantedProcess, 
                                args=(member, ctx, amount, reason, filename, backup))
        process.start()

        while process.is_alive():
            await asyncio.sleep(0.75)

        with open(filename, "rb") as file:
            image = discord.File(file)
            await ctx.send(file=image)
        os.remove(filename)

    @commands.command()
    async def fidgetSpinner(self, ctx, *, line : str = None):
        "why would you even do this to yourself"

        await ctx.trigger_typing()
        identifier = self.getIdentifier(ctx)
        filename = opj("assets", "fs-%s-%s.png" % \
                    (time.time(), identifier))

        process = mp.Process(target=self.fsProcess,
                                args=(line, filename))
        process.start()

        while process.is_alive():
            await asyncio.sleep(0.75)

        with open(filename, "rb") as file:
            image = discord.File(file)
            await ctx.send(file=image)
        os.remove(filename)

    @commands.command()
    async def techSupport(self, ctx):
        "Hello, tech support, how may we be of assistance?"
        await ctx.trigger_typing()
        with open(opj("assets", "support.gif"), "rb") as f:
            image = discord.File(f)
            await ctx.send(file=image)

    @commands.command()
    async def slap(self, ctx, member : discord.Member = None):
        "Slap ya friends"
        await ctx.trigger_typing()
        
        # handle nicknames
        slapper = util.getMemberName(ctx.author)
        if member != None:
            target = util.getMemberName(member)

        if ctx.message.author == member:
            d = "%s slapped themselves." % (target)
        elif self.bot.user == member:
            d = "%s slapped me!  ;-;" % (slapper)
        elif member == None:
            d = "slappity slappity"
        else:
            d = "%s got slapped by %s." % (target, slapper)
        
        e = discord.Embed(title = random.choice(self.slapTitles), description = d)
        e.set_image(url = random.choice(self.slapPics))
        await ctx.send(embed = e)

    @commands.command()
    async def punch(self, ctx, member : discord.Member = None):
        "punch ya friends"
        await ctx.trigger_typing()
        imgDict = random.choice(self.punchPics)

        if member != None:
            name = util.getMemberName(member)
        puncher = util.getMemberName(ctx.author)

        if member is ctx.message.author:
            title = "Ya done punched urself"
            description = "%s punched themselves!" % (ctx.message.author.name)
        elif self.bot.user == member:
            title = "aw  :("
            description = "%s punched me." % (ctx.message.author.name)
        elif member == None:
            title = "oof"
            description = "Somewhere, something was punched."
        else:
            title = imgDict["title"]
            description = imgDict["description"].format(name, puncher)

        embed = discord.Embed()
        embed.title = title
        embed.description = description
        embed.set_image(url = imgDict["image-url"])
        await ctx.send(embed=embed)

    @commands.command()
    async def hug(self, ctx, member : discord.Member = None):
        "Hug ya friends"

        await ctx.trigger_typing()
        titles = ["hugs", "aww", "yay", "huggie hug"]

        if member != None:
            target = util.getMemberName(member)

        if ctx.message.author == member:
            d = "{} hugged themselves.".format(target)
        elif self.bot.user == member:
            d = "{} hugged me!".format(ctx.message.author.name)
        elif member == None:
            d = "hugs"
        else:
            d = "{} got hugged by {}.".format(target, ctx.message.author.name)

        urlText = random.choice(self.hugPics)
        titleText = random.choice(titles)
        if urlText == "https://i.imgur.com/oQ8J3Za.gif":
            titleText="oops"
            if ctx.author == member:
                d = "%s got pizza." % (target)
            elif self.bot.user.id == memberID:
                d = "%s gave me pizza!" % (ctx.message.author.name)
            elif member == None and target == "":
                d = "pizza"
            else:
                d = "%s gave %s pizza." % (ctx.message.author.name, target)
        if urlText == "https://i.imgur.com/MnszwT3.gif":
            titleText="no"
            if ctx.message.author.id == memberID:
                d = "%s didn't want the hug." % (target)
            elif self.bot.user.id == memberID:
                d = "%s didn't want my hugs! ;-;" % (ctx.message.author.name)
            elif member == None and target == "":
                d = "no"
            else:
                d = "%s didn't want %s's hug." % (target, ctx.message.author.name)

        e = discord.Embed(title=titleText, description = d)
        e.set_image(url=urlText)
        await ctx.send(embed = e)

    @commands.command()
    async def beanRegister(self, ctx, register : bool):
        "Add or remove yourself to the beanlist. Affects the bean command."
        filename = opj(self.JSON_PATH, "bean.json")
        strID = str(ctx.author.id)

        beanList = util.load_js(filename, returnListIfEmpty = True)

        name = util.getMemberName(ctx.author)

        if register == True:
            if strID in beanList:
                await ctx.send("**%s**, you're already on the beanlist." % name)
                return

            beanList.append(strID)
            await ctx.send("**%s**, you have been added to the beanlist." % name)   
        else:
            if strID not in beanList:
                await ctx.send("**%s**, you aren't on the beanlist." % name)
                return

            beanList.remove(str(ctx.author.id))
            await ctx.send("**%s**, you've been removed from the beanlist." % \
                            name)

        util.save_js(filename, beanList)
    
    @commands.command()
    async def bean(self, ctx, member : discord.Member = None):
        "bean yourself or others, you friccin' moron"
        await ctx.trigger_typing()
        imageUrl="https://i.imgur.com/sncYgfx.png"

        beanList = util.load_js(opj(self.JSON_PATH, "bean.json"), \
                                    returnListIfEmpty = True)
        if member != None:
            name = util.getMemberName(member)
            if str(member.id) in beanList:
                imageUrl="https://i.imgur.com/oBadUcY.gif"

        else:
            if str(ctx.author.id) in beanList:
                imageUrl="https://i.imgur.com/oBadUcY.gif"
        
        if member is ctx.author:
            title = "Ya done beaned urself"
            description = "{} beaned themselves!".format(ctx.message.author.name)
        elif self.bot.user == member:
            title = "aw  :("
            description = "{} beaned me.".format(ctx.message.author.name)
        elif member == None:
            title = "you friccin' moron"
            description = "you just got beaned!!!!1111!!11!1!1"
        else:
            title = "Uh oh!"
            description = "{} got beaned by {}!".format(name, ctx.message.author.name)

        embed = discord.Embed()
        embed.title = title
        embed.description = description
        embed.set_image(url = imageUrl)
        await ctx.send(embed = embed)

    @commands.command()
    async def embedImage(self, ctx, u : str):
        "Embeds a picture so we don't have to look at a big, ugly URL."
        e = discord.Embed()
        e.set_image(url = u)

        await ctx.message.delete()
        await ctx.send(embed = e)

def setup(bot):
    bot.add_cog(Images(bot))
