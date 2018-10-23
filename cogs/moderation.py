"""Moderation commands."""
import discord
from discord.ext import commands

class Moderation:
    """Commands for moderation."""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_ready():
        """Prints when the cog is ready."""
        print("Moderation is ready!")

    @staticmethod
    async def mod_log(log_type, user, reason, moderator):
        """Mod logging."""
        embed = discord.Embed()
        embed.add_field(name="Type:", value=log_type, inline=True)
        embed.add_field(name="User:", value=user, inline=True)
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.set_footer(text=moderator)
        return embed

    @staticmethod
    async def check_mod_log_exists(ctx):
        """Checks if a mod_log channel exists."""
        guild = ctx.guild
        channels = guild.text_channels
        if 'mod_log' not in channels:
            overwrites = {
                guild.me: discord.PermissionOverwrite(send_messages=True),
                guild.default_role: discord.PermissionOverwrite(send_messages=True)
            }
            log_channel = await guild.create_text_channel("mod_log", overwrites=overwrites)
            return log_channel
        log_channel = discord.utils.get(channels, name="mod_log")
        return log_channel

    @commands.command()
    async def clear(self, ctx, amount=100):
        """Clears the specified amount of messages."""
        channel = ctx.message.channel
        author = ctx.author
        messages = []
        if author.permissions_in(channel).manage_messages:
            async for message in channel.history(limit=int(amount)):
                messages.append(message)
            await channel.delete_messages(messages)
        else:
            await ctx.send("{author.name}, you do not have the permission to delete messages!")

    @commands.command()
    async def kick(self, ctx, user: discord.Member, reason):
        """Kicks the specified user."""
        author = ctx.author
        if author.guild_permissions.kick_members and author.is_superset(user):
            await user.kick(reason=reason)
            embed = await self.mod_log("Kick", user.name, reason, author.name)
            log_channel = await self.check_mod_log_exists(ctx)
            await log_channel.send(embed=embed)
        else:
            await ctx.send("{author.name}, you do not have the permission to kick that user!")

    @commands.command()
    async def ban(self, ctx, user: discord.Member, reason):
        """Bans the specified user."""
        author = ctx.author
        if author.guild_permissions.ban_members and author.is_superset(user):
            await user.ban(reason=reason)
            embed = await self.mod_log("Ban", user.name, reason, author.name)
            log_channel = await self.check_mod_log_exists(ctx)
            await log_channel.send(embed=embed)
        else:
            await ctx.send("{author.name}, you do not have the permission to ban that user!")

    @commands.command()
    async def unban(self, ctx, user: discord.Member, reason):
        """Unbans the specified user."""
        author = ctx.author
        guild = ctx.guild
        if author.guild_permissions.ban_members:
            await guild.unban(user, reason=reason)
            embed = await self.mod_log("Unban", user.name, reason, author.name)
            log_channel = await self.check_mod_log_exists(ctx)
            await log_channel.send(embed=embed)
        else:
            await ctx.send("{author.name}, you do not have the permission to unban users!")

    @commands.command()
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
        """Gives the specified user a role."""
        author = ctx.author
        if author.guild_permissions.manage_roles and author.top_role >= role:
            await user.add_roles(role)
        else:
            await ctx.send("{author.name}, you don't have the permission\
            to give that role to users!")

    @commands.command()
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
        """Removes a role from the specified user."""
        author = ctx.author
        if author.guild_permissions.manage_roles and author.is_superset(user):
            await user.remove_roles(role)
        else:
            await ctx.send("%s, you don't have the permission\
            to remove roles from users!" % author.name)

    @commands.command()
    async def mute(self, ctx, user: discord.Member, reason):
        """Mutes the specified user."""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")
        if muted is None:
            await guild.create_role(name="Muted")
            muted = discord.utils.get(guild.roles, name="Muted")
        if author.guild_permissions.manage_roles and author.is_superset(user):
            if "Muted" in user.roles:
                await user.add_roles(muted, reason=reason)
                embed = await self.mod_log("Mute", user.name, reason, author.name)
                log_channel = await self.check_mod_log_exists(ctx)
                await log_channel.send(embed=embed)
            else:
                await ctx.send("%s is already muted!", user.name)
        else:
            await ctx.send("%s, you don't have the permission to mute users!" % author.name)

    @commands.command()
    async def unmute(self, ctx, user: discord.Member, reason):
        """Unmutes the specified user."""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")
        if author.guild_permissions.manage_roles:
            if "Muted" in user.roles:
                await user.remove_roles(muted, reason=reason)
                embed = await self.mod_log("Unmute", user.name, reason, author.name)
                log_channel = await self.check_mod_log_exists(ctx)
                await log_channel.send(embed=embed)
            else:
                await ctx.send("%s is not muted!", user.name)
        else:
            await ctx.send("%s, you do not have the permission to mute other users!" % author.name)

def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Moderation(bot))
