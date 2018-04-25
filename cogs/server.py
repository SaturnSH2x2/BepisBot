import asyncio
import discord
import util

from discord.ext import commands
from cogs.base import Base


class Server(Base):
    @commands.command(pass_context=True)
    async def roleInfo(self, ctx, *, roleName: str= None):
        util.nullifyExecute()
        s = ctx.message.server
        r = s.roles
        embeds = {}
        send = False
        for i in range(len(r)):
            permissionText = """"""
            e = discord.Embed()
            e.description = """"""
            e.title = r[i].name
            if r[i].permissions.administrator == True:
                permissionText = """Administrator"""
            else:
                if r[i].permissions.create_instant_invite:
                    permissionText += """Create Instant Invites, """
                if r[i].permissions.kick_members:
                    permissionText += """Kick Members, """
                if r[i].permissions.ban_members:
                    permissionText += """Ban Members, """
                if r[i].permissions.manage_channels:
                    permissionText += """Manage Channels, """
                if r[i].permissions.manage_server:
                    permissionText += """Manage Server, """
                if r[i].permissions.add_reactions:
                    permissionText += """Add Reactions, """
                if r[i].permissions.view_audit_logs:
                    permissionText += """View Audit Logs, """
                if r[i].permissions.manage_messages:
                    permissionText += """Manage Messages, """
                if r[i].permissions.mention_everyone:
                    permissionText += """Mention Everyone, """
                if r[i].permissions.mute_members:
                    permissionText += """Mute Members, """
                if r[i].permissions.deafen_members:
                    permissionText += """Deafen Members, """
                if r[i].permissions.move_members:
                    permissionText += """Move Members, """
                if r[i].permissions.change_nickname:
                    permissionText += """Change Nickname, """
                if r[i].permissions.manage_nicknames:
                    permissionText += """Manage Nicknames, """
                if r[i].permissions.manage_roles:
                    permissionText += """Manage Roles, """
                if r[i].permissions.manage_webhooks:
                    permissionText += """Manage Webhooks, """
                if r[i].permissions.manage_emojis:
                    permissionText += """Manage Emojis, """
                if len(permissionText) > 0:
                    permissionText = permissionText[:-2]
            e.description = e.description+"""ID: {}
Color: rgb({},{},{})
Displayed Separatly: {}
Positon: {}
Managed: {}
Mentionable: {}
Created At: {}

**Permissions**
{}
""".format(r[i].id, r[i].color.r, r[i].color.g, r[i].color.b, r[i].hoist, r[i].position, r[i].managed, r[i].mentionable, r[i].created_at, permissionText)
            e.description += """
"""
            e.color = r[i].color
            e.set_thumbnail(url=s.icon_url)
            embeds[r[i].name] = e
        if roleName == "*all*":
            for name, embedded in embeds.items():
                await self.bot.say(embed=embedded)
        elif roleName != None:
            try:
                await self.bot.say(embed=embeds[roleName])
            except:
                await self.bot.say("Invalid role")
        else:
            await self.bot.say("Please enter the name of a role (Don't @ them!)")

    @commands.command(pass_context=True)
    async def serverInfo(self, ctx):
        util.nullifyExecute()
        """Gives various statistics regarding a server."""
        s = ctx.message.server
        e = discord.Embed()

        e.title = "Server Statistics"
        e.description = """
Name: {n}
Number of Roles: {r}
Server Region: {sr}
Number of Emojis: {em}
Number of Members: {m}
ID: {i}
Owner: {o}
Created at: {c}
						""".format(n=s.name, r=len(s.roles), sr=s.region, em=len(s.emojis),
                 m=s.member_count, i=s.id, o=s.owner.name, c=s.created_at)
        e.set_thumbnail(url=s.icon_url)

        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(Server(bot))
