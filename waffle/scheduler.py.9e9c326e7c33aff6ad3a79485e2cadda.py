import re
import time
import asyncio

from waffle.database import add, modify, get
from waffle.config import Config


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


def set_task(function, duration, *args):
    add('tasks', {
        'time': duration + time.now(),
        'function': function,
        'arguments': args
    })


async def check_for_tasks(tasks):
    for task in tasks:
        if task['time'] >= time.now():
            args = task['args']
            getattr(task['function'])(*args)
    await asyncio.sleep(Config['check_interval'])
    check_for_tasks(get('tasks'))

