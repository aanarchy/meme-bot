"""Main bot."""
from discord.ext import commands

bot = commands.Bot(command_prefix='!', description='I help you run errands!')

@bot.event
async def on_ready():
    """Prints when the bot is ready."""
    print("Mom is home!")
    print('Logged in as')
    print(bot.user.id)

@bot.command()
async def ping(ctx):
    """Sends pong in chat."""
    await ctx.send("pong!")


extensions = ['cogs.moderation', 'cogs.music']

for extension in extensions:
    try:
        bot.load_extension(extension)
    except Exception as exception:
        print('Failed to load extension %s.' % extension)

bot.run(TOKEN)
