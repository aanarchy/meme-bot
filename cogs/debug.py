"""Debug commands."""
from discord.ext import commands


def setup(bot):
    """Set up the cog."""
    bot.add_cog(Debug(bot))


class Debug:
    """Debug class."""

    @staticmethod
    async def on_ready():
        """Print when the cog is ready."""
        print("Debug is ready!")

    def __init__(self, bot):
        """Initizises debug cog."""
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        """Log out of the bot user."""
        await self.bot.logout()
