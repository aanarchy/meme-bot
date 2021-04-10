"""Debug commands."""
from discord.ext import commands

import waffle.scheduler
import waffle.database


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
        self.bot.reload_extension(f"waffle.{cog}")
        await ctx.send(f"{cog} has been reloaded.")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog):
        """Log out of the bot user."""
        self.bot.unload_extension(f"waffle.{cog}")
        await ctx.send(f"{cog} has been unloaded.")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog):
        """Log out of the bot user."""
        self.bot.load_extension(f"waffle.{cog}")
        await ctx.send(f"{cog} has been loaded.")

    @commands.command()
    @commands.is_owner()
    async def runcheck(self, ctx):
        """Runs check_for_task"""
        await waffle.scheduler.check_for_tasks()

    @commands.command()
    @commands.is_owner()
    async def clearcollection(self, ctx, database_name, collection_name):
        """Runs check_for_task"""
        waffle.database.client[database_name][collection_name].drop()
        await ctx.send(f"{collection_name} has been cleared.")

