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
wel = db["welcomeandleave"]
lev = db["welcomeandleave"]

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="set-welcome-channel", description="Set the welcome channel")
    @commands.has_permissions(kick_members=True)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel):
        existing_channel = wel.settings.find_one(
            {"server_id": ctx.guild.id, "name": "welcome_channel"})
        if existing_channel is None:
            wel.settings.insert_one(
                {"server_id": ctx.guild.id, "name": "welcome_channel", "channel_id": channel.id})
        else:
            wel.settings.update_one({"server_id": ctx.guild.id, "name": "welcome_channel"}, {
                "$set": {"channel_id": channel.id}})
        await ctx.respond(f"The designated channel has been set to {channel.mention}.")

    @commands.command(name="set-leave-channel", description="Set the leave channel")
    @commands.has_permissions(kick_members=True)
    async def setleavechannel(self, ctx, channel: discord.TextChannel):
        existing_channel = lev.settings.find_one(
            {"server_id": ctx.guild.id, "name": "leave_channel"})
        if existing_channel is None:
            lev.settings.insert_one(
                {"server_id": ctx.guild.id, "name": "leave_channel", "channel_id": channel.id})
        else:
            lev.settings.update_one({"server_id": ctx.guild.id, "name": "leave_channel"}, {
                "$set": {"channel_id": channel.id}})
        await ctx.respond(f"The designated channel has been set to {channel.mention}.")

    @slash_command(name="toggle-swear", description="Turn the swear filter on and off")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def toggle_swear(self, ctx, status: discord.Option(str, required=True, choices=['Enabled', 'Disabled'])):
        settings = swear[str(ctx.guild.id)].find_one(
            {"guild_id": ctx.guild.id})
        filter_enabled = settings["filter_enabled"]

        if status == "Enabled":
            filter_enabled = True
        elif status == "Disabled":
            filter_enabled = False
        else:
            return await ctx.respond("Invalid status. Use `Enable` or `Disable`.", ephemeral=True)

        swear[str(ctx.guild.id)].update_one({"guild_id": ctx.guild.id}, {
            "$set": {"filter_enabled": filter_enabled}})
        if filter_enabled:
            embed = discord.Embed(
                title="Anti-swear filter enabled", color=0x000000)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Anti-swear filter disabled", color=0x000000)
            await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Settings(client))
