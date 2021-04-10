import re
from datetime import timedelta
import time
import importlib
import asyncio

import discord.utils

import waffle

CONFIG = waffle.config.CONFIG["database"]


def string_to_seconds(string):
    time_mapping = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}

    seconds = 0
    for match in re.findall("(\d+)(s|m|h|d|w|y)", string, re.IGNORECASE):
        seconds += int(match[0]) * time_mapping[match[1].lower()]

    if seconds == 0:
        return False

    return seconds


def set_task(ctx, function, duration, **kwargs):
    waffle.database.add(
        "tasks",
        "tasklist",
        {
            "channel_id": ctx.channel.id,
            "message_id": ctx.message.id,
            "time": int(string_to_seconds(duration) + time.time()),
            "function": function,
            "kwargs": kwargs,
        },
    )


async def check_for_tasks():
    tasks = waffle.database.client["tasks"]["tasklist"].find({})
    for task in tasks:
        if time.time() >= task["time"]:
            kwargs = task["kwargs"]
            channel = waffle.bot.get_channel(task["channel_id"])
            message = await channel.fetch_message(task["message_id"])
            # message = discord.utils.get(waffle.bot.cached_messages, id=task['message_id'])
            ctx = await waffle.bot.get_context(message)
            await ctx.invoke(".waffle.moderation.unmute", **kwargs)
            waffle.database.remove(
                "tasks", "tasklist", {"message_id": task["message_id"]}
            )
    await asyncio.sleep(CONFIG["check_interval"])
    await check_for_tasks()
