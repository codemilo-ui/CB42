import discord
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from discord.ui import *
from defs import *


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='mute', description="mutes a member")
    @commands.has_permissions(kick_members=True)
    @option("user", discord.Member, description="Whom you want mute?")
    @option("duration", description="How long they should be muted?")
    @option("duration_type", description="How long should they be muted?", choices=["Seconds", "Hours", "Days"])
    @option("reason", description="Why do you want mute this member?", default=None)
    async def mute_command(self, ctx, user: discord.Member, duration: int, duration_type: str, reason: str):
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

    @commands.command(name="purge", descripton="Clears the amount of messages specified")
    @has_permissions(manage_messages=True)
    @cooldown(1, 5, BucketType.user)
    async def purge(self, ctx, amount: Option(int, required=True)):
        t = ctx.channel.id
        if amount > 101:
            await ctx.respond("Not allowed to clear these many messages, please try a number below 100", ephemeral=True)
        else:
            z = await ctx.channel.purge(limit=amount)
            await ctx.respond(f"**Cleared** `{len(z)}` **messages in** <#{t}>", delete_after=5)

    @commands.command(name="slowmode", description="Change/set the slowmode of a channel")
    @cooldown(1, 5, BucketType.user)
    @has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: Option(int, required=True)):
        t = ctx.channel.id
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.respond(f"**Set the slowmode for <#{t}> as** `{seconds}` **seconds** ✅", delete_after=5)

    @commands.command(name="removerole", description="Remove a role from a discord member")
    @has_permissions(manage_roles=True)
    @cooldown(1, 5, BucketType.user)
    async def removerole(self, ctx, user: discord.Member, *, role: discord.Role):
        await user.remove_roles(role)
        await ctx.respond(f"Removed {role} from {user.mention}")

    @commands.command(name="unban", description="Unban a member using their USER-ID")
    @has_permissions(ban_members=True)
    @cooldown(1, 5, BucketType.user)
    async def unban(self, ctx, id: Option(required=True)):
        user = await self.client.fetch_user(id)
        await ctx.guild.unban(user)
        await ctx.respond(f'Unbanned {user.mention}')

    @commands.command(name="addrole", description="Add a role to a discord member")
    @has_permissions(manage_roles=True)
    async def addrole(self, ctx, user: discord.Member, *, role: discord.Role):
        await user.add_roles(role)
        await ctx.respond(f"Added {role} to {user.mention}")

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
