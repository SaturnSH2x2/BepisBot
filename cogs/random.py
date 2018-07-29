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
        ctx=util.execute(self,ctx)

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
    async def techSupport(self,ctx):
        util.nullifyExecute()
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.upload("assets/support.gif")

    @commands.command(pass_context = True)
    async def doYouKnowDeWae(self,ctx):
        util.nullifyExecute()
        """Dead meme killer"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.upload("assets/wae.mp4")

    @commands.command(pass_context=True)
    async def slap(self, ctx, *, target : str = ""):
        await self.bot.send_typing(ctx.message.channel)
        """Slap ya friends"""
        ctx=util.execute(self,ctx)
        titles = ["oof", "ouch", "owie", "hngh", "ouchie ouch", "ow"]
        pics = util.load_js(os.path.join("assets", "slap.json"))
        
        memberID = target.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        member = ctx.message.server.get_member(memberID)
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
        await self.bot.say(embed = e)

    @commands.command(pass_context=True)
    async def hug(self, ctx, *, target : str = ""):
 #   async def hug(self, ctx, *, hugNum : int = -1, target : str = ""):
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
        
        
##    @commands.command(pass_context = True)
##    async def punch(self, ctx, *, user : str = ""):
##        await self.bot.send_typing(ctx.message.channel)
##        
##        user = user.replace("<", "").replace(">", "").replace("!", "").replace("@", "")
##        member = ctx.message.server.get_member(user)
##        if member != None:
##            user = member.name  
##        
##        images = util.load_js(os.path.join("assets", "punch.json"))
##        imgDict = random.choice(images)
##        
##        e = discord.Embed()
##        if member != None:
##            if member.id == ctx.message.author.id:
##                e.title = "Ya done punched urself"
##                e.description = "{} punched themselves!".format(ctx.message.author.name)
##            elif self.bot.user.id == member.id:
##                e.title = "aw  :("
##                e.description = "{} punched me.".format(ctx.message.author.name)
##        else:
##            e.title = imgDict["title"]
##            e.description = imgDict["description"].format(user, ctx.message.author.name)
##        e.set_image(url = imgDict["image-url"])
##        
##        await self.bot.say(embed = e)

    @commands.command(pass_context = True)
    async def punch(self, ctx, *, user : str=""):
        await self.bot.send_typing(ctx.message.channel)
        ctx=util.execute(self,ctx)
        images = util.load_js(os.path.join("assets", "punch.json"))
        imgDict = random.choice(images)
        memberID = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        member = ctx.message.server.get_member(memberID)
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
        await self.bot.say(embed=embed)
    
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
    
    @commands.command(pass_context = True)
    async def wanted(self, ctx, member : discord.Member, *, text : str = None):
        """?"""
        backup=ctx.message.author.avatar_url
        ctx=util.execute(self,ctx)
        await self.bot.send_typing(ctx.message.channel)
        glitcher=False
        reasonBool=False
        whitelist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','&','2','9','.',' ']
        finalImage = Image.new("RGBA", (764, 997), "white")
        frameImage = Image.open(os.path.join("assets", "wanted.png")).convert("RGBA")
        draw=ImageDraw.Draw(finalImage)
        if text == None:
            text="5,000"
        splitter=text.split(" ",maxsplit=1)
        text=splitter[0]
        try:
            reason=splitter[1]
            reasonBool=True
        except:
            reasonBool=False
        text=text.replace(",", "")
        try:
            x=int(text)
            if x<1000000 and x>-100000:
                text="{:,}".format(int(text))
            else:
                glitcher=True
        except:
            glitcher=True
        
        fontA  = ImageFont.truetype(os.path.join("assets","RodeoClown.ttf"), 83)
        fontB  = ImageFont.truetype(os.path.join("assets","Nashville.ttf"), 44)
        url = member.avatar_url
        if url == "":
            url = member.default_avatar_url
        
        if reasonBool==True:
            reason=reason.lower()
            w2,h2=draw.textsize(reason, font=fontB)
            if w2>670:
                glitcher=True
            for char in reason:
                if char not in whitelist:
                    reasonBool=False
        
        if glitcher==True:
            url=ctx.message.author.avatar_url
            text="999,999"
            reasonBool=True
            reason="Trying to break the system"
            w2,h2=draw.textsize(reason, font=fontB)
        
        if self.bot.user.id==ctx.message.author.id:
            url=backup
            text="999,999"
            reasonBool=True
            reason="Trying to frame me!"
            w2,h2=draw.textsize(reason, font=fontB)
        line="$"+text+" REWARD"
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
        w,h=draw.textsize(line, font=fontA)
        if reasonBool==True:
            w2,h2=draw.textsize(reason, font=fontB)
            draw.multiline_text((((681-w)/2)+42, 785), line, (0, 0, 0), font=fontA, align="left")
            draw.multiline_text((((681-w2)/2)+42, 865), reason, (0, 0, 0), font=fontB, align="left")
        else:
            draw.multiline_text((((681-w)/2)+42, 806), line, (0, 0, 0), font=fontA, align="left")

        finalImage.save("wantedTemp.png", "PNG")

        await self.bot.send_file(ctx.message.channel, "wantedTemp.png")

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
    async def fidgetSpinner(self, ctx, *, line : str = None):
        util.nullifyExecute()
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
                postedMessage = await self.bot.say(question)
                for reaction in toReact:
                    await self.bot.add_reaction(postedMessage, reaction)
            
        

##    @commands.command(pass_context=True)
##    async def test(self,ctx):
##        s=ctx.message.server
##        r=s.roles
##        for i in range(len(r)):
##            permissionText=""""""
##            print(r[i].name)
##            if r[i].permissions.administrator==True:
##                permissionText="""Administrator"""
##            else:
##                if r[i].permissions.create_instant_invite:
##                    permissionText+="""Create Instant Invites, """
##                if r[i].permissions.kick_members:
##                    permissionText+="""Kick Members, """
##                if r[i].permissions.ban_members:
##                    permissionText+="""Ban Members, """
##                if r[i].permissions.manage_channels:
##                    permissionText+="""Manage Channels, """
##                if r[i].permissions.manage_server:
##                    permissionText+="""Manage Server, """
##                if r[i].permissions.add_reactions:
##                    permissionText+="""Add Reactions, """
##                if r[i].permissions.view_audit_logs:
##                    permissionText+="""View Audit Logs, """
##                if r[i].permissions.manage_messages:
##                    permissionText+="""Manage Messages, """
##                if r[i].permissions.mention_everyone:
##                    permissionText+="""Mention Everyone, """
##                if r[i].permissions.mute_members:
##                    permissionText+="""Mute Members, """
##                if r[i].permissions.deafen_members:
##                    permissionText+="""Deafen Members, """
##                if r[i].permissions.move_members:
##                    permissionText+="""Move Members, """
##                if r[i].permissions.change_nickname:
##                    permissionText+="""Change Nickname, """
##                if r[i].permissions.manage_nicknames:
##                    permissionText+="""Manage Nicknames, """
##                if r[i].permissions.manage_roles:
##                    permissionText+="""Manage Roles, """
##                if r[i].permissions.manage_webhooks:
##                    permissionText+="""Manage Webhooks, """
##                if r[i].permissions.manage_emojis:
##                    permissionText+="""Manage Emojis, """
##                if len(permissionText)>0:
##                    permissionText=permissionText[:-2]
##                else:
##                    permissionText+="""None"""
##            print(permissionText)

##    @commands.command(pass_context=True)
##    async def test(self,ctx, *, t : str = None):
##        util.nullifyExecute()
##        """Update the bot to the latest version.  This requires special perms."""
##        perms = await util.check_perms(self, ctx)
##        if not perms:
##            return
##        if ctx.message.author.id=="172898048702283776" and ctx.message.server.id=="349283770689519617":
##            serverNoteList = util.load_js(os.path.join("notes", "{}.json".format(ctx.message.server.id)))
##            key="a"#hashlib.sha256(str(serverNoteList).encode("utf-8")).hexdigest()
##            if t!=key:
##                await self.bot.say(":pedro:")
##                return
##        await self.bot.say(":doot:")
    
        
        
def setup(bot):
    bot.add_cog(RandomStuff(bot))
