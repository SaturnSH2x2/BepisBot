import asyncio
import discord
import time
import os

from discord.ext import commands

import util

def log_action(string : str):
	with open( os.path.join( "logs", "{}.txt".format( time.strftime("%d%m%Y") ) ), "a+" ) as log:
		log.write(string + "\n")
		log.flush()
		log.close()

COGS = ["cogs.userrole",
	"cogs.mod",
	"cogs.random",
	"cogs.bot"]

conf = util.load_js("config.json")
token  = conf["token"]
prefix = conf["prefix"]
main_c = conf["main-channels"]

if not os.path.exists("cache"): os.mkdir("cache")
if not os.path.exists("logs"):  os.mkdir("logs")

bot = commands.Bot(command_prefix = prefix)

@bot.event
async def on_command_error(error, ctx):
	print("Command Error!  {}".format(type(error)))
	if isinstance(error, commands.errors.MissingRequiredArgument):
		await bot.send_message(ctx.message.channel, bot.formatter.format_help_for(ctx, ctx.command)[0])
	else:
		print("An error has occurred.  {}".format(error))

@bot.event
async def on_ready():
	for channel in main_c:
		await bot.send_message(bot.get_channel(str(channel)), "BepisBot is back up!")

@bot.event
async def on_message(message):
	print("{}: {}".format(message.author.name, message.content))
	log_action("{}: {}".format(message.author.name, message.content))

	await bot.process_commands(message)

@bot.event
async def on_member_join(member):
	print("{} has joined the server!".format(member.name))
	for c in main_c:
		channel = bot.get_channel(str(c))
		if channel.server == member.server:
			await bot.send_message(channel, "Welcome, **{}**, to the server!".format(member.name))

	log_action("{} joined the server.".format(member.name))
	bot.process_commands(member)

@bot.event
async def on_member_remove(member):
	print("{} has left the server.".format(member.name))
	for c in main_c:
		channel = bot.get_channel(str(c))
		if channel.server == member.server:
			await bot.send_message(channel, "**{}** has left the server.  Welp.".format(member.name))

	log_action("{} left the server.".format(member.name))
	bot.process_commands(member)


for cog in COGS:
	bot.load_extension(cog)

bot.run(token)
