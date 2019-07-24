"""Main bot."""
import config
from discord.ext import commands

bot = commands.Bot(command_prefix='m!', description='Morgz is my fav channel')


@bot.event
async def on_ready():
    """Print when the bot is ready."""
    print("*Surprised Pikachu Face*")
    print('Logged in as')
    print(bot.user.id)


@bot.command()
async def ping(ctx):
    """Send pong in chat."""
    await ctx.send("pong!")


extensions = []


if config.debug_enabled:
    extensions.append('cogs.debug')


if config.moderation_enabled:
    extensions.append('cogs.moderation')


if config.music_enabled:
    extensions.append('cogs.music')


for extension in extensions:
    try:
        bot.load_extension(extension)
    except Exception:
        print('Failed to load extension {}.'.format(extension))

bot.run(config.token)
