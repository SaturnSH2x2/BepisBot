import asyncio
import discord
import sys
import logging

import util

from src.bepisbotclient import BepisBotClient
from discord.ext import commands

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
    bot = BepisBotClient(command_prefix = conf["prefix"], pm_help = True)
    bot.run(conf["token"])

if __name__ == "__main__":
    main()
