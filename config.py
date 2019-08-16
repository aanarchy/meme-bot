import os

"""Change the line in quotation marks to your own bot token."""
token = os.environ.get('DISCORD_TOKEN')
prefix = '//'
music_enabled = True
debug_enabled = True
moderation_enabled = True
error_enabled = True
autorole = 'Member'     # Set this to None if you do not want autorole
dj = None     # Set this to None if you do not want DJ functionality
log_channel = "mod-log"
welcome_channel = None   # Set this to None if you do not want welcome messages
