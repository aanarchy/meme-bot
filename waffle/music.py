"""Music commands."""
import asyncio
import pathlib
import os
from datetime import timedelta

import discord
from discord.ext import commands
import youtube_dl
import config


def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Music(bot))


class Song:
    """A song object to play youtube videos from."""

    def __init__(self):

        self.opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
        }
        self.youtube = youtube_dl.YoutubeDL(self.opts)
        self.filename = None
        self.url = None
        self.title = None
        self.video_id = None
        self.duration = 0
        self.position = None
        self.thumbnail = "https://youtube.com/"
        self.channel = None

    def create(self, query):
        """Creates song info."""

        extracted_info = self.from_youtube(query)
        self.video_id = extracted_info.get("id", None)
        self.url = extracted_info.get("webpage_url", None)
        self.title = extracted_info.get("title", None)
        self.duration_seconds = extracted_info.get("duration", None)
        self.duration = str(timedelta(seconds=self.duration_seconds))
        self.filename = self.video_id + ".mp3"
        self.thumbnail = f"https://img.youtube.com/vi/{self.video_id}/"\
                         "maxresdefault.jpg"
        self.uploader = extracted_info.get("uploader", None)
        self.channel_url = extracted_info.get("channel_url", None)
        self.artist = extracted_info.get("artist", None)
        self.position = 1

    def download(self):
        """Downloads video."""

        if not pathlib.Path(self.filename).exists():
            self.youtube.extract_info(self.url, download=True)

    def from_youtube(self, request):
        """Gets video info."""

        query = "ytsearch:" + str(request)
        info = self.youtube.extract_info(query, download=False)
        entries = info.get("entries", None)
        extracted_info = entries[0]
        return extracted_info

    def embed(self, author):
        embed = discord.Embed(title=self.title, url=self.url,
                              colour=discord.Colour(0x4a90e2))
        embed.set_image(url=self.thumbnail)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.add_field(name="Uploader", value=self.uploader,
                        inline=True)
        embed.add_field(name="Artist", value=self.artist,
                        inline=True)
        embed.add_field(name="Position in queue",
                        value=self.position, inline=True)
        embed.add_field(name="Duration:",
                        value=self.duration, inline=True)
        return embed


class GuildMusicState:
    """Class to store music states to seperate different guild's playlists"""

    def __init__(self, ctx, loop):
        self.bot = ctx.bot
        self.queue = asyncio.Queue(maxsize=50)
        self.voice = ctx.guild.voice_client
        self._volume = 0.05
        self.current_song = None
        self.loop = loop

    def next_song_info(self):

        if self.queue.empty():
            return None
        return self.queue.get_nowait()

    async def play_next_song(self, song=None):
        """Plays next song."""
        if song is None:
            self.voice.stop()
            await self.voice.disconnect()
            self.voice = None
        else:
            self.voice.play(discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio(song.filename),
                            volume=self._volume),
                            after=lambda e: self.voice.loop.run_until_complete(
                            self.play_next_song(self.next_song_info())
                            ))
            self.current_song = song


class Music(commands.Cog):
    """Main music cog"""

    def __init__(self, bot):

        self.bot = bot
        self.states = {}

    def is_dj():
        """Check if a specifed channel exists."""
        async def predicate(ctx):
            if config.dj:
                author = ctx.author
                converter = commands.RoleConverter()
                dj_role = await converter.convert(ctx, config.dj)
                if dj_role in author.roles:
                    return True
                else:
                    return False
            else:
                return True
        return commands.check(predicate)

    async def __before_invoke(self, ctx):
        ctx.music_state = self.states.setdefault(ctx.guild.id, GuildMusicState(
                                                 ctx, self.bot.loop))

    @staticmethod
    async def on_ready():
        """Prints a message when the cog is ready."""
        print('Music is ready!')

    @staticmethod
    def clear_song_cache():
        """Clears downloaded songs."""

        songs = os.listdir()
        for item in songs:
            if item.endswith(".mp3"):
                os.remove(item)

    @commands.command(name="join", aliases=['connect'])
    @commands.guild_only()
    async def join(self, ctx, channel=None):
        """Joins author's channel."""
        if not channel and not ctx.author.voice:
            ctx.send(f":no_entry_sign: {ctx.author.mention}, you have not "
                     "specified a channel nor are connected to one.")
        else:
            voice_channel = discord.utils.find(
                lambda m: m.name == channel, ctx.guild.voice_channels)
        if not self.states[ctx.guild.id]:
            self.voice = await voice_channel.connect()
        else:
            self.states[ctx.guild.id]

    @commands.command(name="play", aliases=["p"])
    @commands.guild_only()
    @is_dj()
    async def play(self, ctx, *keywords):
        """Plays or adds a song to queue. Args: <search terms/url>"""
        author = ctx.author
        song = Song()
        request = ""
        for kw in keywords:
            request = request + " " + kw
        song.create(request)
        voice_channel = author.voice.channel

        if self.voice is None or voice_channel != self.voice.channel:
            await voice_channel.connect()

        if not self.current_song:
            song.download()
            self.voice = ctx.guild.voice_client
            await self.play_next_song(song)
            await ctx.send(embed=song.embed(author))
        elif self.queue.full():
            await ctx.send(":no_entry_sign: "
                           "The queue is full! Please try again later.")
        else:
            self.queue.put_nowait(song)
            song.position = self.queue.qsize() + 1
            song.download()
            await ctx.send(embed=song.embed(author))

    @commands.command(name="stop", aliases=["disconnect"])
    @commands.guild_only()
    @is_dj()
    async def stop(self, ctx):
        """Stops the voice client."""

        self.voice = ctx.guild.voice_client

        if self.voice is not None:
            if self.voice.is_playing():
                self.voice.stop()
            await self.voice.disconnect()
            del self.queue
            self.queue = asyncio.Queue(maxsize=50)
            await ctx.send(":octagonal_sign: Stopped!")
        else:
            await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="pause")
    @commands.guild_only()
    @is_dj()
    async def pause(self, ctx):
        """Pauses the voice client."""

        self.voice = ctx.guild.voice_client

        if self.voice is not None:
            if self.voice.is_paused():
                await ctx.send(":no_entry_sign: I'm already paused!")
            else:
                self.voice.pause()
        else:
            await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="resume")
    @commands.guild_only()
    @is_dj()
    async def resume(self, ctx):
        """Resumes the voice client."""

        self.voice = ctx.guild.voice_client

        if self.voice is not None:
            if not self.voice.is_paused():
                await ctx.send(":no_entry_sign: I'm not paused!")
            else:
                self.voice.resume()
        else:
            await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="volume")
    @commands.guild_only()
    @is_dj()
    async def volume(self, ctx, volume: float):
        """Changes voice client volume. Args: <0.0-0.1>"""
        if volume >= 0.1:
            await ctx.send(":no_entry_sign: Volume over 0.1 is prohibited.")
        else:
            guild = ctx.guild
            self.voice = guild.voice_client
            self._volume = volume

            if self.voice:
                self.voice.source.volume = self._volume
                await ctx.send(
                    f":loud_sound: Changed volume to {self._volume}")
            else:
                await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="skip", aliases=["s"])
    @commands.guild_only()
    @is_dj()
    async def skip(self, ctx):
        """Skips to the next song."""

        self.voice = ctx.guild.voice_client
        self.voice.stop()
        await ctx.send(":track_next: Skipped!")

    @commands.command(name="loop", aliases=["l"])
    @commands.guild_only()
    @is_dj()
    async def loop(self, ctx):
        self.loop_enabled = True
