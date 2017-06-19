import asyncio
import discord
import requests
import util

from discord.ext import commands
from cogs.base import Base

class BotCmd(Base):
	def __init__(self, bot):
		conf = util.load_js("config.json")
		self.mod_roles= conf["moderator-roles"]
		super().__init__(bot)

	@commands.command(pass_context = True)
	async def setAvatar(self, ctx, link : str):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		await self.bot.send_typing(ctx.message.channel)
		image = requests.get(link)

		try:
			await self.bot.edit_profile(avatar = image.content)
			await self.bot.say("How do I look?")
		except discord.errors.InvalidArgument:
			await self.bot.say("That image type is unsupported!")
		except:
			await self.bot.say("Something went wrong.  Sorry.")

	@commands.command(pass_context = True)
	async def setUsername(self, ctx, name : str):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		try:
			await self.bot.edit_profile(username = name)
			await self.bot.say("Henceforth, I shall be known as {}!".format(name))
		except discord.errors.HTTPException:
			await self.bot.say("Hrm?  Something came up; the profile can't be set.")
		except:
			await self.bot.say("Something went wrong.  Sorry.")

def setup(bot):
	bot.add_cog(BotCmd(bot))

		
