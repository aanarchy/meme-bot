import re
import sys
import datetime
import asyncio

import discord.utils
from sqlalchemy.sql import select

import waffle
import waffle.moderation
from waffle.tables import TasksTable

CONFIG = waffle.config.CONFIG


def string_to_seconds(string):
    time_mapping = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}

    seconds = 0
    for match in re.findall("(\d+)(s|m|h|d|w|y)", string, re.IGNORECASE):
        seconds += int(match[0]) * time_mapping[match[1].lower()]

    if seconds == 0:
        return False

    return seconds


async def set_task(ctx, function, duration, user_id):
    async with waffle.database.engine.begin() as conn:
        await conn.execute(
            TasksTable.insert(),
            {
                "guild_id": ctx.guild.id,
                "message_id": ctx.message.id,
                "channel_id": ctx.channel.id,
                "time": datetime.timedelta(seconds=string_to_seconds(duration))
                + datetime.datetime.now(),
                "function": function,
                "user_id": user_id,
            },
        )


async def check_for_tasks():
    async with waffle.database.engine.begin() as conn:
        tasks = await conn.execute(select(TasksTable))
    for task in tasks:
        if datetime.datetime.now() >= task["time"]:
            if task["function"] == "unmute":
                guild_id = task["guild_id"]
                user_id = task["user_id"]
                guild = waffle.bot.get_guild(guild_id)
                channel = guild.get_channel(task["channel_id"])
                message = await channel.fetch_message(task["message_id"])
                ctx = await waffle.bot.get_context(message)
                user = guild.get_member(user_id)
                muted = discord.utils.get(
                    ctx.guild.roles, name=CONFIG["config"]["mute"]
                )

                if muted in user.roles:
                    await user.remove_roles(muted, reason="Tempmute")
                    await waffle.moderation.Moderation.mod_log(
                        ctx,
                        "Unmute",
                        user,
                        "Tempmute",
                        ctx.author,
                    )
                async with waffle.database.engine.begin() as conn:
                    await conn.execute(
                        TasksTable.delete().where(
                            TasksTable.c.message_id == task["message_id"]
                        )
                    )
    await asyncio.sleep(CONFIG["database"]["check_interval"])
    await check_for_tasks()
