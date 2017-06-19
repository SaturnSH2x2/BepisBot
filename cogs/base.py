import asyncio
import discord

class Base:
	def __init__(self, bot):
		self.bot = bot
		print("{} cog set up successfully.".format(self.__class__.__name__))
