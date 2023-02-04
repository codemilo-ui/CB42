import os
from io import BytesIO

import certifi
import discord
import pymongo
import operator
import requests
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient

mango_url = os.environ['MONGO']
e = certifi.where()
cluster = MongoClient(mango_url, tlsCAFile=e)
db = cluster["cb42"]
collection = db["level"]


class Rank(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(name="rank", description="Shows the rank of a user")
    @cooldown(1, 5, commands.BucketType.user)
    async def rank(self, ctx):
        author_id = ctx.author.id
        level = collection.find_one(
            {"_id": author_id})["Level"]
        xp = collection.find_one({"_id": author_id})["XP"]

        if author_id is None:
            await ctx.send("You did not level in this server yet!")

        ava = ctx.author.avatar.url
        response = requests.get(ava)
        imge = Image.open(BytesIO(response.content))
        imge = imge.resize((100, 100))
        img = Image.new("RGB", (400, 200), color=(73, 80, 87))
        img.paste(imge, (290, 10))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./assets/arial.ttf", 36)
        draw.text((10, 10), f"Level: {level}", font=font, fill=(255, 255, 255))
        draw.text((10, 130), "XP", font=font, fill=(255, 255, 255))
        draw.rectangle([(10, 170), (10 + xp * 0.3, 190)], fill=(247, 134, 28))

        img.save("rank.png")
        with open("rank.png", "rb") as f:
            await ctx.respond(file=discord.File(f))

    @slash_command(name="leaderboard", description="Shows the XP leaderboard of all users who use the bot")
    @cooldown(1, 5, commands.BucketType.user)
    async def leaderboard(self, ctx):
        levels = collection.find()
        leaderboard = {}
        for level in levels:
            leaderboard[level["_id"]] = level["XP"]
        sorted_leaderboard = sorted(leaderboard.items(), key=operator.itemgetter(1), reverse=True)
        embed = discord.Embed(title="XP Leaderboard", description="Top 10 users with the highest XP")
        for i in range(10):
            user = self.client.get_user(sorted_leaderboard[i][0])
            embed.add_field(name=f"{i + 1}. {user.name}", value=sorted_leaderboard[i][1], inline=False)
        await ctx.respond(embed=embed)

def setup(client):
    client.add_cog(Rank(client))
