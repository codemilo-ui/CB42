import random
import randfacts
import json
import requests
import string
from datetime import *
from datetime import timedelta
import aiohttp
import discord
import certifi
from pymongo import MongoClient
import os
from discord import *
from discord.ext import commands
from discord.ui import *
from discord.ext.commands import *
e = certifi.where()
mango_url = os.environ['MONGO']
cluster = MongoClient(mango_url, tlsCAFile=e)
db = cluster["cb42"]
swear = db["swear"]
wel = db["welcomeandleave"]
lev = db["welcomeandleave"]
topics = ["What's your favorite quote",
          "Think of something your own",
          "What's your Favorite band",
          "What's the time for you?",
          "What's your favorite book?",
          "What's your favorite song?",
          "When did you join this Discord server?",
          "If you could, would you go to space?",
          "What skill would you like to have?",
          "What do you do most of your time? (School/work don't count)",
          "What is your favorite subject at school?",
          "What is your favorite YouTube channel?",
          "What battery percentage is your phone on?",
          "What are your hobbies?",
          "Do you play any sports?",
          "If you could be an animal, what would you be?",
          "If you could have any ability in the world, what would it be?",
          "You can choose a super power but the first person to reply can choose a side effect",
          "What country do you always wanted/want to visit? Why?",
          "What place in the Universe would you like to visit?",
          "How many languages do you speak",
          "If you could learn any language in the world, what would it be?"]


def get_fact(): return randfacts.get_fact()
def get_topic(): return random.choice(topics)


def in_list(str_, list_):
    text = str_.lower().split()
    for element in text:
        for item in list_:
            if element.replace(item, "") != element:
                return True
    return False


async def kick_user(ctx, member, reason):
    await member.kick(reason=reason)
    return True


async def ban_user(ctx, member, reason):
    await member.ban(reason=reason)
    return True


async def timeout_user(ctx, member, reason, timeouttime):
    duration = timedelta(seconds=timeouttime)
    try:
        await member.timeout_for(duration, reason=reason)
    except HTTPException:
        await ctx.reply(
            'I failed to Timeout this member due to a Discord Server error'
        )
        return False
    return True


def get_welcome_channel_id(server_id):
    return wel.settings.find_one({"server_id": server_id, "name": "welcome_channel"})["channel_id"]


def get_leave_channel_id(server_id):
    return lev.settings.find_one({"server_id": server_id, "name": "leave_channel"})["channel_id"]


def update_welcome_channel_id(server_id, channel_id):
    wel.settings.update_one({"server_id": server_id, "name": "welcome_channel"}, {
                            "$set": {"channel_id": channel_id}})


def update_leave_channel_id(server_id, channel_id):
    lev.settings.update_one({"server_id": server_id, "name": "leave_channel"}, {
                            "$set": {"channel_id": channel_id}})


async def send_welcome_message(member):
    server_id = member.guild.id
    channel_id = wel.settings.find_one(
        {"server_id": server_id, "name": "welcome_channel"})["channel_id"]

    channel = client.get_channel(channel_id)

    welcome_message = f"Welcome to the server, {member.name}!"
    embed = discord.Embed(title=welcome_message)
    embed.set_thumbnail(url=member.avatar.url)

    await channel.send(embed=embed)


async def send_leave_message(member):
    server_id = member.guild.id
    channel_id = lev.settings.find_one(
        {"server_id": server_id, "name": "leave_channel"})["channel_id"]

    channel = client.get_channel(channel_id)

    welcome_message = f"{member.name} has just left the server!"
    embed = discord.Embed(title=welcome_message)

    await channel.send(embed=embed)


def get_shower():
    with open("./database/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return random.choice(data["thoughts"])


async def scam_check(message):
    with open('./database/blocked_links.json', 'r') as f1:
        scam_links = json.load(f1)
    scam_links = scam_links['domains']
    for links in scam_links:
        if links in message.content:
            await message.delete()
            await message.channel.send("You can't send this link! ❌", delete_after=3)


class DropDownMenu(discord.ui.View):
    @discord.ui.select(placeholder="Select a value", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Moderation",
                             description="Moderation commands", emoji="🚩"),
        discord.SelectOption(
            label="Fun", description="Fun commands", emoji="🚀"),
        discord.SelectOption(
            label="Information", description="Information commands", emoji="ℹ"),
        discord.SelectOption(
            label="Settings", description="Settings commands", emoji="🔧"),
        discord.SelectOption(
            label="Level", description="Level commands", emoji="⬆")
    ])
    async def callback(self, select, interaction: discord.Interaction):
        if select.values[0] == "Moderation":
            view = View()
            modembed = discord.Embed(
                title="Moderation commands",
                description="`mute`, `purge`, `slowmode`, `removerole`, `unban`, `addrole`, `kick`, `ban`",
            )

            await interaction.response.send_message(embed=modembed, view=view, ephemeral=True)

        if select.values[0] == "Fun":
            view = View()
            funembed = discord.Embed(
                title="Fun commands",
                description="`dog`, `cat`, `dice`, `eightball`, `meme`, `fact`, `topic`, `showerthought`",
            )

            await interaction.response.send_message(embed=funembed, view=view, ephemeral=True)

        if select.values[0] == "Information":
            view = View()
            inembed = discord.Embed(
                title="Information commands",
                description="`uptime`, `ping`, `membercount`, `avatar`, `invite`, `credits`, `help`",
            )

            await interaction.response.send_message(embed=inembed, view=view, ephemeral=True)

        if select.values[0] == "Settings":
            view = View()
            lnembed = discord.Embed(
                title="Settings commands",
                description="`set-welcome-channel`, `set-leave-channel`, `toggle-swear`",
            )

            await interaction.response.send_message(embed=lnembed, view=view, ephemeral=True)
        if select.values[0] == "Level":
            view = View()
            lnembed = discord.Embed(
                title="Level commands",
                description="`rank`",
            )

            await interaction.response.send_message(embed=lnembed, view=view, ephemeral=True)


length = random.randint(12, 25)
lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
symbols = string.punctuation

all = lower + upper + num + symbols

temp = random.sample(all, length)

am = "".join(temp)
