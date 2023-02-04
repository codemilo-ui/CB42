import discord
from discord import *
from discord.ext import commands
from discord.ext.commands import *


class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @slash_command(name="test", description="Shows all available commands")
    async def test_command(self, ctx):
        cogs = self.client.cogs
        embeds = []

        for cog in cogs:
            cog_commands = self.client.get_cog(cog).get_commands()
            command_list = ""
            for command in cog_commands:
                command_list += f"{command.name}\n"

            embed = discord.Embed(
                title=f"{cog} Commands",
                description=command_list,
                color=discord.Color.blue()
            )
            embeds.append(embed)

        await ctx.send(embed=embeds[0])
        for embed in embeds[1:]:
            await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Help(client))
