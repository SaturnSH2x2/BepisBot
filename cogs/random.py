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
	async def fidgetSpinner(self, ctx, line : str = None):
		"""hahaha dead meme"""
		# font found here: http://www.fontspace.com/jake-luedecke-motion-and-graphic-design/ldfcomicsans
		# code based off this: https://stackoverflow.com/questions/25255206/alternatives-to-pil-pillow-for-overlaying-an-image-with-text#25255348
		await self.bot.send_typing(ctx.message.channel)
		POSSIBLE_LINES = [	"vsssssssssshhhhhhh",
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
		if thing == "<@!162357148540469250>":
			rating = 420
		elif "persona 3" in thing.lower():
			rating = 10
		elif "kingy" in thing.lower():
			rating = "gey"
		elif thing == "<@!197244770626568193>":
			rating = "gey"

		if rating == 8:
			word = "an"
		else:
			word = "a"

		await self.bot.say(":thinking: I'd give {} {} {} out of 10.".format(thing, word, rating))

	@commands.command()
	async def ship(self, mem1, mem2):
		"""Ship two people together to create a fanfiction.  Slightly disturbing material may arise out of this.  You have been warned."""
		fanfics = util.load_js("cogs/fanfics.json")

		if isinstance(mem1, discord.User) or isinstance(mem1, discord.Member):
			mem1 = mem1.display_name
		else:
			mem1 = str(mem1)

		if isinstance(mem2, discord.User) or isinstance(mem2, discord.Member):
			mem2 = mem2.display_name
		else:
			mem2 = str(mem2)

		message = fanfics[random.randint(0, len(fanfics) - 1)]
		await self.bot.say(message.format(mem1, mem2))

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

def setup(bot):
	bot.add_cog(RandomStuff(bot))
