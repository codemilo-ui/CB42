import asyncio
import datetime
import os
import random
from datetime import *
from datetime import timedelta

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
coll = db["prefix"]
collection = db["level"]
wel = db["welcomeandleave"]
lev = db["welcomeandleave"]
ver = db["verify"]


def prefix(client, message):
    prefix = coll.find_one({"_id": message.guild.id})["prefix"]
    return prefix


client = commands.Bot(command_prefix=prefix,
                      case_insensitive=True, help_command=None, intents=intents)

client.launch_time = datetime.utcnow()


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f"on {len(client.guilds)} servers"))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="cb!help | cb42bot.tk"))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="Slash Commands!"))
    print(f"{client.user.name} says, Hello world")


async def status():
    await client.wait_until_ready()

    statuses = [f"on {len(client.guilds)} servers", "cb!help"]

    while not client.is_closed():

        status = random.choice(statuses)
        await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name=status))

        await asyncio.sleep(10)


def get_verify_role_id(server_id):
    return ver.settings.find_one({"name": "verify_role", "server_id": server_id})["role_id"]

# Update the verify role ID in the database


def update_verify_role_id(server_id, role_id):
    ver.settings.update_one({"name": "verify_role", "server_id": server_id}, {
                            "$set": {"role_id": role_id}})


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
    # Get the channel ID
    channel_id = get_welcome_channel_id()

    # Get the channel
    channel = client.get_channel(channel_id)

    # Create the welcome message
    welcome_message = f"Welcome to the server, {member.mention}! We're glad to have you here!"
    embed = discord.Embed(title=welcome_message)
    embed.set_thumbnail(url=member.avatar.url)

    # Send the welcome message
    await channel.send(embed=embed)


async def send_leave_message(member):
    channel_id = get_leave_channel_id()

    channel = client.get_channel(channel_id)

    welcome_message = f"{member.name} has just left the server!"
    embed = discord.Embed(title=welcome_message)

    await channel.send(embed=embed)


@client.event
async def on_guild_join(guild):
    coll.insert_one({"_id": guild.id, "prefix": "cb!"})


@client.event
async def on_guild_remove(guild):
    coll.delete_one({"_id": guild.id})


@client.event
async def on_member_join(member):
    await send_welcome_message(member)


@client.event
async def on_member_remove(member):
    await send_leave_message(member)


async def scam_check(message):
    with open('blocked_links.json', 'r') as f1:
        scam_links = json.load(f1)
    scam_links = scam_links['domains']
    for links in scam_links:
        if links in message.content:
            await message.delete()
            await message.channel.send("You can't send this link! ❌", delete_after=3)


@client.command()
async def verify(ctx):
    member = ctx.author
    # Get the verify role ID
    verify_role_id = get_verify_role_id(ctx.guild.id)
    role = discord.utils.get(ctx.guild.roles, id=verify_role_id)
    # Check if the verify role has been set
    if role is None:
        await ctx.send("No verify role has been set.")
        return
    # Add the role to the member
    await member.edit(roles=role)
    await ctx.send(f"{ctx.author.mention} has been verified!")


@client.command()
async def setverifyrole(ctx, role: discord.Role):
    # Check if the role exists
    if role in ctx.guild.roles:
        # Update the verify role ID in the database
        update_verify_role_id(ctx.guild.id, role.id)
        await ctx.send(f"The designated verify role has been set to {role.name}.")
    else:
        # Insert the verify role into the database
        ver.settings.insert_one(
            {"name": "verify_role", "server_id": ctx.guild.id, "role_id": role.id})
        await ctx.send(f"The designated verify role has been set to {role.name}.")


