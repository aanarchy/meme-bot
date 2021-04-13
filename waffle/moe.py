from jikanpy import AioJikan

import discord
from discord.ext import commands


def setup(bot):
    """Set up the cog."""
    bot.add_cog(Moe(bot))


class Moe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="moe", invoke_without_command=True)
    @commands.guild_only()
    async def moe(self, ctx):
        """
        Group for Anime-related command.
        """
        pass

