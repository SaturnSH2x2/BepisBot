import asyncio
import discord
import os
from discord.ext import commands

import util
import cogs.base as base

class Moderator(base.Base):
	MAXWARNS = 3

	def __init__(self, bot, config):
		self.mod_roles = config["moderator-roles"]
		super().__init__(bot)

		# make sure this directory exists
		try:
			os.mkdir("warns")
		except FileExistsError:
			pass

	@commands.command(pass_context = True)
	async def kick(self, ctx, member : discord.Member):
		"""Kick a member from a server.  This requires special perms."""
		perms = await util.check_perms(self, ctx)
		print(perms)
		if (perms):
			try:
				await self.bot.kick(member)
				await self.bot.say("{} has been kicked from the server.".format(member.name))
			except:
				await self.bot.say("Could not kick member.  This might be a permissions issue.")

	@commands.command(pass_context = True)
	async def unwarn(self, ctx, member : discord.Member, amount : int = 1):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		serverWarnList = util.load_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)))
		if member.id not in serverWarnList or serverWarnList[member.id] <= 0:
			await self.bot.say("{} does not currently have any warns".format(member.name))
			return

		if amount > self.MAXWARNS:
			amount = self.MAXWARNS

		serverWarnList[member.id] -= amount
		await self.bot.say("<@!{}>, you have had {} warns removed.  {} warnings remain.".format(member.id, amount, self.MAXWARNS - serverWarnList[member.id]))
		util.save_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)), serverWarnList)

	@commands.command(pass_context = True)
	async def warn(self, ctx, member : discord.Member):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		serverWarnList = util.load_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)))

		if member.id not in serverWarnList:
			serverWarnList[member.id] = 0
		serverWarnList[member.id] += 1

		if self.MAXWARNS - serverWarnList[member.id] > 1:
			await self.bot.say("<@!{}>, you have been given a warning.  You have {} warnings left.".format(member.id, self.MAXWARNS - serverWarnList[member.id]))
		elif serverWarnList[member.id] >= self.MAXWARNS:
			pass
		else:
			await self.bot.say("<@!{}>, this is your final warning.  One more warn and you will be banned.".format(member.id))
		util.save_js(os.path.join("warns", "{}.json".format(ctx.message.server.id)), serverWarnList)

		if serverWarnList[member.id] >= self.MAXWARNS:
			await self.bot.ban(member)
			await self.bot.say("<@!{}> has been banned from the server for getting {} warnings.".format(member.id, self.MAXWARNS))
		

def setup(bot):
	config = util.load_js("config.json")
	bot.add_cog(Moderator(bot, config))
