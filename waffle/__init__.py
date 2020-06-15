from waffle.config import CONFIG
from waffle.scheduler import check_for_tasks
from waffle.database import get_collection
from discord.ext import commands

CONFIG = CONFIG['bot']

bot = commands.Bot(command_prefix=CONFIG['prefix'],
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


for extension in CONFIG["extensions"]:
    try:
        bot.load_extension(f"waffle.{extension}")
    except Exception as e:
        print('Failed to load extension {} because of error {}.'.format(
              extension, e))


bot.run(CONFIG['token'])
check_for_tasks(get_collection('tasks'))
