import asyncio
from collections import defaultdict
import datetime
import os
import random
from datetime import *
from datetime import timedelta

import aiohttp
from googlesearch import search
import certifi
import discord
import pymongo
from bs4 import BeautifulSoup
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *
from dotenv import load_dotenv
from pymongo import MongoClient
from PIL import Image, ImageDraw, ImageFont
import io
from io import *
from defs import *

load_dotenv()
e = certifi.where()
intents = discord.Intents().all()
token_ = os.environ['TOKEN']
mango_url = os.environ['MONGO']
cluster = MongoClient(mango_url, tlsCAFile=e)
db = cluster["cb42"]
collection = db["level"]
wel = db["welcomeandleave"]
lev = db["welcomeandleave"]
swear = db["swear"]
antibot = db["botset"]
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


def get_welcome_channel_id():
    return wel.settings.find_one({"name": "welcome_channel"})["channel_id"]


def get_leave_channel_id():
    return lev.settings.find_one({"name": "leave_channel"})["channel_id"]


def update_welcome_channel_id(channel_id):
    wel.settings.update_one({"name": "welcome_channel"}, {
                            "$set": {"channel_id": channel_id}})


def update_leave_channel_id(channel_id):
    lev.settings.update_one({"name": "leave_channel"}, {
                            "$set": {"channel_id": channel_id}})


async def send_welcome_message(member):
    channel_id = get_welcome_channel_id()

    channel = client.get_channel(channel_id)

    welcome_message = f"Welcome to the server, {member.mention}! We're glad to have you here!"
    embed = discord.Embed(title=welcome_message)
    embed.set_thumbnail(url=member.avatar.url)

    await channel.send(embed=embed)


async def send_leave_message(member):
    channel_id = get_leave_channel_id()

    channel = client.get_channel(channel_id)

    welcome_message = f"{member.name} has just left the server!"
    embed = discord.Embed(title=welcome_message)

    await channel.send(embed=embed)


@client.event
async def on_guild_join(guild):
    swear[str(guild.id)].insert_one({"guild_id": guild.id, "filter_enabled": False})


@client.event
async def on_member_join(member):
    await send_welcome_message(member)
    guild_id = str(member.guild.id)
    guild_settings = antibot.find_one({"guild_id": guild_id})
    if guild_settings and guild_settings["anti_bot"] and member.bot:
        await member.kick()


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


async def scam_check(message):
    with open('blocked_links.json', 'r') as f1:
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
            label="Level", description="Level commands", emoji="⬆")
    ])
    async def callback(self, select, interaction: discord.Interaction):
        if select.values[0] == "Moderation":
            view = View()
            modembed = discord.Embed(
                title="Moderation commands",
                description="`clear`, `kick`, `ban`, `unban`, `membercount`, `setprefix`, `addrole`, `delrole`, `mute`, `unmute`, `set-welcome-channel`, `set-leave-channel`",
            )

            await interaction.response.send_message(embed=modembed, view=view, ephemeral=True)

        if select.values[0] == "Fun":
            view = View()
            funembed = discord.Embed(
                title="Fun commands",
                description="`cat`, `dog`, `meme`, `showerthought`, `dice`, `password`, `eightball`",
            )

            await interaction.response.send_message(embed=funembed, view=view, ephemeral=True)

        if select.values[0] == "Information":
            view = View()
            inembed = discord.Embed(
                title="Information commands",
                description="`invite`, `ping`, `credits`, `uptime`, `website-status`",
            )

            await interaction.response.send_message(embed=inembed, view=view, ephemeral=True)

        if select.values[0] == "Level":
            view = View()
            lnembed = discord.Embed(
                title="Level commands",
                description="`rank`",
            )

            await interaction.response.send_message(embed=lnembed, view=view, ephemeral=True)

# SLASH

@client.slash_command(name="google", description="Google something...")
@commands.cooldown(1, 5, commands.BucketType.user)
async def google(ctx, query: Option(str)):
    msg = await ctx.respond(f"Searching...🔍")
    embed = discord.Embed(title=f"Search results", description=f"Query: {query}")
    for j in search(query, num_results=4):
        embed.add_field(name="Search result:", value=j)
    await msg.edit(embed=embed)

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


@client.slash_command(name="ping", description="Get the bots latency")
@commands.cooldown(1, 15, commands.BucketType.user)
async def ping(ctx):
    l = round(client.latency * 1000, 1)
    await ctx.respond(f"The bots ping is: `{l}`", ephemeral=True)

