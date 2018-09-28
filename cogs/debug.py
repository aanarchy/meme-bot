import discord
from discord import commands

class Debug:
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.is_owner()
    """Logs out of the bot user."""
    async def logout(self, ctx):
        await self.bot.logout()     

def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Debug(bot))           
