import asyncio
import discord
import os

# Base cog class, from which all other cogs inherit.
class Base:
    # Folder to put all per-cog JSON data.
    # This helps keep the repo folder clean.
    JSON_PATH = "jsondata"

    # Temporary file storage path.  Useful for
    # cogs that need to create temporary files.
    TEMP_PATH = "temp"

    # Metadata file path.  Where stuff like chat
    # logs, recordings, and other extraneous
    # data is stored and can be accessed by the
    # user.
    METADATA_PATH = "metadata"

    def __init__(self, bot):
        self.bot = bot
        print("{} cog set up successfully.".format(self.__class__.__name__))

        # checks to see that each directory exists on startup.
        # Probably wasteful to have this run for each cog loaded,
        # but it's only run at startup, so it shouldn't have
        # too much impact.
        for directory in (self.JSON_PATH, self.TEMP_PATH, self.METADATA_PATH):
            if not os.path.exists(directory):
                print("Creating directory:  %s" % (directory))
                os.mkdir(directory)