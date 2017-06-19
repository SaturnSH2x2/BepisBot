import asyncio
import discord
from discord.ext import commands

import util
import cogs.base as base

class Moderator(base.Base):
	def __init__(self, bot, config):
		self.mod_roles = config["moderator-roles"]
		super().__init__(bot)

	@commands.command(pass_context = True)
	async def kick(self, ctx, member : discord.Member):
		perms = await util.check_perms(self, ctx)
		print(perms)
		if (perms):
			try:
				await self.bot.kick(member)
				await self.bot.say("{} has been kicked from the server.".format(member.name))
			except:
				await self.bot.say("Could not kick member.  This might be a permissions issue.")

def setup(bot):
	config = util.load_js("config.json")
	bot.add_cog(Moderator(bot, config))
