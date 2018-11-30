"""Debug commands."""
from discord.ext import commands


def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Debug(bot))


class Debug:
    """Debug class."""

    @staticmethod
    async def on_ready():
        """Prints when the cog is ready."""
        print("Debug is ready!")

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        """Logs out of the bot user."""
        await self.bot.logout()
