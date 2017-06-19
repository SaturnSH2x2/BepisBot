import asyncio
import discord
from discord.ext import commands

import cogs.base as base

class UserRole(base.Base):
	@commands.command()
	async def ping(self):
		await self.bot.say("pong")

	@commands.command()
	async def giveRole(self, member : discord.Member, role : discord.Role):
		try:
			await self.bot.add_roles(member, role)
			await self.bot.say("{} has been given the {} role.".format(member.display_name, role.name))
		except:
			await self.bot.say("Could not add role.  This might be a permissions issue.")

	@commands.command()
	async def removeRole(self, member : discord.Member, role : discord.Role):
		try:
			await self.bot.remove_roles(member, role)
			await self.bot.say("{} has had the {} role revoked.".format(member.display_name, role.name))
		except:
			await self.bot.say("Could not remove role.  This might be a permissions issue.")

def setup(bot):
	bot.add_cog(UserRole(bot))
