"""Moderation commands."""
import discord
import config
from discord.ext import commands
import threading


def setup(bot):
    """Set up the cog."""
    bot.add_cog(Moderation(bot))


class Moderation(commands.Cog):
    """Commands for moderation."""

    def __init__(self, bot):
        """Initizises Moderation cog."""
        self.bot = bot

    @staticmethod
    async def on_ready():
        """Print when the cog is ready."""
        print("Moderation is ready!")

    @staticmethod
    async def mod_log(log_type, user, reason, moderator, duration=None):
        """Mod logging."""
        embed = discord.Embed()
        embed.add_field(name="Type:", value=log_type, inline=True)
        embed.add_field(name="User:", value=user, inline=True)
        embed.add_field(name="Reason:", value=reason, inline=False)
        if duration:
            embed.add_field(name="Duration:", value=duration, inline=False)
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
        """Clear the specified amount of messages. Args: <amount>"""
        channel = ctx.message.channel
        author = ctx.author
        messages = []
        try:
            if author.permissions_in(channel).manage_messages:
                async for message in channel.history(limit=int(amount)):
                    messages.append(message)
                await channel.delete_messages(messages)
            else:
                await ctx.send(":no_entry_sign: {}, you don't "
                               "have the permission "
                               "to delete messages!".format(author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to delete messages!")

    @commands.command()
    async def kick(self, ctx, user: discord.Member, reason="None Specified"):
        """Kicks the specified user. Args: m!kick <user> <reason>"""
        author = ctx.author
        try:
            if author.guild_permissions.kick_members and \
                    author.guild_permissions.is_strict_superset(
                    user.guild_permissions):
                await user.kick(reason=reason)
                embed = await self.mod_log("Kick", user.name,
                                           reason, author.name)
                log_channel = self.check_channel_exists(
                    ctx, config.log_channel)
                if log_channel is None:
                    await ctx.send(":no_entry_sign: Mod logging channel "
                                   "does not exist! "
                                   "Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)
            else:
                await ctx.send("{}, you do not have the "
                               "permission to kick that member!".format(
                                    author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to kick members!")

    @commands.command()
    async def ban(self, ctx, user: discord.Member,
                  reason="None Specified", temp=False, duration=None):
        """Bans the specified user. Args: <user> <reason>"""
        author = ctx.author

        if temp:
            log_type = "Temp ban"
        else:
            log_type = "Ban"
        try:
            if author.guild_permissions.ban_members and \
                    author.guild_permissions.is_strict_superset(
                    user.guild_permissions):
                await user.ban(reason=reason)
                if temp:
                    embed = await self.mod_log(
                        log_type, user.name, reason, author.name)
                else:
                    embed = await self.mod_log(log_type, user.name, reason,
                                               author.name, duration=duration)
                log_channel = self.check_channel_exists(
                    ctx, config.log_channel)
                if log_channel is None:
                    await ctx.send(":no_entry_sign: Mod logging channel "
                                   "does not exist! "
                                   "Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)
            else:
                await ctx.send("{}, you do not have the "
                               "permission to ban that member!".format(
                                    author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to ban members!")

    @commands.command()
    async def tempban(self, ctx, user: discord.Member, seconds, reason):
        """Tempbans a specfic user. Args: <user> <seconds> <reason>"""
        await ctx.invoke(self.ban, user, reason, temp=True, duration=seconds)
        unban_timer = threading.Timer(float(seconds),
                                      await ctx.invoke(
                                      self.unban, user, reason, temp=True))
        unban_timer.start()

    @commands.command()
    async def unban(self, ctx, user: discord.User,
                    reason="None Specified", temp=False):
        """Unbans the specified user. Args: <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        try:
            banned = await guild.fetch_ban(user)
            if author.guild_permissions.ban_members:
                if banned:
                    await guild.unban(user, reason=reason)
                    if not temp:
                        embed = await self.mod_log(
                            "Unban", user.name, reason, author.name)
                        log_channel = self.check_channel_exists(
                            ctx, config.log_channel)
                        if log_channel is None:
                            await ctx.send(":no_entry_sign: Mod logging "
                                           "channel does not exist! "
                                           "Either create "
                                           "a channel named 'mod-log' "
                                           "or change the config file.")
                        else:
                            await log_channel.send(embed=embed)
            else:
                await ctx.send(":no_entry_sign: {}, you do not have the "
                               "permission to unban users!".format(
                                author.name))
        except discord.NotFound:
            await ctx.send(':no_entry_sign: User does not exist or '
                           'is not banned.')
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to ban members!")

    @commands.command()
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
        """Give the specified user a role. Args: <user> <role>"""
        author = ctx.author
        try:
            if author.guild_permissions.manage_roles and \
                    author.top_role >= role:
                await user.add_roles(role)
            else:
                await ctx.send(":no_entry_sign: {}, "
                               "you don't have the permission"
                               "to give that role to members!".format(
                                    author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to manage roles!")

    @commands.command()
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
        """Remove a role from the specified user. Args: <user> <role>"""
        author = ctx.author
        try:
            if author.guild_permissions.manage_roles and \
                    author.guild_permissions.is_strict_superset(
                    user.guild_permissions):
                await user.remove_roles(role)
            else:
                await ctx.send(":no_entry_sign: {}, "
                               "you don't have the permission"
                               "to remove roles to members!".format(
                                    author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to manage roles!")

    @commands.command()
    async def mute(self, ctx, user: discord.Member,
                   reason="None Specified", temp=False, duration=None):
        """Mute the specified user. Args: <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")
        log_channel = self.check_channel_exists(
            ctx, config.log_channel)
        try:
            if muted is None:
                await guild.create_role(name='Muted')

            if author.guild_permissions.is_strict_superset(
                    user.guild_permissions):
                if muted in user.roles:
                    await ctx.send(":no_entry_sign: {} "
                                   "is already muted!".format(user.name))
                elif log_channel:
                    await user.add_roles(muted, reason=reason)
                    if temp:
                        embed = await self.mod_log("Temp mute", user.name,
                                                   reason, author.name,
                                                   duration=duration)
                    else:
                        embed = await self.mod_log("Mute", user.name,
                                                   reason, author.name)
                    await log_channel.send(embed=embed)
                else:
                    await ctx.send(":no_entry_sign: Mod logging channel "
                                   "does not exist! "
                                   "Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
            else:
                await ctx.send("{}, you don't have the "
                               "permission to mute members!".format(
                                    author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to manage roles!")

    @commands.command()
    async def tempmute(self, ctx, user: discord.Member, seconds, reason):
        """Tempbans a specfic user. Args: <user> <seconds> <reason>"""
        await ctx.invoke(self.mute, user, reason, temp=True, duration=seconds)
        unmute_timer = threading.Timer(
            15.0, await ctx.invoke(self.unmute, user, temp=True))
        unmute_timer.start()

    @commands.command()
    async def unmute(self, ctx, user: discord.Member,
                     reason="None Specified", temp=False):
        """Unmute the specified user. Args: <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")
        log_channel = self.check_channel_exists(
            ctx, config.log_channel)
        try:
            if author.guild_permissions.is_strict_superset(
                        user.guild_permissions):
                if muted in user.roles:
                    await user.remove_roles(muted, reason=reason)
                    if not temp:
                        embed = await self.mod_log(
                            "Unmute", user.name, reason, author.name)
                        if log_channel is None:
                            await ctx.send(":no_entry_sign: Mod logging "
                                           "channel does not exist! "
                                           "Either create "
                                           "a channel named 'mod-log' "
                                           "or change the config file.")
                        else:
                            await log_channel.send(embed=embed)
                else:
                    await ctx.send(":no_entry_sign: {} "
                                   "is not muted!".format(user.name))
            else:
                await ctx.send(":no_entry_sign: {}, you do not have the "
                               "permission to mute other members!".format(
                                    author.name))
        except discord.Forbidden:
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to manage roles!")
