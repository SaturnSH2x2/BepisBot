import asyncio
import discord

from discord.ext import commands
from cogs.base import Base

import util

class BlackWhiteList(Base):
	def __init__(self, bot):
		self.whitelist     = util.load_js("whitelist.json")
		self.blacklistList = util.load_js("blacklist.json")
		if "roles" not in self.whitelist:
			self.whitelist["roles"] = []
		if "users" not in self.whitelist:
			self.whitelist["users"] = []
		
		print("Whitelist: {}".format(self.whitelist))
		super().__init__(bot)
		
	@commands.command(pass_context = True)
	async def wlsAddUser(self, ctx, member : discord.Member):
		"""Adds a user to the whitelist.  This requires special perms"""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		if str(member.id) in self.whitelist["users"]:
			await self.bot.say("{} is already in the bot's whitelist.".format(ctx.author.name))
			return
			
		self.whitelist["users"].append(member.id)
		util.save_js("whitelist.json", self.whitelist)
		
		await self.bot.say("**{}**, you have been added to the bot's whitelist!  You now have access to special commands!".format(member.mention))
		return
		
	@commands.command(pass_context = True)
	async def wlsAddRole(self, ctx, role : discord.Role):
		"""Adds a role to the whitelist.  This requires special perms."""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		if str(role.id) in self.whitelist["roles"]:
			await self.bot.say("The {} role is already in the bot's whitelist.".format(role.name))
			return
			
		self.whitelist["roles"].append(role.id)
		util.save_js("whitelist.json", self.whitelist)
		
		await self.bot.say("All members with the **{}** role now have access to this bot's special commands!".format(role.mention))
		return
		
	@commands.command(pass_context = True)
	async def wlsRemoveUser(self, ctx, member : discord.Member):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		if member.id in self.whitelist["users"]:
			self.whitelist["users"].remove(member.id)
			util.save_js("whitelist.json", self.whitelist)
			
			await self.bot.say("**{}**, you have been removed from the bot's whitelist.".format(member.mention))
			return
		else:
			await self.bot.say("{} isn't in this bot's whitelist.".format(member.name))
			return
			
	@commands.command(pass_context = True)
	async def wlsRemoveRole(self, ctx, role : discord.Role):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		if role.id in self.whitelist["roles"]:
			self.whitelist["roles"].remove(role.id)
			util.save_js("whitelist.json", self.whitelist)
			
			await self.bot.say("Members with the **{}** have been removed from the bot's whitelist.".format(role.mention))
			return
		else:
			await self.bot.say("The {} role isn't in this bot's whitelist.".format(role.name))
			return
			
	@commands.command(pass_context = True)
	async def blacklist(self, ctx, member : discord.Member, *, reason : str = "None given."):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		if len(self.blacklistList) == 0:
			self.blacklistList = []
			
		for user in self.blacklistList:
			if str(member.id) == str(user["id"]):
				await self.bot.say("{} is already in the bot's blacklist.".format(member.name))
				return
				
		self.blacklistList.append( {"id" : member.id, "reason" : reason} )
		util.save_js("blacklist.json", self.blacklistList)
		
		await self.bot.say("**{}**, you have been blacklisted from using the bot.  Reason: {}".format(member.mention, reason))
		
	@commands.command(pass_context = True)
	async def unblacklist(self, ctx, member : discord.Member):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		for user in self.blacklistList:
			if str(member.id) == str(user["id"]):
				self.blacklistList.remove(user)
				await self.bot.say("**{}**, you have been removed from the bot's blacklist".format(member.mention))
				return
				
		await self.bot.say("{} is not in the bot's blacklist".format(member.name))
		
def setup(bot):
	bot.add_cog(BlackWhiteList(bot))
