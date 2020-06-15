import re
from datetime import timedelta
import time
import asyncio

import waffle
from waffle.database import add, modify, get_collection
from waffle.config import CONFIG


CONFIG = CONFIG['database']


def string_to_seconds(string):
    time_mapping = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800,
        'y': 31536000
    }

    seconds = 0
    for match in re.findall('(\d+)(s|m|h|d|w|y)', string, re.IGNORECASE):
        seconds += int(match[0]) * time_mapping[match[1].lower()]

    if seconds == 0:
        return False

    return seconds


def set_task(ctx, function, duration, **kwargs):
    add('tasks', {
        'message_id': ctx.message.id,
        'time': int(string_to_seconds(duration) + time.time()),
        'function': function,
        'kwargs': kwargs
    })


async def check_for_tasks(tasks):
    for task in tasks:
        if time.time() >= task['time']:
            kwargs = task['kwargs']
            ctx = await waffle.bot.get_context(waffle.bot.fetch_message(task['message_id']))
            function = task['function']
            await ctx.invoke(function, **kwargs)
    await asyncio.sleep(CONFIG['check_interval'])
    check_for_tasks(get_collection('tasks'))
