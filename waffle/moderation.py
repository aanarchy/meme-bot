"""Moderation commands."""
import discord
from discord.ext import commands
import humanize

import waffle.config
import waffle.scheduler

CONFIG = waffle.config.CONFIG["config"]


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
    async def mod_log(ctx, log_type, user, reason, duration=None):
        """Mod logging."""
        moderator = ctx.author
        embed = discord.Embed(
            title=f"{log_type} for user {user.id}",
            colour=discord.Colour(0xF8E71C),
            timestamp=ctx.message.created_at,
        )
        embed.set_author(
            name=moderator.name,
            url="https://discordapp.com",
            icon_url=moderator.avatar_url,
        )

        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Moderator", value=moderator.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        if duration:
            embed.add_field(
                name="Duration:", value=humanize.naturaldelta(duration), inline=True
            )
        embed.set_footer(text=f"ID: {ctx.message.id}")
        log_channel = discord.utils.get(ctx.guild.channels, name=CONFIG["log_channel"])
        if log_channel:
            await log_channel.send(embed=embed)

        return embed

    @staticmethod
    @commands.Cog.listener()
    async def on_member_join(member):
        """Auto role."""
        if CONFIG["welcome_channel"]:
            channel = discord.utils.find(
                lambda m: m.name == CONFIG["welcome_channel"], member.guild.channels
            )
            await channel.send(f"Welcome {member.mention}!")
        if CONFIG["autorole"]:
            default_role = discord.utils.find(
                lambda m: m.name == CONFIG["autorole"], member.guild.roles
            )
            await member.add_roles(default_role)

    @commands.command(name="clear", aliases=["c"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=1):
        """
        Clear the specified amount of messages.
        Syntax: clear <amount> <optional:user>
        """
        channel = ctx.message.channel
        messages = []
        async for message in channel.history(limit=int(amount)):
            messages.append(message)
        await channel.delete_messages(messages)

    @commands.command(name="kick", aliases=["k"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason):
        """
        Kicks the specified user.
        Syntax: kick <user> <reason>
        """
        reason = "None specified"
        if not author.top_role > user.top_role:
            raise commands.MissingPermissions("Is superset")
        await user.kick(reason=reason)
        await self.mod_log(ctx, "Kick", user, reason)

    @commands.command(name="ban", aliases=["b"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason):
        """
        Bans the specified user.
        Syntax: ban <user> <reason>
        """
        reason = "None specified"
        if not ctx.author.top_role > user.top_role:
            raise commands.MissingPermissions("Is superset")
        await user.ban(reason=reason)
        await self.mod_log(ctx, "Ban", user, reason)

    @commands.command(name="unban", aliases=["pardon"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason):
        """
        Unbans the specified user.
        Syntax: unban <user> <reason>
        """
        guild = ctx.guild
        reason = "None specified"
        banned = await guild.fetch_ban(user)
        if banned:
            await guild.unban(user, reason=reason)
            await self.mod_log(ctx, "Unban", user, reason)

    @commands.command(name="tempban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, user: discord.Member, duration, *, reason):
        await ctx.invoke(self.ban, user=user, reason=reason)
        waffle.scheduler.set_task(ctx, "unban", duration, user.id)

    @commands.command(name="addrole")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, user: discord.Member, role: discord.role, *, reason):
        """
        Give the specified user a role.
        Syntax: addrole <user> <role>
        """
        author = ctx.author
        reason = "None specified"
        if not author.top_role > role:
            raise commands.missingpermissions("is superset")
        await user.add_roles(role)
        await self.mod_log(ctx, "Add role", user, reason, author)

    @commands.command(name="removerole")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def removerole(
        self, ctx, user: discord.Member, role: discord.role, *, reason
    ):
        """
        Remove a role from the specified user.
        Syntax: removerole <user> <role>
        """
        reason = "None specified"
        if not ctx.author.top_role > role:
            raise commands.missingpermissions("is superset")
        await user.remove_roles(role)
        await self.mod_log(ctx, "Remove role", user, reason)

    @commands.command(name="mute", aliases=["m"])
    @commands.guild_only()
    async def mute(self, ctx, user: discord.Member, *, reason):
        """
        Mute the specified user.
        Syntax: mute <user> <reason>
        """
        guild = ctx.guild
        mute_role = discord.utils.get(guild.roles, name=CONFIG["mute"])
        if mute_role is None and CONFIG["mute"]:
            await guild.create_role(name=CONFIG["mute"])

        if ctx.author.top_role > user.top_role and mute_role:
            if mute_role in user.roles:
                await ctx.send(f":no_entry_sign: {user.mention} is already muted!")
                return
            await user.add_roles(mute_role, reason=reason)
            await self.mod_log(ctx, "Mute", user, reason)
        elif not CONFIG["mute"]:
            ctx.send(":no_entry_sign: Muting is disabled!")
        else:
            raise commands.MissingPermissions("Is superset")

    @commands.command(name="unmute")
    @commands.guild_only()
    async def unmute(self, ctx, user: discord.Member, *, reason):
        """
        Unmute the specified user.
        Syntax: unmute <user> <reason>
        """
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name=CONFIG["mute"])
        if ctx.author.top_role > user.top_role:
            if muted in user.roles:
                await user.remove_roles(muted, reason=reason)
                await self.mod_log(
                    ctx,
                    "Unmute",
                    user,
                    reason
                )
            else:
                await ctx.send(f":no_entry_sign: {user.mention} " "is not muted!")
        else:
            raise commands.MissingPermissions("Is superset")

    @commands.command(name="tempmute")
    @commands.guild_only()
    async def tempmute(self, ctx, user: discord.Member, duration, *, reason):
        await ctx.invoke(self.mute, user=user, reason=reason)
        await waffle.scheduler.set_task(ctx, "unmute", duration, user.id)
