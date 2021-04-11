import re
import sys
import datetime
import asyncio

import discord.utils
from sqlalchemy.sql import select

import waffle
from waffle.tables import TasksTable

CONFIG = waffle.config.CONFIG["database"]


def string_to_seconds(string):
    time_mapping = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}

    seconds = 0
    for match in re.findall("(\d+)(s|m|h|d|w|y)", string, re.IGNORECASE):
        seconds += int(match[0]) * time_mapping[match[1].lower()]

    if seconds == 0:
        return False

    return seconds


async def set_task(ctx, function, duration, **kwargs):
    async with waffle.database.engine.begin() as conn:
        await conn.execute(
            TasksTable.insert(),
            {
                "channel_id": ctx.channel.id,
                "message_id": ctx.message.id,
                "time": datetime.timedelta(seconds=string_to_seconds(duration))
                + datetime.datetime.now(),
                "function": function,
            },
        )


async def check_for_tasks():
    async with waffle.database.engine.begin() as conn:
        tasks = await conn.execute(select(TasksTable))
    for task in tasks:
        if datetime.datetime.now() >= task["time"]:
            message = await channel.fetch_message(task["message_id"])
            if message:
                ctx = await waffle.bot.get_context(message)
                if muted in user.roles:
                    await user.remove_roles(muted, reason=reason)
                    embed = await waffle.moderation.Moderation.mod_log(
                        ctx.message.id,
                        ctx.message.created_at,
                        "Unmute",
                        user,
                        reason,
                        author,
                    )
            async with waffle.database.engine.begin() as conn:
                conn.execute(
                    TasksTable.delete().where(
                        TasksTable.c.message_id == task["message_id"]
                    )
                )
    await asyncio.sleep(CONFIG["check_interval"])
    await check_for_tasks()
