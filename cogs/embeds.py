import asyncio
import discord

from discord.ext import commands
from cogs.base import Base

class Embeds(Base):
	@commands.command(pass_context = True)
	async def embed(self, ctx, u : str):
		"""Embeds a picture so we don't have to look at a big, ugly URL."""
		e = discord.Embed()
		e.set_image(url = u)
		
		await self.bot.delete_message(ctx.message)
		await self.bot.say(embed = e)
		
def setup(bot):
	bot.add_cog(Embeds(bot))
