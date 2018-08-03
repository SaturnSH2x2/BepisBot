# Basically, this class is a way to organize all 
# BepisBot behavior outside of commands.  This way,
# we can keep the on_message method in the BepisBotClient
# cleaner and easier to read.
import asyncio
import discord

class NonCommandBehavior():
    def __init__(self):
        # variable to determine whether or not other
        # BepisBot commands should be executed
        self.continueCommands = True

    def processBehavior(self, message):
        # reset variable
        self.continueCommands = True
