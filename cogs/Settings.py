import discord
import os
import certifi
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from pymongo import MongoClient
e = certifi.where()
mango_url = os.environ['MONGO']
cluster = MongoClient(mango_url, tlsCAFile=e)
db = cluster["cb42"]
swear = db["swear"]


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.swear = self.client.swear
        self.antibot = self.client.antibot

    @commands.slash_command(name="toggle-swear", description="Turn the swear filter on and off")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def toggle_swear(self, ctx, status: discord.Option(str, required=True, choices=['Enabled', 'Disabled'])):
        settings = self.swear[str(ctx.guild.id)].find_one(
            {"guild_id": ctx.guild.id})
        filter_enabled = settings["filter_enabled"]

        if status == "Enabled":
            filter_enabled = True
        elif status == "Disabled":
            filter_enabled = False
        else:
            return await ctx.respond("Invalid status. Use `Enable` or `Disable`.", ephemeral=True)

        self.swear[str(ctx.guild.id)].update_one({"guild_id": ctx.guild.id}, {
            "$set": {"filter_enabled": filter_enabled}})
        if filter_enabled:
            embed = discord.Embed(
                title="Anti-swear filter enabled", color=0x000000)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Anti-swear filter disabled", color=0x000000)
            await ctx.respond(embed=embed)
