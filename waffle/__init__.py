from waffle import config
from discord.ext import commands

bot = commands.Bot(command_prefix=config.prefix,
                   description='Morgz is my fav channel')


@bot.event
async def on_ready():
    """Print when the bot is ready."""
    print("*Waffles*")
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


if config.error_enabled:
    extensions.append('cogs.errors')


for extension in extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('Failed to load extension {} because of error {}.'.format(
              extension, e))


bot.run(config.token)
