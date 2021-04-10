import asyncio

import waffle.config
import waffle.scheduler

from discord.ext import commands

CONFIG = waffle.config.CONFIG["bot"]

bot = commands.Bot(
    command_prefix=CONFIG["prefix"], description="Morgz is my fav channel"
)


@bot.event
async def on_ready():
    """Print when the bot is ready."""
    print("*Waffles*")
    print("Logged in as")
    print(bot.user.id)


@bot.command()
async def ping(ctx):
    """Send pong in chat."""
    await ctx.send("pong!")


for extension in CONFIG["extensions"]:
    try:
        bot.load_extension(f"waffle.{extension}")
    except Exception as e:
        print("Failed to load extension {} because of error {}.".format(extension, e))


bot.run(CONFIG["token"])
asyncio.create_task(waffle.scheduler.check_for_tasks())
