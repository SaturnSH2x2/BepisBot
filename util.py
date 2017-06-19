import asyncio
import discord
from discord.ext import commands

import json

async def check_perms(obj, ctx):
	for role in ctx.message.author.roles:
		if int(role.id) in obj.mod_roles:
			return True
	await obj.bot.say("You do not have permission to perform this action.")
	return False

def load_js(path):
	try:
		with open(path, "r") as js:
			data = json.load(js)
			js.close()
	except FileNotFoundError:
		data = {}

	return data

def save_js(path, data):
	js = open(path, "w+")
	json.dump(data, js)
	js.close()
	
	return
