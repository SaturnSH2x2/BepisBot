import asyncio
import discord
import util

from discord.ext import commands
from cogs.base import Base

class Server(Base):
	@commands.command(pass_context = True)
	async def serverInfo(self, ctx):
		util.nullifyExecute()
		"""Gives various statistics regarding a server."""
		s = ctx.message.server
		e = discord.Embed()
		
		e.title = "Server Statistics"
		e.description = """
Name: {n}
Number of Roles: {r}
Server Region: {sr}
Number of Emojis: {em}
Number of Members: {m}
ID: {i}
Owner: {o}
Created at: {c}
						""".format(n = s.name, r = len(s.roles), sr = s.region, em = len(s.emojis), 
									m = s.member_count, i = s.id, o = s.owner.name, c = s.created_at)
		e.set_thumbnail(url = s.icon_url)
		
		await self.bot.say(embed = e)

def setup(bot):
	bot.add_cog(Server(bot))
