import datetime
import os
from datetime import *
from datetime import timedelta
from io import *

import aiohttp
import certifi
import discord
import pymongo
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from dotenv import load_dotenv
from pymongo import MongoClient

from database.badwords import *
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
