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
    async def mod_log(
            id, time, log_type, user, reason, moderator, duration=None):
        """Mod logging."""
        embed = discord.Embed(title=f'{log_type} for user {user.id}',
                              colour=discord.Colour(0xf8e71c),
                              timestamp=time)
        embed.set_author(name=moderator.name, url="https://discordapp.com",
                         icon_url=moderator.avatar_url)

        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Moderator", value=moderator.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        if duration:
            embed.add_field(name="Duration:", value=duration, inline=True)
        embed.set_footer(text=f'ID: {id}')
        return embed

    def log_channel_exists():
        """Check if a specifed channel exists."""
        def predicate(ctx):
            guild = ctx.guild
            channels = guild.text_channels
            log_channel = discord.utils.get(channels, name=config.log_channel)
            return log_channel
        return commands.check(predicate)

    @staticmethod
    @commands.Cog.listener()
    async def on_member_join(member):
        """Auto role."""
        if config.welcome_channel:
            channel = discord.utils.find(
                lambda m: m.name == config.welcome_channel,
                member.guild.channels)
            await channel.send(f"Welcome {member.mention}!")
        if config.autorole:
            default_role = discord.utils.find(
                lambda m: m.name == config.autorole, member.guild.roles)
            await member.add_roles(default_role)

    @commands.command(name="clear", aliases=["c"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @log_channel_exists()
    async def clear(self, ctx, amount=1):
        """Clear the specified amount of messages.
 Args: <amount> <optional:user>"""
        channel = ctx.message.channel
        messages = []
        async for message in channel.history(limit=int(amount)):
            messages.append(message)
        await channel.delete_messages(messages)

    @commands.command(name="kick", aliases=["k"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @log_channel_exists()
    async def kick(self, ctx, user: discord.Member, *words):
        """Kicks the specified user. Args: m!kick <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        channels = guild.text_channels
        reason = "None specified"
        if not author.top_role > user.top_role:
            raise commands.MissingPermissions("Is superset")
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        await user.kick(reason=reason)
        embed = await self.mod_log(
                ctx.message.id, ctx.message.created_at,
                "Kick", user, reason, author)
        log_channel = discord.utils.get(channels, name=config.log_channel)
        await log_channel.send(embed=embed)

    @commands.command(name="ban", aliases=["b"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @log_channel_exists()
    async def ban(self, ctx, user: discord.Member,
                  *words, temp=False, duration=None):
        """Bans the specified user. Args: <user> <reason>"""
        author = ctx.author
        reason = "None specified"
        channels = ctx.guild.text_channels
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        if not author.top_role > user.top_role:
            raise commands.MissingPermissions("Is superset")
        await user.ban(reason=reason)
        if temp:
            embed = await self.mod_log(
                        ctx.message.id, ctx.message.created_at,
                        "Temp ban", user, reason, author)
        else:
            embed = await self.mod_log(
                        ctx.message.id, ctx.message.created_at,
                        "Ban", user, reason, author, duration=duration)
        log_channel = discord.utils.get(channels, name=config.log_channel)
        if log_channel is None:
            await ctx.send(":no_entry_sign: Mod logging channel "
                           "does not exist! "
                           "Either create "
                           "a channel named 'mod-log' "
                           "or change the config file.")
        else:
            await log_channel.send(embed=embed)

    @commands.command(name="tempban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @log_channel_exists()
    async def tempban(self, ctx, user: discord.Member, seconds, *words):
        reason = "None specified"
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        """Tempbans a specfic user. Args: <user> <seconds> <reason>"""
        await ctx.invoke(self.ban, user, reason, temp=True, duration=seconds)
        unban_timer = threading.Timer(float(seconds),
                                      await ctx.invoke(
                                      self.unban, user, reason, temp=True))
        unban_timer.start()

    @commands.command(name="unban", aliases=["pardon"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @log_channel_exists()
    async def unban(self, ctx, user: discord.User,
                    *words, temp=False):
        """Unbans the specified user. Args: <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        reason = "None specified"
        channels = guild.text_channels
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        banned = await guild.fetch_ban(user)
        if banned:
            await guild.unban(user, reason=reason)
            if not temp:
                embed = await self.mod_log(
                            ctx.message.id, ctx.message.created_at,
                            "Unban", user, reason, author)
                log_channel = discord.utils.get(
                    channels, name=config.log_channel)
                if log_channel is None:
                    await ctx.send(":no_entry_sign: Mod logging channel "
                                   "does not exist! "
                                   "Either create "
                                   "a channel named 'mod-log' "
                                   "or change the config file.")
                else:
                    await log_channel.send(embed=embed)

    @commands.command(name="addrole")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @log_channel_exists()
    async def addrole(self, ctx, user: discord.Member, role: discord.Role,
                      *words):
        """Give the specified user a role. Args: <user> <role>"""
        author = ctx.author
        reason = "None specified"
        channels = ctx.guild.text_channels
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        if not author.top_role > role:
            raise commands.MissingPermissions("Is superset")
        await user.add_roles(role)
        embed = await self.mod_log(
                ctx.message.id, ctx.message.created_at,
                "Add role", user, reason, author)
        log_channel = discord.utils.get(channels, name=config.log_channel)
        if log_channel is None:
            await ctx.send(":no_entry_sign: Mod logging "
                           "channel does not exist! "
                           "Either create "
                           "a channel named 'mod-log' "
                           "or change the config file.")
        else:
            await log_channel.send(embed=embed)

    @commands.command(name="removerole")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @log_channel_exists()
    async def removerole(self, ctx, user: discord.Member, role: discord.Role,
                         *words):
        """Remove a role from the specified user. Args: <user> <role>"""
        author = ctx.author
        reason = "None specified"
        channels = ctx.guild.text_channels
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        if not author.top_role > role:
            raise commands.MissingPermissions("Is superset")
        await user.remove_roles(role)
        embed = await self.mod_log(
                ctx.message.id, ctx.message.created_at,
                "Remove role", user, reason, author)
        log_channel = discord.utils.get(channels, name=config.log_channel)
        if log_channel is None:
            await ctx.send(":no_entry_sign: Mod logging "
                           "channel does not exist! "
                           "Either create "
                           "a channel named 'mod-log' "
                           "or change the config file.")
        else:
            await log_channel.send(embed=embed)

    @commands.command(name=["mute"], aliases=["m"])
    @commands.guild_only()
    @log_channel_exists()
    async def mute(self, ctx, user: discord.Member,
                   *words, temp=False, duration=None):
        """Mute the specified user. Args: <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        channels = ctx.guild.text_channels
        muted = discord.utils.get(guild.roles, name="Muted")
        log_channel = discord.utils.get(channels, name=config.log_channel)
        reason = "None specified"
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        if muted is None:
            await guild.create_role(name='Muted')

        if author.top_role > user.top_role:
            if muted in user.roles:
                await ctx.send(f":no_entry_sign: {user.mention} "
                               "is already muted!")
            elif log_channel:
                await user.add_roles(muted, reason=reason)
                if temp:
                    embed = await self.mod_log(
                            ctx.message.id, ctx.message.created_at,
                            "Temp mute", user, reason,
                            author, duration=duration)
                else:
                    embed = await self.mod_log(
                            ctx.message.id, ctx.message.created_at,
                            "Mute", user, reason, author)
                    await log_channel.send(embed=embed)
            else:
                await ctx.send(":no_entry_sign: Mod logging "
                               "channel does not exist! "
                               "Either create "
                               "a channel named 'mod-log' "
                               "or change the config file.")
        else:
            raise commands.MissingPermissions("Is superset")

    @commands.command(name="tempmute")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @log_channel_exists()
    async def tempmute(self, ctx, user: discord.Member, seconds, *words):
        """Tempbans a specfic user. Args: <user> <seconds> <reason>"""
        reason = "None specified"
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        await ctx.invoke(self.mute, user, reason, temp=True, duration=seconds)
        unmute_timer = threading.Timer(
            15.0, await ctx.invoke(self.unmute, user, temp=True))
        unmute_timer.start()

    @commands.command(name="unmute")
    @commands.guild_only()
    @log_channel_exists()
    async def unmute(self, ctx, user: discord.Member,
                     *words, temp=False):
        """Unmute the specified user. Args: <user> <reason>"""
        author = ctx.author
        guild = ctx.guild
        channels = guild.text_channels
        muted = discord.utils.get(guild.roles, name="Muted")
        log_channel = discord.utils.get(channels, name=config.log_channel)
        reason = "None specified"
        if words:
            reason = ""
            for w in words:
                reason = reason + " " + w
        if author.top_role > user.top_role:
            if muted in user.roles:
                await user.remove_roles(muted, reason=reason)
                if not temp:
                    embed = await self.mod_log(
                            ctx.message.id, ctx.message.created_at,
                            "Unmute", user, reason, author)
                    if log_channel is None:
                        await ctx.send(":no_entry_sign: Mod logging "
                                       "channel does not exist! "
                                       "Either create "
                                       "a channel named 'mod-log' "
                                       "or change the config file.")
                    else:
                        await log_channel.send(embed=embed)
            else:
                await ctx.send(f":no_entry_sign: {user.mention} "
                               "is not muted!")
        else:
            raise commands.MissingPermissions("Is superset")
