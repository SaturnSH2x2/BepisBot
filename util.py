import asyncio
import discord
import os
from discord.ext import commands

import json

async def check_perms(obj, ctx):
	try:
		whitelist = load_js("whitelist.json")
		for member in whitelist["users"]:
			if ctx.message.author.id == member:
				return True
			
		for wRole in whitelist["roles"]:
			for role in ctx.message.author.roles:
				if role.id == wRole:
					return True
	except KeyError:
		whitelist = {"users" : [], "roles" : []}
		save_js("whitelist.json", whitelist)
	
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

def execute(obj, ctx):
        if os.path.isfile(os.path.join("cache","{}.bepis".format(ctx.message.id))):
                os.remove(os.path.join("cache","{}.bepis".format(ctx.message.id)))
                ctx.author=ctx.message.server.get_member(obj.bot.user.id)
                ctx.message.author=ctx.message.server.get_member(obj.bot.user.id)
        return ctx



def nullifyExecute():
	files=os.listdir('cache')
	for file in files:
                if file.endswith('.bepis'):
                        os.remove(os.path.join('cache',file))
