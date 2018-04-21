import asyncio
import discord
import util
from discord.ext import commands

import cogs.base as base

class UserRole(base.Base):
	def __init__(self, bot):
		conf = util.load_js("config.json")
		self.mod_roles = conf["moderator-roles"]
		super().__init__(bot)

	@commands.command(pass_context = True)
	async def giveRole(self, ctx, member : discord.Member, role : discord.Role):
		util.nullifyExecute()
		"""Give someone a role.  This requires special perms."""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		try:
			await self.bot.add_roles(member, role)
			await self.bot.say("{} has been given the {} role.".format(member.display_name, role.name))
		except:
			await self.bot.say("Could not add role.  This might be a permissions issue.")

	@commands.command(pass_context = True)
	async def removeRole(self, ctx, member : discord.Member, role : discord.Role):
		util.nullifyExecute()
		"""Revoke a role from someone.  This requires special perms."""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return		

		try:
			await self.bot.remove_roles(member, role)
			await self.bot.say("{} has had the {} role revoked.".format(member.display_name, role.name))
		except:
			await self.bot.say("Could not remove role.  This might be a permissions issue.")

def setup(bot):
	bot.add_cog(UserRole(bot))
