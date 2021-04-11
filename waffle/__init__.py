import discord
from discord.ext import commands

import waffle.config
import waffle.scheduler

CONFIG = waffle.config.CONFIG["bot"]

intents = discord.Intents().all()
bot = commands.Bot(
    command_prefix=CONFIG["prefix"],
    description="Morgz is my fav channel",
    intents=intents,
)
