import os

Config = {
    'token': 'NDYwOTk4MDg5Mzk5MDc0ODE2.XubV6Q.LX1Fl2TzhW62f4nyvAZLHn__-1I',   # Change the line in quotation marks to your own bot token.
    'prefix': 'waf ',
    'extensions': ['music', 'debug', 'moderation', 'errors'],
    'autorole': 'Member',   # Set this to None if you do not want autorole
    'dj': None,   # Set this to None if you do not want DJ functionality
    'log_channel': 'mod-log',
    'welcome_channel': None,   # Set this to None if you do not want welcome messages
    'mute': 'Edgelord'   # Set this to None if you want to disable muting
}

# Do not edit anything beyond this line

if os.environ.get('MONGODB_URI'):
    Config['database_uri'] = os.environ.get('MONGODB_URI')
else:
    Config['database_uri'] = 'mongodb://localhost:27017/'
