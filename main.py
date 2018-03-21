#!/usr/bin/python3.5

import asyncio
import discord
import time
import os
import random
import traceback

from discord.ext import commands
from discord.ext.commands.view import StringView

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

def log_action(message):
    string = "{u} {t}: {c}".format(u = message.author.name, t = time.strftime("%H:%M"), c = message.content)

    server_name_formatted = message.server.name.replace(" ", "-")

    if not os.path.exists("./logs/{}/".format(server_name_formatted)):
        os.mkdir("logs/{}/".format(server_name_formatted))

    if not os.path.exists("./logs/{}/{}".format(server_name_formatted, message.channel.name)):
        os.mkdir("logs/{}/{}/".format(server_name_formatted, message.channel.name))

    with open( os.path.join( "logs", server_name_formatted, message.channel.name, "{}.txt".format( time.strftime("%d%m%Y") ) ), "a+" ) as log:
        for mention in message.mentions:
            string = string.replace("@!{}".format(mention.id), mention.name)
            string = string.replace("@{}".format(mention.id), mention.name)
            
        try:
            log.write(string)
        except UnicodeEncodeError:
            string = "{u} {t}: {c}, ".format(u = message.author.id, t = time.strftime("%H:%M"), c = message.content)
            log.write(str(string.encode("utf-8")))
                
        log.write("\n")
            
        for embed in message.embeds:	
            log.write("embed by {}".format(message.author.name))
            log.write("\n")
            
        log.flush()
        log.close()

COGS = ["cogs.userrole",
    "cogs.mod",
    "cogs.random",
    "cogs.bot",
    "cogs.tarot",
    "cogs.server",
    "cogs.music",
    "cogs.embeds",
    "cogs.whitelist"]

conf = util.load_js("config.json")
token  = conf["token"]
prefix = conf["prefix"]
main_c = conf["main-channels"]

blacklist = util.load_js("blacklist.json")
serverLogList = util.load_js("logs/server-list.json")

if not os.path.exists("cache"): os.mkdir("cache")
if not os.path.exists("logs"):  os.mkdir("logs")

bot = commands.Bot(command_prefix = prefix, pm_help = True)

@bot.event
async def on_server_update(before, after):
    if after.id not in serverLogList:
        return
        
    old_name_formatted = before.name.replace(" ", "-")
    new_name_formatted = after.name.replace(" ", "-")
        
    if os.path.exists( os.path.join("logs", old_name_formatted) ):
        print("Server renamed?")
        os.rename(os.path.join("logs", old_name_formatted), os.path.join("logs", new_name_formatted))

@bot.event
async def on_channel_update(before, after):
    if after.server.id not in serverLogList:
        return
        
    server_name_formatted = before.server.name.replace(" ", "-")
    
    print(os.path.join("logs", server_name_formatted, before.name))

    if os.path.exists( os.path.join("logs", server_name_formatted, before.name) ):
        print("Channel renamed?")
        os.rename( os.path.join("logs", server_name_formatted, before.name), os.path.join("logs", server_name_formatted, after.name) )

@bot.event
async def on_command_error(error, ctx):
    print("Command Error!  {}".format(type(error)))
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await bot.send_message(ctx.message.channel, bot.formatter.format_help_for(ctx, ctx.command)[0])
    elif isinstance(error, commands.errors.CommandNotFound):
        pass

    elif isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        if (ctx.command.name == "help"):
            e = discord.Embed(title = "DM Failed", description = "{} wouldn't let me send help. :(  Try enabling DMs for this server.".format(ctx.message.author.name))
            e.set_image(url="https://i.imgur.com/qJ5hNzG.gif")
            await bot.send_message(ctx.message.channel, embed=e)
        else:
            await bot.send_message(ctx.message.channel, "An error has occurred.  {}\n\n".format(error))
            print("An error has occurred.  {}, ()".format(error, type(error)))
    else:
        await bot.send_message(ctx.message.channel, "An error has occurred.  {}\n\n".format(error))
        print("An error has occurred.  {}, ()".format(error, type(error)))

@bot.event
async def on_ready():
    for channel in main_c:
        msg = await bot.send_message(bot.get_channel(str(channel)), random.choice(STARTUP_MESSAGES))
        await asyncio.sleep(10)
        await bot.delete_message(msg)

