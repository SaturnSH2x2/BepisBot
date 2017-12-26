import asyncio
import discord
import random
import util
import os

from discord.ext import commands
from cogs.base import Base

HAPPY_SQUIRREL = "http://askthecards.info/tarot/happy_squirrels/simpsons_happy_squirrel.jpg"

MAJOR_ARCANA =  [
                "Fool",
                "Magician",
                "High-Priestess",
                "Empress",
                "Emperor",
                "Hierophant",
                "Lovers",
                "Chariot",
                "Strength",
                "Hermit",
                "Wheel-of-Fortune",
                "Justice",
                "Hanged-Man",
                "Death",
                "Temperance",
                "Devil",
                "Tower",
                "Star",
                "Moon",
                "Sun",
                "Judgement",
                "World"
                ]

class Tarot(Base):
    def __init__(self, bot):
        self.server_decks = util.load_js("server-deck-tarot.json")
        super().__init__(bot)

    """
    @commands.command(pass_context = True)
    async def setDeck(self, ctx, deckName):
        Set the Tarot Deck to use in readings.

        # simple formatting
        origDeckName = deckName
        deckName = deckName.lower()
        deckName = deckName.replace(" ", "-")

        if os.path.exists(os.path.join("assets", "tarot", "{}.json".format(deckName))):
            if ctx.message.server.id not in self.server_decks:
                self.server_decks[ctx.message.server.id] = {}

            self.server_decks[ctx.message.server.id]["deck"] = "{}.json".format(deckName)
            util.save_js("server-deck-tarot.json", self.server_decks)
            await self.bot.say(":thumbsup: Set readings in this server to use the {} deck.".format(origDeckName))
        else:
            await self.bot.say(":thumbsdown: That deck doesn't seem to exist. You'll be able to create and upload your own deck soon, though! Type '{}makeDeck' for more info.".format(self.bot.command_prefix))

    @commands.command(pass_context = True)
    async def makeDeck(self, ctx):
        Sends you a sample template to make a Tarot Deck with.
        await self.bot.whisper("You can create your own deck using JSON files.  In the future, the bot will be able to accept said JSON files and use them as decks, which you can then use in different servers!  Here's the JSON for the default Rider-Waite deck, in case you want to get a head start on your own deck: ")
        await self.bot.send_file( ctx.message.author, os.path.join("assets", "tarot", "rider-waite.json") )
    """

    @commands.command(pass_context = True)
    async def disableExplanations(self, ctx):
        """Disable explanations when doing Tarot Readings."""
        if ctx.message.server.id not in self.server_decks:
            self.server_decks[ctx.message.server.id] = {}

        self.server_decks[ctx.message.server.id]["explanations-enabled"] = False
        util.save_js("server-deck-tarot.json", self.server_decks)

        await self.bot.say(":thumbsup: OK, explanations will be disabled when doing tarot readings.")

    @commands.command(pass_context = True)
    async def enableExplanations(self, ctx):
        """Enable explanations when doing Tarot Readings."""
        if ctx.message.server.id not in self.server_decks:
            self.server_decks[ctx.message.server.id] = {}

        self.server_decks[ctx.message.server.id]["explanations-enabled"] = True
        util.save_js("server-deck-tarot.json", self.server_decks)

        await self.bot.say(":thumbsup: OK, explanations will be enabled when doing tarot readings.")

    @commands.command(pass_context = True)
    async def drawCard(self, ctx):
        """Draws a Tarot Card."""
        try:
            deck = util.load_js( os.path.join("assets", "tarot", self.server_decks[ctx.message.server.id]["deck"]) )
        except KeyError:
            deck = util.load_js( os.path.join("assets", "tarot", "rider-waite.json") )
        explanations = util.load_js( os.path.join("assets", "tarot", "descriptions.json") )

        if random.randint(0, 1):
            card = random.choice(MAJOR_ARCANA)
        else:
            card = random.choice(MAJOR_ARCANA)   # TODO: set this to be of the minor arcana
        cardName = card.replace("-", " ")

        e = discord.Embed()
        e.title = "You drew the {} card.".format(cardName)
        e.set_image( url = deck[card] )

        if ( (ctx.message.server.id in self.server_decks) and (self.server_decks[ctx.message.server.id]["explanations-enabled"]) ) or \
                (ctx.message.server.id not in self.server_decks):
            e.description = explanations[card]
            e.set_footer( text = explanations["source"] )

        await self.bot.say(embed = e)

def setup(bot):
    bot.add_cog(Tarot(bot))
