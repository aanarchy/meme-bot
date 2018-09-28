"""Moderation commands."""
import discord
from discord.ext import commands

class Moderation:
    """Commands for moderation."""

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        """Prints when the cog is ready."""
        print("Moderation is ready!")

    async def mod_log(self, log_type, user, reason, moderator):
        """Mod logging."""
        embed = discord.Embed(title="Mod Log")
        embed.add_field(name="Type:", value=log_type, inline=True)
        embed.add_field(name="User:", value=user, inline=True)
        embed.add_field(name="Reason:", value=reason, inline=True)
        embed.set_footer(text=moderator)
        return embed

    @commands.command()
    async def embed(self, ctx):
        """Testing embed."""
        guild = ctx.guild
        embed = await self.mod_log("Ban", "@JamieTONG", "Because I can.", "@LLaurence")
        channels = guild.text_channels
        if 'mod_log' not in channels:
            overwrites = {
                guild.me: discord.PermissionOverwrite(send_messages=True),
                guild.members: discord.PermissionOverwrite(send_messages=True)
            }
            log_channel = await guild.create_text_channel("mod_log", overwrites=overwrites)
        else:
            log_channel = discord.utils.get(channels, name="mod_log")
        await log_channel.send(embed=embed)

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
            await ctx.send("%s, you do not have the permission to delete messages!" % author)

    @commands.command()
    async def kick(self, ctx, user: discord.Member, reason):
        """Kicks the specified user."""
        author = ctx.author
        if author.guild_permissions.kick_members and author.is_superset(user):
            await user.kick(reason=reason)
            await ctx.send("Kicked %s." % (user.name))
        else:
            await ctx.send("%s, you do not have the permission to kick that user!" % author)


    @commands.command()
    async def ban(self, ctx, user: discord.Member, reason):
        """Bans the specified user."""
        author = ctx.author
        if author.guild_permissions.ban_members and author.is_superset(user):
            await user.ban(reason=reason)
            await ctx.send("Banned %s from my house!" % (user.name))
        else:
            await ctx.send("%s, you do not have the permission to ban that user!" % author)


    @commands.command()
    async def unban(self, ctx, user: discord.User, reason):
        """Unbans the specified user."""
        author = ctx.author
        guild = ctx.guild
        if author.guild_permissions.ban_members:
            await guild.unban(user, reason=reason)
            await ctx.send("Unbanned %s." % (user.name))
        else:
            await ctx.send("%s, you do not have the permission to unban users!" % author)


    @commands.command()
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
        """Gives the specified user a role."""
        author = ctx.author
        if author.guild_permissions.manage_roles and author.top_role >= role:
            await user.add_roles(role)
            await ctx.send("I made %s a %s!" % (user.name, role.name))
        else:
            await ctx.send("%s, you don't have the permission to give that role to users!" % author)


    @commands.command()
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
        """Removes a role from the specified user."""
        author = ctx.author
        if author.guild_permissions.manage_roles and author.is_superset(user):
            await user.remove_roles(role)
            await ctx.send("I removed %s's %s role!" % (user.name, role.name))
        else:
            await ctx.send("%s, you don't have the permission to remove roles from users!" % author)

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
            await user.add_roles(muted, reason=reason)
            await ctx.send("I muted %s!" % (user.name))
        else:
            await ctx.send("%s, you don't have the permission to mute users!" % author)

    @commands.command()
    async def unmute(self, ctx, user: discord.Member, reason):
        """Unmutes the specified user."""
        author = ctx.author
        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name="Muted")
        if author.guild_permissions.manage_roles:
            await user.remove_roles(muted, reason=reason)
            await ctx.send("I unmuted %s!" % (user.name))
        else:
            await ctx.send("%s, you do not have the permission to mute other users!" % author)


def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Moderation(bot))
