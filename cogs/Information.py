import datetime
from datetime import *

import discord
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *


class Information(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(name="uptime", description="Check how long CB42 has been up for")
    @cooldown(1, 5, commands.BucketType.user)
    async def uptime(self, ctx):
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(title="**CB42's Uptime**",
                              description=f"`CB42 has been online for -` {days}d, {hours}h, {minutes}m, {seconds}s")

        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="ping", description="Get the bots latency")
    @cooldown(1, 15, BucketType.user)
    async def ping(self, ctx):
        l = round(self.client.latency * 1000, 1)
        await ctx.respond(f"The bots ping is: `{l}`", ephemeral=True)

    @slash_command(name="membercount", description="Get the membercount of the specific server")
    @cooldown(1, 5, BucketType.user)
    async def membercount(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title="Membercount of this server",
                              description=f"**This server has** `{guild.member_count}` **members**")

        await ctx.respond(embed=embed)

    @slash_command(name="avatar", description="Shows the profile pic of a member")
    @cooldown(1, 5, BucketType.user)
    async def avatar(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        ava = member.avatar.url
        e = member.id
        embed = discord.Embed(
            title=f"Avatar of {member.name}#{member.discriminator}")
        embed.set_image(url=ava)
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="invite", description="Invite CB42 to your server")
    @cooldown(1, 5, BucketType.user)
    async def invite(self, ctx):
        embed = discord.Embed(title=f"Invite {self.client.user.name}",
                              description=f"`Invite CB42 from` [here](https://discord.com/api/oauth2/authorize?client_id=1004727274031038574&permissions=8&redirect_uri=https%3A%2F%2Fcb42bot.tk&response_type=code&scope=bot%20connections%20applications.commands)")

        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="credits", description="Shows who made CB42")
    @cooldown(1, 5, BucketType.user)
    async def credits(self, ctx):
        embed = discord.Embed(
            title=f"Developers of [CB42](https://github.com/codemilo-ui/CB42)",
            description=f"**CB42 was made by** [adzsx](https://github.com/adzsx) **and** [codemilo-ui](https://github.com/codemilo-ui)"
        )
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Information(client))
