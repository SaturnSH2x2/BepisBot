import asyncio
import discord
import requests
import util
import os
import subprocess

from discord.ext import commands
from cogs.base import Base

class BotCmd(Base):
	def __init__(self, bot):
		conf = util.load_js("config.json")
		self.okbLocation = conf["okaybot-location"]
		self.okbToken    = conf["okaybot-token"]
		self.mod_roles= conf["moderator-roles"]
		self.kSpam = False
		super().__init__(bot)

	@commands.command(pass_context = True)
	async def disableCommand(self, ctx, passedCommand : str):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		disabledCommands = util.load_js("disabled-commands.json")
		if len(disabledCommands) == 0:
			disabledCommands = []
			
		if passedCommand == "disableCommand" or passedCommand == "enableCommand":
			await self.bot.say("That command cannot be disabled.")
			return
			
		for command in self.bot.commands:
			if command == passedCommand:
				disabledCommands.append({ "command" : passedCommand,
										"server-id" : ctx.message.server.id})
				util.save_js("disabled-commands.json", disabledCommands)
				await self.bot.say("{}{} has been disabled.".format(self.bot.command_prefix, passedCommand))
				return
				
		await self.bot.say("The {}{} command does not exist!".format(self.bot.command_prefix, passedCommand))
		
	@commands.command(pass_context = True)
	async def enableCommand(self, ctx, passedCommand : str):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		disabledCommands = util.load_js("disabled-commands.json")
		index = 0
		for d in disabledCommands:
			if d["command"] == passedCommand and d["server-id"] == ctx.message.server.id:
				del d
				del disabledCommands[index]
				util.save_js("disabled-commands.json", disabledCommands)
				await self.bot.say("{}{} has been re-enabled.".format(self.bot.command_prefix, passedCommand))
				return
				
			index += 1
		await self.bot.say("{}{} either isn't a valid command, or is not currently disabled.".format(self.bot.command_prefix, passedCommand))
				
	@commands.command(pass_context = True)
	async def printDisabledCommands(self, ctx):
		disabledCommands = util.load_js("disabled-commands.json")
		e = discord.Embed()
		eContent = ""
		for d in disabledCommands:
			if d["server-id"] == ctx.message.server.id:
				eContent += d["command"]
				eContent += "\n"
				
		if eContent == "":
			e.title = "No commands have been disabled for this server."
		else:
			e.title = "Here are the commands that have been disabled for this server."
		e.description = eContent
		
		await self.bot.say(embed = e)
	
	@commands.command(pass_context = True)
	async def deleteMessages(self, ctx, number : int = 10):
		"""Delete the number of messages specified.  Deletes 10 by default.  This requires special perms."""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		await self.bot.purge_from(ctx.message.channel, limit = number)
		msg = await self.bot.say("Deleted {} messages.".format(number))
		await asyncio.sleep(5)
		await self.bot.delete_message(msg)

	@commands.command(pass_context = True)
	async def setAvatar(self, ctx, link : str):
		"""Set the bot's avatar."""
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
	async def setUsername(self, ctx, *, name : str):
		"""Set the bot's username.  This requires special perms."""
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

	@commands.command(pass_context = True)
	async def updateBot(self, ctx):
		"""Update the bot to the latest version.  This requires special perms."""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		await self.bot.say("Updating the bot...")
		os.system("git fetch origin")
		os.system("git checkout --force origin/master")
		await self.bot.say("Bot is updated!  Restarting...")
		await self.bot.close()
		os.system("python3.5 main.py")

	@commands.command(pass_context = True)
	async def leaveServer(self, ctx):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		await self.bot.say("Leaving server.  Bye... :cry:")
		await self.bot.leave_server(ctx.message.server)

	@commands.command(pass_context = True)
	async def shutdown(self, ctx):
		"""Shutdown the bot.  Useful.  Occasionally."""
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		await self.bot.say(":ballot_box_with_check: BepisBot is shutting down...")
		await asyncio.sleep(1)
		await self.bot.close()
		
	@commands.command(pass_context = True)
	async def restart(self, ctx):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		await self.bot.say(":ballot_box_with_check: BepisBot is restarting...")
		await asyncio.sleep(1)
		await self.bot.close()
		os.system("python3.5 main.py")
		
	@commands.command()
	async def setPlaying(self, *, playing : str):
		"Set the bot's playing status."""
		if "emibot" in playing.lower():
			await self.bot.say("Haha.  Nice try there.")
			return

		if ( "clone" in playing.lower() ) and ( "bot" in playing.lower() ):
			await self.bot.say("Haha.  Nice try there.")
			return

		if ( "emily" in playing.lower() ) and ( "bot" in playing.lower() ):
			await self.bot.say("Haha.  Nice try there.")
			return

		await self.bot.change_presence(game = discord.Game(name = playing))
		await self.bot.say("Now playing {}".format(playing))

	@commands.command()
	async def inviteLink(self):
		"""Invite the bot to your own server!  Sends you a DM with the invite link."""
		client_id = util.load_js("config.json")["client-id"]
		await self.bot.whisper("https://discordapp.com/oauth2/authorize?&client_id={0}&scope=bot&permissions=0".format(client_id))

	@commands.command(pass_context = True)
	async def say(self, ctx, *, thing : str):
		"""Have the bot say something.  Chances are, you're gonna make it say something stupid."""
		#thing = ctx.message.content[len(ctx.prefix) + len(ctx.command.name) + 1:]

		if ctx.message.author.id == self.bot.user.id:
			return

		await self.bot.say(thing)
		
	@commands.command(pass_context = True)
	async def spam(self, ctx, number : int, *, thing : str):
		"""Spam a message.  Use with caution."""
		if ctx.message.author.id == self.bot.user.id:
			return
			
		if self.kSpam == True:
			return
			

		if len(ctx.message.role_mentions) > 0:
			await self.bot.say("The bot cannot spam role mentions.")
			return

		await self.bot.type()
		
		if number > 100000000000000000000:
			await self.bot.say("Are you fucking out of your mind?")
			return
		if number > 100:
			await self.bot.say("Yeah, no.")
			return
		
		for i in range(number):
			if self.kSpam == True:
				break
				
			await self.bot.say(thing)
			
			if i == number - 1:
				pass
			else:
				await self.bot.type()
			await asyncio.sleep(0.75)

	@commands.command(pass_context = True)
	async def killSpam(self, ctx):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		self.kSpam = True
		await self.bot.say("Spam killed.  All spam commands will be ignored for the next minute.")
		await asyncio.sleep(60)
		self.kSpam = False

	@commands.command(pass_context = True)
	async def whisper(self, ctx, *, thing : str):
		"""Make it so that it looks like the bot said something on its own."""
		#thing = ctx.message.content[len(ctx.prefix) + len(ctx.command.name) + 1:]

		if ctx.message.author.id == self.bot.user.id:
			return

		await self.bot.delete_message(ctx.message)
		await self.bot.say(thing)
		
	@commands.command(pass_context = True)
	async def setNick(self, ctx, *, nick : str):
		"""Nickname test"""
		botMember = ctx.message.server.get_member(self.bot.user.id)
		await self.bot.change_nickname(botMember, nick)
		await self.bot.say("Set nickname to {}".format(nick))
		
	@commands.command(pass_context = True)
	async def enableLogging(self, ctx):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		logLog = util.load_js("logs/server-list.json")
		if len(logLog) == 0:
			logLog = []
			
		logLog.append(ctx.message.server.id)
		util.save_js("logs/server-list.json", logLog)
		
		await self.bot.say("Logging for this server has been enabled.")

	@commands.command(pass_context = True)
	async def updateOkaybot(self, ctx):
		"""Updates OkayBot.  I'm only able to do this because OkayBot is hosted on the same VPS."""
		user = ctx.message.author.id
		files = ctx.message.attachments

		if (user != "162357148540469250") and (user != "218919888583000064"):
			await self.bot.say("Due to the nature of this command, only B_E_P_I_S_M_A_N and Stovven can update OkayBot.")
			return

		mainRB = None
		for f in files:
			if f["filename"] == "main.rb":
				mainRB = f["url"]
				break

		if not mainRB:
			await self.bot.say("Please make sure your file is named \"main.rb\", then try uploading again.")
			return

		okbInServer = False
		for member in ctx.message.server.members:
			if member.id == "354059440355409921":
				okbInServer = True

		if okbInServer:
			await self.bot.say("Okay, <@!354059440355409921>, get your ass over here")
			await asyncio.sleep(3.0)

		data = requests.get(mainRB)
		with open(os.path.join(self.okbLocation, "main.rb"), "wb+") as mrb:
			mrb.write(data.content)
			mrb.close()
		
		os.system("killall ruby")
		subprocess.Popen(["cd", self.okbLocation, "&&", "bundle", "exec", "ruby", "{}/main.rb".format(self.okbLocation), self.okbToken, "--gemfile={}/Gemfile".format(self.okbLocation)])
		await self.bot.say(":white_check_mark: OkayBot has been updated.")

	@commands.command(pass_context = True)
	async def fDisable(self, ctx):
		"Don't want SpongeBob's ugly mug staring you down every time you pay your respects? Use this. Requires special perms."
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		conf = util.load_js("config.json")
		try:
			conf["fDisabled"].append(ctx.message.server.id)
		except KeyError:
			conf["fDisabled"] = []
			conf["fDisabled"].append(ctx.message.server.id)		

		util.save_js("config.json", conf)

		await self.bot.say("F Reactions have been disabled.")

	@commands.command(pass_context = True)
	async def fEnable(self, ctx):
		"Enables the bot to react accordingly whenever you pay your respects. Requires special perms."
		perms = await util.check_perms(self, ctx)
		if not perms:
			return

		conf = util.load_js("config.json")
		try:
			conf["fDisabled"].remove(ctx.message.server.id)
		except KeyError:
			await self.bot.say("F Reactions are already enabled.")
			return
		except ValueError:
			await self.bot.say("F Reactions are already enabled.")
			return

		util.save_js("config.json", conf)

		await self.bot.say("F Reactions have been enabled.")

	@commands.command(pass_context = True)
	async def disableLogging(self, ctx):
		perms = await util.check_perms(self, ctx)
		if not perms:
			return
			
		logLog = util.load_js("logs/server-list.json")
		logLog.remove(ctx.message.server.id)
		util.save_js("logs/server-list.json", logLog)
		
		await self.bot.say("Logging for this server has been disabled.")
		
def setup(bot):
	bot.add_cog(BotCmd(bot))
