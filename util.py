import asyncio
import discord
import os
from discord.ext import commands

import json

def getMemberName(member : discord.Member):
	try:
		if member.nick != None:
			return member.nick
		else:
			return member.name
	except AttributeError:
		return member.name

def load_js(path, returnListIfEmpty = False):
	try:
		with open(path, "r") as js:
			data = json.load(js)
			js.close()
	except FileNotFoundError:
		if returnListIfEmpty:
			data = []
		else:
			data = {}

	return data

def save_js(path, data):
	js = open(path, "w+")
	json.dump(data, js)
	js.close()
	
	return