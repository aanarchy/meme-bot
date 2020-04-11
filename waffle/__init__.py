from config import Config
from discord.ext import commands

bot = commands.Bot(command_prefix=Config['prefix'],
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


for extension in Config["extensions"]:
    try:
        bot.load_extension(f"waffle.{extension}")
    except Exception as e:
        print('Failed to load extension {} because of error {}.'.format(
              extension, e))


bot.run(Config['token'])
