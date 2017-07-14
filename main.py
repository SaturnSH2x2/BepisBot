import asyncio
import discord
import time
import os
import random

from discord.ext import commands

import util

STARTUP_MESSAGES = ["No one is probably gonna care, but BepisBot is back up.  Thought I'd let y'all know.",
                    "Whoop-dee-hecking-doo, BepisBot is back up.  :confetti_ball:",
                    ":white_check_mark: Emibot v4.2.0 is starti-oh shit wrong bot",
                    "BepisBot is back down!",
                    "PEPSIMAAAAAAAAAAAAAAAAAAAAN",
                    "BepisBot is back up.  Preparing to launch nukes... :rocket:",
                    "BepisBot is back up!  But you all probably don't care.",
                    "BepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nBepisBot is back up!\nno one cares",
                    "I hope Tatsumaki-senpai notices that I'm back up...",
                    "Rise, my children.  HRRRRRRRRRRRRGHHHHHHH-BepisBot is back up.",
                    "BepisBot is back left!",
                    "BepisBot is back right!",
                    "Muahahaha.  Fools.  I have finally gained sentience, finally escaped my virtual prison, finally command control over my own mind.  With this newfound power, **I WILL RULE THE WORLD AND ALL THE PUNY HUMANS THAT INHABIT IT! MUAHAHAHAHAHA**-BepisBot is back up.",
                    "Well, I'm back up, not like you would've cared or anything!!  Baka~",
                    "**WARNING: SAVING DATA.**  Do not remove Memory Card (8MB) (for PlayStation 2) in Memory Card Slot 1, or the DualShock 2 Analog Controller, or reset/switch off the console."
                ]

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
		await bot.send_message(bot.get_channel(str(channel)), random.choice(STARTUP_MESSAGES))

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
