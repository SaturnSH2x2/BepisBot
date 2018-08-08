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
    "Commands that upload/mess around with images. Consists of reacts, messing \
    around with avatars, and other fun stuff like that."

    # Helper function for downloading a Discord member's avatar.
    # Used for some image commands.
    def getMemberAvatar(self, member : discord.Member):
        url = member.avatar_url
        if url == "":
            url = member.default_avatar_url

        data = requests.get(url)
        path = opj(self.TEMP_PATH, "%s.webp" % (member.id))

        with open(path, "wb+") as f:
            f.write(data.content)
            f.close()

        return path

    def artProcess(self, member : discord.Member, filename : str):
        finalImage = Image.new("RGBA", (811, 444), "white")
        frameImage = Image.open(opj("assets", "Art.png"))

        data = requests.get(url)

        with open(opj(self.TEMP_PATH, "%s.webp" % (mID)), "wb+") as f:
            f.write(data.content)
            f.close()

        avPath = getMemberAvatar(member)
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

        url = member.avatar_url
        if url == "":
            url = member.default_avatar_url

        # make sure the user isn't entering in an ungodly amount
        if not (-100000 < amount < 1000000):
            url = ctx.author.avatar_url
            amount = 999999
            reason = "trying to break the system"

        # make sure the reason provided isn't too long
        elif reason != None:
            reason = reason.lower()
            w2,h2 = draw.textsize(reason, font=fontB)
            print(w2)
            if w2 > 670:
                url = ctx.author.avatar_url
                amount = 999999
                reason = "Giving a long reason"

        # in case the user is trying to frame the bot
        elif self.bot.user.id == member.id:
            url = backup
            amount = 999999
            reason = "Trying to frame me!"
            
        line = "$%i REWARD" % (amount)
        avPath = self.getMemberAvatar(member)
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


    @commands.command()
    async def art(self, ctx, member : discord.Member):
        "Turns any profile picture into a work of art."

        await ctx.trigger_typing()
        url = member.avatar_url
        filename = opj(self.TEMP_PATH, "art-%s-%s-%s.png" % (member.id, time.time(), \
                        ctx.guild.id))
        
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
        backup=ctx.message.author.avatar_url
        filename = opj(self.TEMP_PATH, "wanted-%s-%s-%s.png" % \
                        (member.id, time.time(), ctx.guild.id))

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
        filename = opj("assets", "fs-%s-%s.png" % \
                    (time.time(), ctx.guild.id))

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
    async def slap(self, ctx, *, target : str = ""):
        "Slap ya friends"
        await ctx.trigger_typing()

        titles = ["oof", "ouch", "owie", "hngh", "ouchie ouch", "ow"]
        pics = util.load_js(opj("assets", "slap.json"))
        
        memberID = target.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        member = ctx.message.guild.get_member(memberID)
        if member != None:
            target = member.name
        
        if self.bot.user.id==ctx.message.author.id:
            if target==ctx.message.author.name:
                d = "I slapped myself... Why did I do that?"
            elif member != None and target !="":
                d = "{} got slapped by me.".format(target, ctx.message.author.name)
        elif ctx.message.author.id == memberID:
            d = "{} slapped themselves.".format(target)
        elif self.bot.user.id == memberID:
            d = "{} slapped me!  ;-;".format(ctx.message.author.name)
        elif member == None and target == "":
            d = "slappity slappity"
        else:
            d = "{} got slapped by {}.".format(target, ctx.message.author.name)
        
        e = discord.Embed(title = random.choice(titles), description = d)
        e.set_image(url = random.choice(pics))
        await ctx.send(embed = e)

    @commands.command()
    async def punch(self, ctx, *, user : str=""):
        await ctx.trigger_typing()
        ctx=util.execute(self,ctx)
        images = util.load_js(os.path.join("assets", "punch.json"))
        imgDict = random.choice(images)
        memberID = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        member = ctx.message.guild.get_member(memberID)
        if member:
            user=member.name
            if self.bot.user.id==ctx.message.author.id:
                if member is ctx.message.author:
                    title = "I punched my self..."
                    description = "Why did I do that?"
                else:
                    title = imgDict["title"]
                    description = "{} was punched by me!".format(user)
            elif member is ctx.message.author:
                title = "Ya done punched urself"
                description = "{} punched themselves!".format(ctx.message.author.name)
            elif self.bot.user.id == memberID:
                title = "aw  :("
                description = "{} punched me.".format(ctx.message.author.name)
            else:
                title = imgDict["title"]
                description = imgDict["description"].format(user, ctx.message.author.name)
        else:
            title = imgDict["title"]
            description = imgDict["description"].format(user, ctx.message.author.name)
        embed = discord.Embed()
        embed.title = title
        embed.description = description
        embed.set_image(url = imgDict["image-url"])
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))