@bot.event
async def on_message(message):
    try:
        print("{}: {}".format(message.author.name, message.content))
    except UnicodeEncodeError:
        print("{}: {}".format(message.author.name.encode("utf-8"), message.content.encode("utf-8")))
    print(message.attachments)
        
    serverLogList = util.load_js("logs/server-list.json")
    if str(message.server.id) in str(serverLogList):
        log_action(message)

    blacklisted = None
    is_command = False

    conf = util.load_js("config.json")
    try:
        a = conf["fDisabled"]
    except KeyError:
        conf["fDisabled"] = []
        
    try:
        b = conf["noOneCaresDisabled"]
    except KeyError:
        conf["noOneCaresDisabled"] = []
        b= []

    if message.author.bot == True:
        return

    if prefix not in message.content.lower():
        if message.content.lower() == "f" and message.server.id not in conf["fDisabled"]:
            await bot.send_file(message.channel, "assets/f.jpg")
        if message.server.id not in b:
            if ( "no one cares" in message.content.lower() ) and ( len(message.content) < 30 ):
                await bot.send_message(message.channel, "oh wow {} that was kinda rude kys".format(message.author.mention))
            elif ("ñô öñé çãrës" in message.content.lower() ) and ( len(message.content) < 30 ):
                await bot.send_message(message.channel, "oh wow {} that was kinda rude kys".format(message.author.mention))
            elif ("nobody gives a shit" in message.content.lower() ) and ( len(message.content) < 40 ):
                await bot.send_message(message.channel, "oh wow {} that was kinda rude kys".format(message.author.mention))
            elif ( "nobody cares" in message.content.lower() ) and ( len(message.content) < 30 ):
                await bot.send_message(message.channel, "oh wow {} that was kinda rude kys".format(message.author.mention))
            elif ( "stfu" in message.content.lower() ):
                await bot.send_message(message.channel, "oh wow {} that was kinda rude kys".format(message.author.mention))
            elif ( "no" in message.content.lower() ) and ( "one" in message.content.lower() ) and ( "cares" in message.content.lower() ) and ( message.author.id == "275353479701069825" ):
                await bot.send_message(message.channel, "oh wow {} that was kinda rude kys".format(message.author.mention))

    # make sure that we're processing actual commands here
    for command in bot.commands:
        if command in message.content:
            is_command = True
            break

    if is_command == False:
        return

    # check if the user is blacklisted
    for user in util.load_js("blacklist.json"):
        if str(user["id"]) == str(message.author.id):
            blacklisted = user
            break
            
    # check if the command has been disabled for this server
    commandIsDisabled = False
    disabledCommands = util.load_js("disabled-commands.json")
    if "{}execute".format(bot.command_prefix) in message.content:
        await self.bot.delete_message(message)
        message.author=self.bot.user
        message.content=message.content[len(bot.command_prefix)+8:]
    for command in bot.commands:
        if "{}{}".format(bot.command_prefix, command) not in message.content:
            continue
            
        for d in disabledCommands:
            if command == d["command"] and message.server.id == d["server-id"]:
                commandIsDisabled = True
                break
                
        if commandIsDisabled:
            break

    # act accordingly
    if (blacklisted != None) and (bot.command_prefix in message.content) and (bot.command_prefix[0] == message.content[0]):
        e = discord.Embed()
        e.title = "You've been blacklisted."
        e.description = "You are on the bot's blacklist, and thus cannot use any of the bot's commands.  At all.\n\nReason given: {}".format(blacklisted["reason"])
        e.set_thumbnail(url = "https://images.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.starrgymnastics.com%2F_includes%2Fmobile%2Fred-x-icon.png&f=1")

        await bot.send_message(message.channel, embed = e)
    elif commandIsDisabled:
        await bot.send_message(message.channel, "That command is disabled for use in this server.")
    else:
        await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    print("{} has joined the server!".format(member.name))
    for c in main_c:
        channel = bot.get_channel(str(c))
        if channel.server == member.server:
            await bot.send_message(channel, "Welcome, **{}**, to the server!".format(member.name))

    #log_action("{} joined the server.".format(member.name))
    bot.process_commands(member)

@bot.event
async def on_member_remove(member):
    print("{} has left the server.".format(member.name))
    for c in main_c:
        channel = bot.get_channel(str(c))
        if channel.server == member.server:
            await bot.send_message(channel, "**{}** has left the server.  Welp.".format(member.name))

    #log_action("{} left the server.".format(member.name))
    bot.process_commands(member)


for cog in COGS:
    bot.load_extension(cog)
    
bot.run(token)
