import discord
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *
from defs import *
import psutil


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

    @slash_command(name="usage", description="CB42 resource usage")
    @cooldown(1, 5, commands.BucketType.user)
    async def usage(self, ctx):
        embed = discord.Embed(
            title="CB42 host",
            description=f"**CB42 runs on:**"
        )
        embed.add_field(name="OS", value=f"`{psutil.os.name}`", inline=False)

        cpu_usage = psutil.cpu_percent(interval=1)
        embed.add_field(name="CPU usage", value=f"`{cpu_usage}%`", inline=False)

        mem = psutil.virtual_memory()
        mem_usage = mem.used / mem.total * 100
        embed.add_field(name="Memory usage",
                        value=f"`{round(mem_usage, 2)}%`", inline=False)

        num_cores = psutil.cpu_count(logical=False)
        embed.add_field(name="CPU cores", value=f"`{num_cores}`", inline=False)
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Help(client))
