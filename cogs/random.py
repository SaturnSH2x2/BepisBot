import asyncio
import discord
import requests
import random
import os
import util

from PIL import Image
from discord.ext import commands

from cogs.base import Base

class RandomStuff(Base):
	@commands.command(pass_context = True)
	async def art(self, ctx, member : discord.Member):
		"""?"""
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
	async def rate(self, ctx):
		"""Rate anything, on a scale frrom 0 to 10."""
		rating = 0

		thing = ctx.message.content[len(ctx.prefix) + len(ctx.command.name) + 1:]

		for char in thing:
			a_value = ord(char) % 10
			rating += a_value

		rating %= 10

		if thing == "<@162357148540469250>":
			rating = 420

		await self.bot.say(":thinking: I'd give {} a {} out of 10.".format(thing, rating))

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

def setup(bot):
	bot.add_cog(RandomStuff(bot))
