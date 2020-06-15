import discord
from discord.ext import commands


def setup(bot):
    """Set up the cog."""
    bot.add_cog(ErrorHandler(bot))


class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_ready():
        """Prints a message when the cog is ready."""

        print('Error Handler is ready!')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandInvokeError):
            raise error.__cause__

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":no_entry_sign: Command missing required "
                           "argument!")
        elif isinstance(error, commands.ExtensionNotLoaded):
            await ctx.send(":no_entry_sign: Extension was not loaded.")
        elif isinstance(error, commands.ExtensionFailed):
            await ctx.send(":no_entry_sign: Extension failed.")
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.send(":no_entry_sign: Extension not found.")
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.send(":no_entry_sign: Extension already loaded.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f":no_entry_sign: Command does not exist.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f":no_entry_sign: {ctx.author.mention}, you do not "
                           "have the permission to run this command.")
        elif isinstance(error, discord.NotFound):
            await ctx.send(':no_entry_sign: User does not exist or '
                           'is not banned.')
        elif isinstance(error, discord.Forbidden
                        or commands.BotMissingPermissions):
            await ctx.send(":no_entry_sign: I don't "
                           "have the permission "
                           "to run that command!")

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":no_entry_sign: This command can only be ran in a "
                           "guild/server.")
        elif isinstance(error, commands.NotOwner):
            await ctx.send(":no_entry_sign: That command can only be ran "
                           "by the owner of this bot, @Faith.")
        elif isinstance(error, commands.CheckFailure):
            if ctx.cog.name == "Moderation":
                await ctx.send(":no_entry_sign: Mod logging channel "
                               "does not exist! "
                               "Either create "
                               "a channel named 'mod-log' "
                               "or change the config file.")
            elif ctx.cog.name == "Music":
                await ctx.send(f":no_entry_sign: {ctx.author.mention}, you do "
                               "not have the permission to run this command.")
        if isinstance(error, discord.InvalidArgument
                      or commands.BadArgument):
            await ctx.send(":no_entry_sign: Invalid argument. Please check "
                           "that the arguments passed are of the right type.")
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(":no_entry_sign: Too many arguments passed.")