@client.slash_command(name="website-status", description="Check the status of a website")
@commands.cooldown(1, 5, commands.BucketType.user)
async def website_status(ctx, url: str):
    try:
        await ctx.defer()
        req = requests.get(url)
        await ctx.defer()
        if req.status_code == 200:
            embed = discord.Embed(
                title="The website is running! ✅", description=f"`{url}` is up and running")
            await ctx.respond(embed=embed)
        else:
            await ctx.defer()
            embed = discord.Embed(title="The website is running! ✅",
                                  description=f"`{url}` returned status code **{req.status_code}**")
            await ctx.respond(embed=embed)
    except:
        await ctx.defer()
        await ctx.respond(f'Error occured while checking the status of {url}', ephemeral=True)


@client.slash_command(name="membercount", description="Get the membercount of the specific server")
@commands.cooldown(1, 5, commands.BucketType.user)
async def membercount(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="Membercount of this server",
                          description=f"**This server has** `{guild.member_count}` **members**")

    await ctx.respond(embed=embed)

@client.slash_command(name="set-welcome-channel", description="Set the welcome channel")
@commands.has_permissions(kick_members=True)
async def setwelcomechannel(ctx, channel: discord.TextChannel):
    existing_channel = wel.settings.find_one({"name": "welcome_channel"})
    if existing_channel is None:
        wel.settings.insert_one(
            {"name": "welcome_channel", "channel_id": channel.id})
    else:
        wel.settings.update_one({"name": "welcome_channel"}, {
                                "$set": {"channel_id": channel.id}})
    await ctx.respond(f"The designated channel has been set to {channel.mention}.")


@client.slash_command(name="set-leave-channel", description="Set the leave channel")
@commands.has_permissions(kick_members=True)
async def setleavechannel(ctx, channel: discord.TextChannel):
    existing_channel = lev.settings.find_one({"name": "leave_channel"})
    if existing_channel is None:
        lev.settings.insert_one(
            {"name": "leave_channel", "channel_id": channel.id})
    else:
        lev.settings.update_one({"name": "leave_channel"}, {
                                "$set": {"channel_id": channel.id}})
    await ctx.respond(f"The designated channel has been set to {channel.mention}.")


@client.slash_command(name="avatar", description="Shows the profile pic of a member")
@commands.cooldown(1, 5, commands.BucketType.user)
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author
    ava = member.avatar.url
    e = member.id
    embed = discord.Embed(
        title=f"Avatar of {member.name}#{member.discriminator}")
    embed.set_image(url=ava)
    await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(name="invite", description="Invite CB42 to your server")
@commands.cooldown(1, 5, commands.BucketType.user)
async def invite(ctx):
    invitebt = Button(
        label="Invite CB42",
        url="https://discord.com/api/oauth2/authorize?client_id=1004727274031038574&permissions=8&redirect_uri=https%3A%2F%2Fcb42bot.tk&response_type=code&scope=bot%20connections%20applications.commands"
    )
    view = View()
    view.add_item(invitebt)

    embed = discord.Embed(title=f"Invite {client.user.name}",
                          description=f"Invite CB42 from [here](https://discord.com/api/oauth2/authorize?client_id=1004727274031038574&permissions=8&redirect_uri=https%3A%2F%2Fcb42bot.tk&response_type=code&scope=bot%20connections%20applications.commands)")

    await ctx.respond(embed=embed, view=view, ephemeral=True)


@client.slash_command(name="credits", description="Shows who made CB42")
@commands.cooldown(1, 5, commands.BucketType.user)
async def credits(ctx):
    cbt = Button(
        label="Github",
        url="https://github.com/CB42Bot/CB42"
    )
    view = View()
    view.add_item(cbt)

    embed = discord.Embed(title=f"Developers of {client.user.name}",
                          description=f"CB42 was made by [sudo-adrian](https://github.com/sudo-adrian) and [codemilo-ui](https://github.com/codemilo-ui)")

    await ctx.respond(embed=embed, view=view, ephemeral=True)


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
            embed = Embed(title="Inappropriate language detected", description="Your message contained inappropriate language.", color=0x000000, delete_after=3)
            await message.channel.send(embed=embed)
    message.content = message.content.lower()
    await client.process_commands(message)
    await scam_check(message)
try:
    client.loop.create_task(status())
    client.run(token_)
except:
    print("Make sure the token is correct!")
