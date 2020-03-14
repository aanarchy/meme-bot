import re


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
