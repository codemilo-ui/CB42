import random
import aiohttp
import discord
from discord.ext import commands
from discord.commands import slash_command
from defs import *


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(name="dog", description="Get a random dog pic")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://some-random-api.ml/img/dog')
            dogjson = await request.json()
        embed = discord.Embed(title="Dog!")
        embed.set_image(url=dogjson['link'])

        await ctx.respond(embed=embed)

    @slash_command(name="cat", description="Get a random cat pic")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://some-random-api.ml/img/cat')
            dogjson = await request.json()
        embed = discord.Embed(title="Cat!")
        embed.set_image(url=dogjson['link'])

        await ctx.respond(embed=embed)

    @slash_command(name="dice", description="Get a random number form 1 to 6")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx):
        num = [
            '1',
            '2',
            '3',
            '4',
            '5',
            '6']
        await ctx.respond(f"Your random number is: {random.choice(num)}")

    @slash_command(name="eightball", description="Ask some questions!", aliases=["8ball"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def eightball(self, ctx, *, question: str):
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

    @slash_command(name="meme", description="Get a random meme from reddit")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        embed = discord.Embed(title="Meme")

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/memes/top.json?sort=top&t=week&limit=100') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children']
                                [random.randint(0, 25)]['data']['url'])

                await ctx.respond(embed=embed)

    @slash_command(name="fact", description="Get a random fact")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def fact(self, ctx):
        await ctx.respond(get_fact())

    @slash_command(name="topic", description="Get a random topic")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def topic(self, ctx):
        await ctx.respond(get_topic())

    @slash_command(name="showerthough", description="Get a random showerthought from reddit", aliases=["showerthought", "st"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def showerthought(self, ctx):
        shower = get_shower()
        thought = shower[0]
        author = shower[1]
        embed = discord.Embed(title=f"{thought}\n  {author}")
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Fun(client))
