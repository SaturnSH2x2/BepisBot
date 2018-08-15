import asyncio
import discord
import random
import util
import os

from discord.ext import commands
from cogs.base import Base

from os.path import join as opj

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
        self.cfgPath = opj(self.JSON_PATH, "tarot.json")
        self.guild_decks = util.load_js(self.cfgPath)
        self.deck = util.load_js( opj("assets", "tarot", "rider-waite.json") )
        self.explanations = util.load_js( opj("assets", 
                            "tarot", "descriptions.json") )
        super().__init__(bot)

        print(self.guild_decks)

    @commands.command()
    async def setExplanations(self, ctx, setEx : bool):
        "Set explanations for tarot readings, per user."
        self.guild_decks[str(ctx.author.id)] = setEx
        util.save_js(self.cfgPath, self.guild_decks)

        if setEx:
            enStr = "enabled"
        else:
            enStr = "disabled"

        await ctx.send("Explanations for readings have been **%s**." % (enStr))

    @commands.command()
    async def drawCard(self, ctx):
        "Draws a Tarot Card. Major Arcana only, at the moment."
        if random.randint(0, 1):
            card = random.choice(MAJOR_ARCANA)
        else:
            card = random.choice(MAJOR_ARCANA)
        cardName = card.replace("-", " ")

        e = discord.Embed()
        e.title = "You drew the {} card.".format(cardName)
        e.set_image( url = self.deck[card] )

        try:
            if self.guild_decks[str(ctx.author.id)]:
                e.description = self.explanations[card]
                e.set_footer( text = self.explanations["source"] )
        except KeyError:
            self.guild_decks[str(ctx.author.id)] = True
            e.description = self.explanations[card]
            e.set_footer( text = self.explanations["source"] )

        await ctx.send(embed = e)

def setup(bot):
    bot.add_cog(Tarot(bot))
