"""Debug commands."""
from discord.ext import commands


def setup(bot):
    """Set up the cog."""
    bot.add_cog(Debug(bot))


class Debug(commands.Cog):
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

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog):
        """Log out of the bot user."""
        self.bot.reload_extension(f'waffle.{cog}')
        await ctx.send(f"{cog} has been reloaded.")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog):
        """Log out of the bot user."""
        self.bot.unload_extension(f'waffle.{cog}')
        await ctx.send(f"{cog} has been unloaded.")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog):
        """Log out of the bot user."""
        self.bot.load_extension(f'waffle.{cog}')
        await ctx.send(f"{cog} has been loaded.")
