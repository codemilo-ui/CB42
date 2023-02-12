import discord
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *
from defs import *
import psutil

mem_usage = psutil.virtual_memory()

print(f"Free: {mem_usage.percent}%")
print(f"Total: {mem_usage.total/(1024**3):.2f}G")
print(f"Used: {mem_usage.used/(1024**3):.2f}G")


class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @slash_command(name="help", description="Get all the commands of the bot")
    @cooldown(1, 5, commands.BucketType.user)
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="CB42 help panel",
            url="https://cb42bot.tk",
            description="CB42 is an all in one bot you ever need.."
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/943039554108133378/1005764186485305345/standard.gif")

        dropdowns = DropDownMenu(timeout=60)

        await ctx.respond(embed=embed, view=dropdowns)

    @slash_command(name="usage", description="Get all the commands of the bot")
    @cooldown(1, 5, commands.BucketType.user)
    async def usage(self, ctx):
        embed = discord.Embed(
            title="CB42 help panel",
            url="https://cb42bot.tk",
            description=f"Free: {mem_usage.percent}%"
        )
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Help(client))
