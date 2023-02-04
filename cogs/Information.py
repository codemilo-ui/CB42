import discord
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *


class Information(commands.Cog):
    def __init__(self, client):
        self.client = client

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
    @commands.command(name="avatar", description="Shows the profile pic of a member")
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

    @commands.command(name="invite", description="Invite CB42 to your server")
    @cooldown(1, 5, BucketType.user)
    async def invite(self, ctx):
        invitebt = discord.Button(
            label="Invite CB42",
            url="https://discord.com/api/oauth2/authorize?client_id=1004727274031038574&permissions=8&redirect_uri=https%3A%2F%2Fcb42bot.tk&response_type=code&scope=bot%20connections%20applications.commands"
        )
        view = discord.View()
        view.add_item(invitebt)

        embed = discord.Embed(title=f"Invite {self.client.user.name}",
                              description=f"Invite CB42 from [here](https://discord.com/api/oauth2/authorize?client_id=1004727274031038574&permissions=8&redirect_uri=https%3A%2F%2Fcb42bot.tk&response_type=code&scope=bot%20connections%20applications.commands)")

        await ctx.respond(embed=embed, view=view, ephemeral=True)

    @commands.command(name="credits", description="Shows who made CB42")
    @cooldown(1, 5, BucketType.user)
    async def credits(self, ctx):
        cbt_button = discord.Button(
            label="Github",
            url="https://github.com/CB42Bot/CB42"
        )
        view = discord.View()
        view.add_item(cbt_button)

        embed = discord.Embed(
            title=f"Developers of {self.bot.user.name}",
            description=f"CB42 was made by [sudo-adrian](https://github.com/sudo-adrian) and [codemilo-ui](https://github.com/codemilo-ui)"
        )

        await ctx.respond(embed=embed, view=view)

def setup(client):
    client.add_cog(Information(client))