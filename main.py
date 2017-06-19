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
invite_c = conf["invite-channel"]

bot = commands.Bot(command_prefix = prefix)

@bot.event
async def on_message(message):
	print("{}: {}".format(message.author.name, message.content))
	log_action("{}: {}".format(message.author.name, message.content))

	await bot.process_commands(message)

# TODO: fix this
"""
@bot.event
async def on_member_join(member):
	print("{} has joined the server!".format(member.name))
	await bot.send_message(discord.Channel(id=invite_c), "Welcome, {}, to the server!".format(member.name))

	log_action("{} joined the server.".format(member.name))
	bot.process_commands(member)

@bot.event
async def on_member_remove(member):
	print("{} has left the server.".format(member.name))
	await bot.send_message(discord.Channel(id=invite_c), "{} has left the server.  Welp.".format(member.name))

	log_action("{} left the server.".format(member.name))
	bot.process_commands(member)
"""

for cog in COGS:
	bot.load_extension(cog)

bot.run(token)