@client.command(aliases=['prefix'])
@commands.has_permissions(manage_guild=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def setprefix(ctx, prefix=None):
    if prefix is None:
        await ctx.reply("Please enter a prefix!", delete_after=5)
    else:
        coll.update_one({"_id": ctx.guild.id}, {
                        "$set": {"prefix": prefix}}, upsert=True)
        await ctx.reply("**Prefix has been changed to:** `{}`".format(prefix))


@client.command()
async def setwelcomechannel(ctx, channel: discord.TextChannel):
    existing_channel = wel.settings.find_one({"name": "welcome_channel"})
    if existing_channel is None:
        # Insert a new document with the channel ID and name "welcome_channel"
        wel.settings.insert_one(
            {"name": "welcome_channel", "channel_id": channel.id})
    else:
        # Update the channel ID
        wel.settings.update_one({"name": "welcome_channel"}, {
                                "$set": {"channel_id": channel.id}})
    await ctx.send(f"The designated channel has been set to {channel.mention}.")


@client.command()
async def setleavechannel(ctx, channel: discord.TextChannel):
    existing_channel = lev.settings.find_one({"name": "leave_channel"})
    if existing_channel is None:
        lev.settings.insert_one(
            {"name": "leave_channel", "channel_id": channel.id})
    else:
        lev.settings.update_one({"name": "leave_channel"}, {
                                "$set": {"channel_id": channel.id}})
    await ctx.send(f"The designated channel has been set to {channel.mention}.")


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
                description="`clear`, `kick`, `ban`, `unban`, `membercount`, `setprefix`, `addrole`, `delrole`, `mute`, `unmute`",
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


@client.command(aliases=['commands'])
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

    await ctx.reply(embed=embed, view=dropdowns)


@client.command(aliases=['p', 'latency'])
@commands.cooldown(1, 15, commands.BucketType.user)
async def ping(ctx):
    l = round(client.latency * 1000, 1)
    embed = discord.Embed(
        title="Pong 🏓", description=f"The bots ping is: `{l}`")
    await ctx.reply(embed=embed)


@client.command(aliases=['code', 'secret', 'pass'])
@commands.cooldown(1, 15, commands.BucketType.user)
async def password(ctx):
    author = ctx.author
    await ctx.reply("Check your DM's‼", delete_after=3)
    await ctx.author.send(f"Your secret password is: `{am}`")


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def fact(ctx):
    await ctx.send(get_fact())


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def topic(ctx):

    await ctx.send(get_topic())


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def showerthought(ctx):
    shower = get_shower()
    thought = shower[0]
    author = shower[1]
    embed = discord.Embed(title=f"{thought}\n  {author}")
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def meme(ctx):
    embed = discord.Embed(title="Meme")

    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/memes/top.json?sort=top&t=week&limit=100') as r:
            res = await r.json()
            embed.set_image(url=res['data']['children']
                            [random.randint(0, 25)]['data']['url'])

            await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    t = ctx.channel.id
    await ctx.channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(
        title="Success ✅", description=f"**Set the slowmode for <#{t}> as** `{seconds}` **seconds**")
    await ctx.reply(embed=embed, delete_after=5)


@client.command(aliases=['members', 'guildcount'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def membercount(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="Membercount of this server",
                          description=f"**This server has** `{guild.member_count}` **members**")

    await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def dog(ctx):
    async with aiohttp.ClientSession() as session:
        request = await session.get('https://some-random-api.ml/img/dog')
        dogjson = await request.json()
    embed = discord.Embed(title="Dog!")
    embed.set_image(url=dogjson['link'])

    await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def cat(ctx):
    async with aiohttp.ClientSession() as session:
        request = await session.get('https://some-random-api.ml/img/cat')
        dogjson = await request.json()
    embed = discord.Embed(title="Cat!")
    embed.set_image(url=dogjson['link'])

    await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def dice(ctx):
    num = [
        '1',
        '2',
        '3',
        '4',
        '5',
        '6']
    embed = discord.Embed(title="Your random number is...",
                          description=f"Your random number is: {random.choice(num)}")
    await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason=None):
    if member == None:
        await ctx.reply("Mention the member to be kicked!", delete_after=3)
    if reason == None:
        reason = "None"
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="Success ✅", description=f"Successfully kicked {member.mention} from **{ctx.guild}**")
    await ctx.reply(embed=embed)


@client.command(aliases=['8b', '8ball'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def eightball(ctx, *, question):
    responses = [
        'Hell no.',
        'Prolly not.',
        'Idk bro.',
        'Prolly.',
        'Hell yeah my dude.',
        'It is certain.',
        'It is decidedly so.',
        'Without a Doubt.',
        'Yes - Definitely.',
        'You may rely on it.',
        'As i see it, Yes.',
        'Most Likely.',
        'Outlook Good.',
        'Yes!',
        'No!',
        'Signs a point to Yes!',
        'Reply Hazy, Try again.',
        'Better not tell you know.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        "Don't Count on it.",
        'My reply is No.',
        'My sources say No.',
        'Outlook not so good.',
        'Very Doubtful']
    eightbembed = discord.Embed(
        title=f"{question}", description=f"{random.choice(responses)}")
    await ctx.reply(embed=eightbembed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author
    ava = member.avatar.url
    e = member.id
    embed = discord.Embed(
        title=f"Avatar of {member.name}#{member.discriminator}")
    embed.set_image(url=ava)
    await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def uptime(ctx):
    delta_uptime = datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(title="**CB42's Uptime**",
                          description=f"`CB42 has been online for -` {days}d, {hours}h, {minutes}m, {seconds}s")

    await ctx.reply(embed=embed)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def invite(ctx):
    invitebt = Button(
        label="Invite CB42",
        url="https://discord.com/api/oauth2/authorize?client_id=1004727274031038574&permissions=8&redirect_uri=https%3A%2F%2Fcb42bot.tk&response_type=code&scope=bot%20connections%20applications.commands"
    )
    view = View()
    view.add_item(invitebt)

    embed = discord.Embed(title="Invite CB42")

    await ctx.reply(embed=embed, view=view)


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if member == None:
        await ctx.reply("Mention the member to be banned!", delete_after=3)
    if reason == None:
        reason = "None"
    await member.ban(reason=reason)
    embed = discord.Embed(
        title="Success ✅", description=f"Successfully banned {member.mention} from **{ctx.guild}**")
    await ctx.reply(embed=embed)


@client.command()
@commands.has_permissions(ban_members=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def unban(ctx, id: int):
    user = await client.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.reply(f'Unbanned {user.mention}')


@client.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, user: discord.Member, *, role: discord.Role):
    await user.add_roles(role)
    await ctx.reply(f"Added {role} to {user.mention}")


@client.command()
@commands.has_permissions(manage_roles=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def removerole(ctx, user: discord.Member, *, role: discord.Role):
    await user.remove_roles(role)
    await ctx.reply(f"Removed {role} from {user.mention}")


@client.command()
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

    await ctx.reply(embed=embed, view=view)


@client.command(aliases=['purge'])
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def clear(ctx, amount=1):
    amount = amount+1
    realamount = amount-1
    if amount > 151:
        await ctx.reply('**Not able to delete so many messages! Please try a number below 150.** ❌', delete_after=5)
    else:
        await ctx.channel.purge(limit=amount)
        await ctx.send(f'**Cleared {realamount} messages!** ✅', delete_after=3)


@client.command(aliases=['level'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def rank(ctx):
    author_id = ctx.author.id
    level = collection.find_one({"_id": author_id})["Level"]
    await ctx.reply(f"**You are level:** `{level}`")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("This command doesn't exist!", delete_after=3)
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(error, delete_after=3)
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You dont have the permission to use this command!", delete_after=3)
    if isinstance("You are missing a required argument", commands.MissingRequiredArgument):
        await ctx.reply(error, delete_after=3)

# SLASH


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


@client.slash_command(name="google", description="Google something...")
@commands.cooldown(1, 5, commands.BucketType.user)
async def google(ctx, *, query: str):
    await ctx.respond(f'Searching for "{query}"...')
    await ctx.defer()
    response = requests.get(f'https://www.google.com/search?q={query}')
    soup = BeautifulSoup(response.content, 'html.parser')
    link = soup.find('a', {'class': 'BNeawe tAd8D AP7Wnd'}).get('href')
    text = soup.find('div', {'class': 'BNeawe iBp4i AP7Wnd'}).text
    embed = discord.Embed(title=query, description=text, color=0x00ff00)
    embed.set_author(name='Google Search', url=link)
    embed.set_footer(text='powered by google')
    await ctx.respond(embed=embed)
    images = soup.find_all('img')
    for i, image in enumerate(images[:5]):
        await ctx.followup.send(image['src'])


@client.slash_command(description="mutes a member")
@commands.has_permissions(kick_members=True)
@option("user", discord.Member, description="Whom you want mute?")
@option("duration", description="How long they should be muted?")
@option("duration_type", description="How long should they be muted?", choices=["Seconds", "Hours", "Days"])
@option("reason", description="Why do you want mute this member?", default=None)
async def mute(ctx, user: discord.Member, duration: int, duration_type: str, reason: str):
    if user.id == ctx.author.id:
        await ctx.respond(embed=discord.Embed(description=f"*You can't timeout yourself*"))
        return
    if reason == None:
        reason = "Not Provided"
    if duration_type == "Hours":
        time = int(duration)*3600
    elif duration_type == "Days":
        time = int(duration)*86400
    elif duration_type == "Seconds":
        time = int(duration)
    responce_check = await timeout_user(ctx, user, reason, time)
    if responce_check == True:
        timeout_embed = discord.Embed(
            description=f"*`{user}` has been timeout by `{ctx.author}`*")
        timeout_embed.set_footer(text=f"Reason: {reason}")
        await ctx.respond(embed=timeout_embed)


@client.slash_command(name='unmute', description="Unmutes the member")
@commands.has_permissions(moderate_members=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def unmute(ctx, member: Option(discord.Member, required=True)):
    await member.remove_timeout()
    await ctx.respond(f"<@{member.id}> has been unmuted by <@{ctx.author.id}>.")


@client.slash_command(aliases=['prefix'])
@commands.has_permissions(manage_guild=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def setprefix(ctx, prefix=None):
    if prefix is None:
        await ctx.respond("Please enter a prefix!", ephemeral=True)
    else:
        coll.update_one({"_id": ctx.guild.id}, {
                        "$set": {"prefix": prefix}}, upsert=True)
        await ctx.respond("Prefix has been changed to: {}".format(prefix))


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


@client.slash_command(name="fact", description="Get a random fact")
@commands.cooldown(1, 5, commands.BucketType.user)
async def fact(ctx):
    await ctx.respond(get_fact(), ephemeral=True)


@client.slash_command(name="topic", description="Get a random topic")
@commands.cooldown(1, 5, commands.BucketType.user)
async def topic(ctx):

    await ctx.respond(get_topic(), ephemeral=True)


@client.slash_command(name="showerthough", description="Get a random showerthought from reddit")
@commands.cooldown(1, 5, commands.BucketType.user)
async def showerthought(ctx):
    shower = get_shower()
    thought = shower[0]
    author = shower[1]
    embed = discord.Embed(title=f"{thought}\n  {author}")
    await ctx.respond(embed=embed, ephemeral=True)


@client.slash_command(name="meme", description="Get a random meme from reddit")
@commands.cooldown(1, 5, commands.BucketType.user)
async def meme(ctx):
    embed = discord.Embed(title="Meme")

    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/memes/top.json?sort=top&t=week&limit=100') as r:
            res = await r.json()
            embed.set_image(url=res['data']['children']
                            [random.randint(0, 25)]['data']['url'])

            await ctx.respond(embed=embed)


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


@client.slash_command(name="dog", description="Get a random dog pic")
@commands.cooldown(1, 5, commands.BucketType.user)
async def dog(ctx):
    async with aiohttp.ClientSession() as session:
        request = await session.get('https://some-random-api.ml/img/dog')
        dogjson = await request.json()
    embed = discord.Embed(title="Dog!")
    embed.set_image(url=dogjson['link'])

    await ctx.respond(embed=embed)


@client.slash_command(name="cat", description="Get a random cat pic")
@commands.cooldown(1, 5, commands.BucketType.user)
async def cat(ctx):
    async with aiohttp.ClientSession() as session:
        request = await session.get('https://some-random-api.ml/img/cat')
        dogjson = await request.json()
    embed = discord.Embed(title="Cat!")
    embed.set_image(url=dogjson['link'])

    await ctx.respond(embed=embed)


@client.slash_command(name="dice", description="Get a random number form 1 to 6")
@commands.cooldown(1, 5, commands.BucketType.user)
async def dice(ctx):
    num = [
        '1',
        '2',
        '3',
        '4',
        '5',
        '6']
    await ctx.respond(f"Your random number is: {random.choice(num)}", ephemeral=True)


async def kick_user(ctx, member, reason):
    await member.kick(reason=reason)
    return True


async def ban_user(ctx, member, reason):
    await member.ban(reason=reason)
    return True


@client.slash_command(name="set-welcome-channel", description="Set the welcome channel")
@commands.has_permissions(kick_members=True)
async def setchannel(ctx, channel: discord.TextChannel):
    existing_channel = wel.settings.find_one({"name": "welcome_channel"})
    if existing_channel is None:
        # Insert a new document with the channel ID and name "welcome_channel"
        wel.settings.insert_one(
            {"name": "welcome_channel", "channel_id": channel.id})
    else:
        # Update the channel ID
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


@client.slash_command(description="Kick a member from the server")
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Option(discord.Member, description="Please select a user to kick", required=True), reason: discord.Option(str, description="Why do you want to kick?", required=False)):
    if user.id == ctx.author.id:
        await ctx.respond(embed=discord.Embed(description=f"*You can't kick yourself*", color=discord.Color.red()))
        return
    kick_embed = discord.Embed(
        description=f"*Please confirm to kick {user}*", color=discord.Color.blurple())
    confirm = Button(label="Confirm", style=discord.ButtonStyle.green)
    cancel = Button(label="Cancel", style=discord.ButtonStyle.red)
    view = View()
    view.add_item(confirm)
    view.add_item(cancel)

    async def button_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(
            label="Confirm", style=discord.ButtonStyle.green, disabled=True)
        button3 = Button(
            label="Cancel", style=discord.ButtonStyle.gray, disabled=True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        responce_get = await kick_user(ctx, user, reason=reason)
        if responce_get == True:
            confirm_kick = discord.Embed(
                description=f"{user} *has beeen kicked by* `{ctx.author}`", color=discord.Color.green())
            await interaction.response.edit_message(embed=confirm_kick, view=view1)
        else:
            pass

    async def button2_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(
            label="Confirm", style=discord.ButtonStyle.gray, disabled=True)
        button3 = Button(
            label="Cancel", style=discord.ButtonStyle.green, disabled=True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        cancel_kick = discord.Embed(
            description=f"Command has stopped.", color=discord.Color.green())
        await interaction.response.edit_message(embed=cancel_kick, view=view1)
    await ctx.respond(embed=kick_embed, view=view)
    confirm.callback = button_callback
    cancel.callback = button2_callback


@client.slash_command(description="Ban a member from the server")
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Option(discord.Member, description="Please select a user to ban", required=True), reason: discord.Option(str, description="Why do you want to ban?", required=False)):
    if user.id == ctx.author.id:
        await ctx.respond(embed=discord.Embed(description=f"*You can't ban yourself*", color=discord.Color.red()))
        return
    ban_embed = discord.Embed(
        description=f"*Please confirm to ban {user}*", color=discord.Color.blurple())
    confirm = Button(label="Confirm", style=discord.ButtonStyle.green)
    cancel = Button(label="Cancel", style=discord.ButtonStyle.red)
    view = View()
    view.add_item(confirm)
    view.add_item(cancel)

    async def button_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(
            label="Confirm", style=discord.ButtonStyle.green, disabled=True)
        button3 = Button(
            label="Cancel", style=discord.ButtonStyle.gray, disabled=True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        responce_get = await ban_user(ctx, user, reason=reason)
        if responce_get == True:
            confirm_ban = discord.Embed(
                description=f"{user} *has beeen banned by* `{ctx.author}`", color=discord.Color.green())
            await interaction.response.edit_message(embed=confirm_ban, view=view1)
        else:
            pass

    async def button2_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(
            label="Confirm", style=discord.ButtonStyle.gray, disabled=True)
        button3 = Button(
            label="Cancel", style=discord.ButtonStyle.green, disabled=True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        cancel_ban = discord.Embed(
            description=f"Command has stopped.", color=discord.Color.green())
        await interaction.response.edit_message(embed=cancel_ban, view=view1)
    await ctx.respond(embed=ban_embed, view=view)
    confirm.callback = button_callback
    cancel.callback = button2_callback


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


@client.slash_command(name="unban", description="Unban a member using their USER-ID")
@commands.has_permissions(ban_members=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def unban(ctx, id: Option(required=True)):
    user = await client.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.respond(f'Unbanned {user.mention}')


@client.slash_command(name="addrole", description="Add a role to a discord member")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, user: discord.Member, *, role: discord.Role):
    await user.add_roles(role)
    await ctx.respond(f"Added {role} to {user.mention}")


@client.slash_command(name="removerole", description="Remove a role from a discord member")
@commands.has_permissions(manage_roles=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def removerole(ctx, user: discord.Member, *, role: discord.Role):
    await user.remove_roles(role)
    await ctx.respond(f"Removed {role} from {user.mention}")


@client.slash_command(name="purge", descripton="Clears the amount of messages specified")
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def purge(ctx, amount: Option(int, required=True)):
    t = ctx.channel.id
    if amount > 101:
        await ctx.respond("Not allowed to clear these many messages, please try a number below 100", ephemeral=True)
    else:
        z = await ctx.channel.purge(limit=amount)
        await ctx.respond(f"**Cleared** `{len(z)}` **messages in** <#{t}>", delete_after=5)


@client.slash_command(name="slowmode", description="Change/set the slowmode of a channel")
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: Option(int, required=True)):
    t = ctx.channel.id
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.respond(f"**Set the slowmode for <#{t}> as** `{seconds}` **seconds** ✅", delete_after=5)


@client.slash_command(name="rank", description="Shows the rank of a user")
@commands.cooldown(1, 5, commands.BucketType.user)
async def rank(ctx):
    guild_id = ctx.guild.id
    author_id = ctx.author.id
    level = collection.find_one(
        {"GuildID": guild_id, "_id": author_id})["Level"]
    xp = collection.find_one({"GuildID": guild_id, "_id": author_id})["XP"]

    if level is None:
        await ctx.respond("You did not level in this server yet!")

    # Get the user's avatasr
    ava = ctx.author.avatar.url
    response = requests.get(ava)
    imge = Image.open(BytesIO(response.content))
    imge = imge.resize((100, 100))

    # Create an image
    img = Image.new("RGB", (400, 200), color=(73, 80, 87))
    img.paste(imge, (100, 10))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 36)
    draw.text((10, 10), f"Level: {level}", font=font, fill=(255, 255, 255))
    draw.text((10, 130), "XP", font=font, fill=(255, 255, 255))
    # Add a bar to show the XP progress
    draw.rectangle([(10, 170), (10 + xp * 0.3, 190)], fill=(247, 134, 28))

    # Save the image to a file
    img.save("rank.png")
    # Send the image in the Discord channel
    with open("rank.png", "rb") as f:
        await ctx.respond(file=discord.File(f))


@client.slash_command(name="eightball", description="Ask some questions!")
@commands.cooldown(1, 5, commands.BucketType.user)
async def eightball(ctx, *, question):
    responses = [
        'Hell no.',
        'Prolly not.',
        'Idk bro.',
        'Prolly.',
        'Hell yeah my dude.',
        'It is certain.',
        'It is decidedly so.',
        'Without a Doubt.',
        'Yes - Definitely.',
        'You may rely on it.',
        'As i see it, Yes.',
        'Most Likely.',
        'Outlook Good.',
        'Yes!',
        'No!',
        'Signs a point to Yes!',
        'Reply Hazy, Try again.',
        'Better not tell you know.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        "Don't Count on it.",
        'My reply is No.',
        'My sources say No.',
        'Outlook not so good.',
        'Very Doubtful']
    eightbembed = discord.Embed(
        title=f"{question}", description=f"{random.choice(responses)}")
    await ctx.respond(embed=eightbembed)


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
        prefix = coll.find_one({"_id": message.guild.id})['prefix']
        embed = discord.Embed(
            title="CB42", description=f"Type `{prefix}`help for more info")
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
    answer = check_message(message)
    if answer[0] == "del":
        await message.delete()
        await message.channel.send(answer[1], delete_after=3)

    message.content = message.content.lower()
    await client.process_commands(message)
    await scam_check(message)
try:
    client.loop.create_task(status())
    client.run(token_)
except:
    print("Make sure the token is correct!")
