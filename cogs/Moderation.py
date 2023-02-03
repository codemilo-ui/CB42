import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import *
from defs import *


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Option(discord.Member, description="Please select a user to kick", required=True), reason: discord.Option(str, description="Why do you want to kick?", required=False)):
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

    @slash_command(description="Bans a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Option(discord.Member, description="Please select a user to ban", required=True), reason: discord.Option(str, description="Why do you want to kick?", required=False)):
        if user.id == ctx.author.id:
            await ctx.respond(embed=discord.Embed(description=f"*You can't ban yourself*", color=discord.Color.red()))
            return
        kick_embed = discord.Embed(
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
                confirm_kick = discord.Embed(
                    description=f"{user} *has beeen banned by* `{ctx.author}`", color=discord.Color.green())
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


def setup(client):
    client.add_cog(Moderation(client))
