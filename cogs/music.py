import asyncio
import discord

from ctypes.util import find_library
from discord.ext import commands
from cogs.base import Base

class Music(Base):
	def __init__(self, bot):
		if discord.opus.is_loaded():
			pass
		else:
			discord.opus.load_opus(find_library("opus"))
			
		self.voice = None
		super().__init__(bot)
		
	async def checkOpus(self, ctx):
		if discord.opus.is_loaded():
			return True
		else:
			await self.bot.send_message(ctx.message.channel, "The Opus Library is not loaded.  Voice commands are not available at this time.")
			return False

	@commands.command(pass_context = True)
	async def join(self, ctx):
		if not self.checkOpus:
			return
			
		# you'd think this command would be at least a little shorter
		vChannel = ctx.message.server.get_member(ctx.message.author.id).voice.voice_channel
		if vChannel == None:
			await self.bot.say("You are not connected to a voice channel.  Connect first, then call this command.")
			return
			
		try:
			self.voice = await self.bot.join_voice_channel(vChannel)
			await self.bot.say("Ready!")
		except discord.ClientException:
			await self.voice.move_to(vChannel)
			
	@commands.command(pass_context = True)
	async def mikeWazowski(self, ctx):
		if self.voice == None:
			await self.bot.say("Connect to a voice channel, call me with {}join, then call this command.".format(self.bot.command_prefix))
			return
		elif ctx.message.server.get_member(ctx.message.author.id).voice.voice_channel != self.voice.channel:
			await self.bot.say("You're in a different voice channel!  Either switch channels, or use {}join to summon me there.".format(self.bot.command_prefix))
			return
			
		await self.bot.type()
		mw = await self.voice.create_ytdl_player("https://youtu.be/IRP-2y43BLo")
		mw.start()
		
		await self.bot.say("**_M I K E  W A Z O W S K I_**")
		
def setup(bot):
	bot.add_cog(Music(bot))
