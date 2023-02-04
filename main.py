import asyncio
import datetime
import io
import os
import random
from collections import defaultdict
from datetime import *
from datetime import timedelta
from io import *

import aiohttp
import certifi
import discord
import pymongo
from bs4 import BeautifulSoup
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *
from dotenv import load_dotenv
from googlesearch import search
from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient

from badwords import *
from defs import *

load_dotenv()
e = certifi.where()
intents = discord.Intents().all()
token_ = os.environ['TOKEN']
mango_url = os.environ['MONGO']
cluster = MongoClient(mango_url, tlsCAFile=e)
db = cluster["cb42"]
collection = db["level"]
swear = db["swear"]
warnings = {}
timeout_duration = 60

client = commands.Bot(command_prefix=".",
                      case_insensitive=True, help_command=None, intents=intents)

client.launch_time = datetime.utcnow()


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f"on {len(client.guilds)} servers"))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="/help | cb42bot.tk"))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="Slash Commands!"))
    print(f"{client.user.name} says, Hello world")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


async def status():
    await client.wait_until_ready()

    statuses = [f"on {len(client.guilds)} servers", "/help"]

    while not client.is_closed():

        status = random.choice(statuses)
        await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name=status))

        await asyncio.sleep(10)


@client.event
async def on_guild_join(guild):
    swear[str(guild.id)].insert_one(
        {"guild_id": guild.id, "filter_enabled": False})


@client.event
async def on_member_join(member):
    await send_welcome_message(member)


@client.event
async def on_member_remove(member):
    await send_leave_message(member)


@client.event
async def on_message_edit(before, after):
    content = after.content.lower()
    for word in bad_words:
        if word.lower() in content:
            await after.delete()
            return

# SLASH


@client.slash_command(name="help", description="Get all the commands of the bot")
@commands.cooldown(1, 5, commands.BucketType.user)
async def help(ctx):
    embed = discord.Embed(
        title="CB42 help panel",
        url="https://cb42bot.tk",
        description="CB42 is an all in one bot you ever need.."
    )
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/943039554108133378/1005764186485305345/standard.gif")

    dropdowns = DropDownMenu()

    await ctx.respond(embed=embed, view=dropdowns)


@client.slash_command(name="password", description="Makes you a random password")
@commands.cooldown(1, 15, commands.BucketType.user)
async def password(ctx):
    author = ctx.author
    await ctx.respond("Check your DM's‼", ephemeral=True)
    await ctx.author.send(f"Your secret password is: `{am}`")


@client.slash_command(name="rank", description="Shows the rank of a user")
@commands.cooldown(1, 5, commands.BucketType.user)
async def rank(ctx):
    author_id = ctx.author.id
    level = collection.find_one(
        {"_id": author_id})["Level"]
    xp = collection.find_one({"_id": author_id})["XP"]

    if author_id is None:
        await ctx.respond("You did not level in this server yet!")

    ava = ctx.author.avatar.url
    response = requests.get(ava)
    imge = Image.open(BytesIO(response.content))
    imge = imge.resize((100, 100))
    img = Image.new("RGB", (400, 200), color=(73, 80, 87))
    img.paste(imge, (290, 10))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 36)
    draw.text((10, 10), f"Level: {level}", font=font, fill=(255, 255, 255))
    draw.text((10, 130), "XP", font=font, fill=(255, 255, 255))
    draw.rectangle([(10, 170), (10 + xp * 0.3, 190)], fill=(247, 134, 28))

    img.save("rank.png")
    with open("rank.png", "rb") as f:
        await ctx.respond(file=discord.File(f))


@client.slash_command(name="uptime", description="Check how long CB42 has been up for")
@commands.cooldown(1, 5, commands.BucketType.user)
async def uptime(ctx):
    delta_uptime = datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(title="**CB42's Uptime**",
                          description=f"`CB42 has been online for -` {days}d, {hours}h, {minutes}m, {seconds}s")

    await ctx.respond(embed=embed, ephemeral=True)

# SLASH


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    if message.author.bot:
        return

    if client.user.mentioned_in(message) and message.mention_everyone is False:
        embed = discord.Embed(
            title="CB42", description="Type `/help` for more info")
        await message.channel.send(embed=embed, delete_after=10)
        return

    author_id = message.author.id
    guild_id = message.guild.id

    author = message.author

    user_id = {"_id": author_id}

    if (collection.count_documents({}) == 0):
        user_info = {"_id": author_id,
                     "GuildID": guild_id, "Level": 1, "XP": 0}
        collection.insert_one(user_info)

    if (collection.count_documents(user_id) == 0):
        user_info = {"_id": author_id,
                     "GuildID": guild_id, "Level": 1, "XP": 0}
        collection.insert_one(user_info)

    exp = collection.find(user_id)
    for xp in exp:
        cur_xp = xp["XP"]

        new_xp = cur_xp + 1

    collection.update_one({"_id": author_id}, {
                          "$set": {"XP": new_xp}}, upsert=True)

    lvl = collection.find(user_id)
    for levl in lvl:
        lvl_start = levl["Level"]

        new_level = lvl_start + 1

    if cur_xp >= round(5 * (lvl_start ** 4 / 5)):
        collection.update_one({"_id": author_id}, {
                              "$set": {"Level": new_level}}, upsert=True)
        await message.channel.send(f"{message.author.mention} is now level **{new_level}**!")

    settings = swear[str(message.guild.id)].find_one(
        {"guild_id": message.guild.id})
    filter_enabled = settings["filter_enabled"]

    if filter_enabled:
        if any(word in message.content.lower() for word in bad_words):
            await message.delete()
            embed = Embed(title="Inappropriate language detected",
                          description="Your message contained inappropriate language.", color=0x000000, delete_after=3)
            await message.channel.send(embed=embed)
    message.content = message.content.lower()
    await client.process_commands(message)
    await scam_check(message)
try:
    client.loop.create_task(status())
    client.run(token_)
except:
    print("Make sure the token is correct!")
