"""Moderation commands."""
import discord
import config
from discord.ext import commands
import threading


def setup(bot):
    """Set up the cog."""
    bot.add_cog(Moderation(bot))


class Moderation:
    """Commands for moderation."""

    def __init__(self, bot):
        """Initizises Moderation cog."""
        self.bot = bot

    @staticmethod
    async def on_ready():
        """Print when the cog is ready."""
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
    def check_channel_exists(ctx, channel=None):
        """Check if a specifed channel exists."""
        guild = ctx.guild
        channels = guild.text_channels
        log_channel = discord.utils.get(channels, name=channel)
        return log_channel

    @commands.command()
    async def clear(self, ctx, amount=100):
        """Clear the specified amount of messages."""
        channel = ctx.message.channel
        author = ctx.author
        messages = []

        if author.permissions_in(channel).manage_messages:
            async for message in channel.history(limit=int(amount)):
                messages.append(message)
            await channel.delete_messages(messages)
        else:
            await ctx.send("{author.name}, you do not have the "
                           "permission to delete messages!")

    @commands.command()
    async def kick(self, ctx, user: discord.Member, reason="None Specified"):
        """Kicks the specified user."""
        author = ctx.author

        if author.guild_permissions.kick_members and author.is_superset(user):
            await user.kick(reason=reason)
            embed = await self.mod_log("Kick", user.name, reason, author.name)
            log_channel = await self.check_channel_exists(ctx, config.log_channel)
            if log_channel is None:
                await ctx.send("Mod logging channel does not exist! Either create "
                               "a channel named 'mod-log' "
                               "or change the config file.")
            else:
                await log_channel.send(embed=embed)
        else:
            await ctx.send("{author.name}, you do not have the "
                           "permission to kick that user!")

    @commands.command()
    async def ban(self, ctx, user: discord.Member, reason="None Specified", tempban=False):
        """Bans the specified user."""
        author = ctx.author

        if tempban:
            log_type = "Tempban"
        else:
            log_type = "Ban"

        if author.guild_permissions.ban_members and author.is_superset(user):
            await user.ban(reason=reason)
            embed = await self.mod_log(log_type, user.name, reason, author.name)
            log_channel = await self.check_channel_exists(ctx, config.log_channel)
            if tempban:
                if log_channel is None:
                    await ctx.send("Mod logging channel does not exist! Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)
        else:
            await ctx.send("{author.name}, you do not have the "
                           "permission to ban that user!")

    @commands.command()
    async def tempban(self, ctx, user: discord.Member, seconds, reason):
        """Temporarily bans a specfic user."""
        ctx.invoke(self.ban, user, reason, tempban=True)
        unban_timer = threading.Timer(int(seconds),
                                      ctx.invoke(self.unban, user, reason, tempban=True))
        unban_timer.start()

    @commands.command()
    async def unban(self, ctx, user: discord.Member, reason="None Specified", tempban=False):
        """Unbans the specified user."""
        author = ctx.author
        guild = ctx.guild
        if author.guild_permissions.ban_members:
            await guild.unban(user, reason=reason)
            if not tempban:
                embed = await self.mod_log("Unban", user.name, reason, author.name)
                log_channel = await self.check_channel_exists(ctx, config.log_channel)
                if log_channel is None:
                    await ctx.send("Mod logging channel does not exist! Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)
        else:
            await ctx.send("{author.name}, you do not have the "
                           "permission to unban users!")

    @commands.command()
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
        """Give the specified user a role."""
        author = ctx.author

        if author.guild_permissions.manage_roles and author.top_role >= role:
            await user.add_roles(role)
        else:
            await ctx.send("{author.name}, you don't have the permission"
                           "to give that role to users!")

    @commands.command()
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
        """Remove a role from the specified user."""
        author = ctx.author

        if author.guild_permissions.manage_roles and author.is_superset(user):
            await user.remove_roles(role)
        else:
            await ctx.send("%s, you don't have the permission "
                           "to remove roles from users!" % author.name)

    @commands.command()
    async def mute(self, ctx, user: discord.Member, reason="None Specified"):
        """Mute the specified user."""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")

        if muted is None:
            await guild.create_role(name="Muted")
            muted = discord.utils.get(guild.roles, name="Muted")
        if author.guild_permissions.manage_roles and author.is_superset(user):
            if "Muted" in user.roles:
                await user.add_roles(muted, reason=reason)
                embed = await self.mod_log("Mute", user.name,
                                           reason, author.name)
                log_channel = await self.check_channel_exists(ctx, config.log_channel)
                if log_channel is None:
                    await ctx.send("Mod logging channel does not exist! Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)
            else:
                await ctx.send("%s is already muted!", user.name)
        else:
            await ctx.send("%s, you don't have the "
                           "permission to mute users!" % author.name)

    @commands.command()
    async def unmute(self, ctx, user: discord.Member, reason="None Specified"):
        """Unmute the specified user."""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")

        if author.guild_permissions.manage_roles:
            if "Muted" in user.roles:
                await user.remove_roles(muted, reason=reason)
                embed = await self.mod_log(
                    "Unmute", user.name, reason, author.name)
                log_channel = await self.check_channel_exists(ctx, config.log_channel)
                if log_channel is None:
                    await ctx.send("Mod logging channel does not exist! Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)
            else:
                await ctx.send("%s is not muted!", user.name)
        else:
            await ctx.send("%s, you do not have the permission "
                           "to mute other users!" % author.name)
