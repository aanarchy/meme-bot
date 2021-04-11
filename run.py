import asyncio

import waffle

from discord.ext import commands

CONFIG = waffle.config.CONFIG["bot"]

bot = waffle.bot


@bot.event
async def on_ready():
    """Print when the bot is ready."""
    print("*Waffles*")
    print("Logged in as")
    print(bot.user.id)
    asyncio.ensure_future(waffle.scheduler.check_for_tasks())


@bot.command()
async def ping(ctx):
    """Send pong in chat."""
    await ctx.send("pong!")


@bot.command()
async def test(ctx, id):
    msg = await ctx.channel.fetch_message(id)
    await ctx.send(msg.content)


for extension in CONFIG["extensions"]:
    try:
        bot.load_extension(f"waffle.{extension}")
    except Exception as e:
        print("Failed to load extension {} because of error {}.".format(extension, e))


bot.run(CONFIG["token"])
