import asyncio
import discord
import sys
import logging

import util
import cogs

from src.bepisbotclient import BepisBotClient
from discord.ext import commands

# list of cogs for the bot client to load
COGS = [
    "cogs.music",
    "cogs.random",
    "cogs.images",
    "cogs.tarot",
    "cogs.bot",
    "cogs.mod",
    "cogs.react"
]

def main():
    # load config file
    if len(sys.argv) < 2:
        conf = util.load_js("config.json")
    else:
        conf = util.load_js(sys.argv[2])

    if conf == {}:
        print("Could not find/open config file. Double-check your settings and run the bot again.")
        print("Exiting...")
        sys.exit()

    # configure logging
    logging.basicConfig(level=logging.INFO)

    # create and run the bot
    bot = BepisBotClient(command_prefix = conf["prefix"], pm_help = True,
          description = "A complete rewrite of BepisBot using the rewrite " + 
          "branch of discord.py")

    for ext in COGS:
        bot.load_extension(ext)

    bot.run(conf["token"])

if __name__ == "__main__":
    main()
