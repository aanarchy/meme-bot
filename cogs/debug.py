"""Debug commands."""
from discord.ext import commands

class Debug:
    """Debug class."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        """Logs out of the bot user."""
        await self.bot.logout()

def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Debug(bot))
