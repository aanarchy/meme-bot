"""Music commands."""
import asyncio
import pathlib
import os
from datetime import timedelta

import discord
from discord.ext import commands
import youtube_dl
from config import Config


def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Music(bot))


class Song:
    """A song object to play youtube videos from."""

    def __init__(self, ctx):

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
        self.requested_by = ctx.author

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
            try:
                self.youtube.extract_info(self.url, download=True)
            except youtube_dl.utils.DownloadError:
                return False

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
    """Class to store music states to separate different guild's playlists"""

    def __init__(self, ctx, loop):
        self.bot = ctx.bot
        self.queue = asyncio.Queue(maxsize=50)
        self.voice = ctx.guild.voice_client
        self.volume = 0.05
        self.current_song = None
        self.loop = loop
        self.repeat = False

    def next_song_info(self):
        try:
            self.queue.get_nowait()
        except youtube_dl.utils.DownloadError:
            return None

    async def play_next_song(self, song=None):
        """Plays next song."""
        if song is None:
            self.voice.stop()
            await self.voice.disconnect()
            self.voice = None
        else:
            self.voice.play(discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio(song.filename),
                            volume=self.volume),
                            after=lambda e: self.loop.create_task(
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
            if Config['dj']:
                author = ctx.author
                converter = commands.RoleConverter()
                dj_role = await converter.convert(ctx, Config['dj'])
                if dj_role in author.roles:
                    return True
                else:
                    return False
            else:
                return True
        return commands.check(predicate)

    async def cog_before_invoke(self, ctx):
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
            await ctx.send(f":no_entry_sign: {ctx.author.mention}, you "
                           "have not specified a channel "
                           " nor are connected to one.")
        else:
            voice_channel = discord.utils.find(
                lambda m: m.name == channel, ctx.guild.voice_channels)
            ctx.music_state = await voice_channel.connect()

    @commands.command(name="play", aliases=["p"])
    @commands.guild_only()
    @is_dj()
    async def play(self, ctx, *, request):
        """Plays or adds a song to queue. Args: <search terms/url>"""
        author = ctx.author
        song = Song(ctx)
        music_state = ctx.music_state
        song.create(request)

        if len(request) == 0:
            await ctx.send(f":no_entry_sign: please enter a song.")
            return

        if not author.voice:
            await ctx.send(f":no_entry_sign: {ctx.author.mention}, you are "
                           "not connected to any voice channel.")
            return

        voice_channel = author.voice.channel
        if not music_state.voice \
                or voice_channel != music_state.voice.channel:
            music_state.voice = await voice_channel.connect()

        if not music_state.current_song:
            if not song.download():
                await ctx.send(":no_entry_sign: Song not found!")
            await music_state.play_next_song(song)
            await ctx.send(embed=song.embed(author))
        elif music_state.queue.full():
            await ctx.send(":no_entry_sign: "
                           "The queue is full! Please try again later.")
        else:
            music_state.queue.put_nowait(song)
            song.position = music_state.queue.qsize() + 1
            if not song.download():
                await ctx.send(":no_entry_sign: Song not found!")
            else:
                await ctx.send(embed=song.embed(author))

    @commands.command(name="stop", aliases=["disconnect"])
    @commands.guild_only()
    @is_dj()
    async def stop(self, ctx):
        """Stops the voice client."""
        music_state = ctx.music_state

        if music_state.voice is not None:
            if music_state.voice.is_playing():
                music_state.voice.stop()
            await music_state.voice.disconnect()
            while music_state.queue.qsize() > 0:
                music_state.
            await ctx.send(":octagonal_sign: Stopped!")
        else:
            await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="pause")
    @commands.guild_only()
    @is_dj()
    async def pause(self, ctx):
        """Pauses the voice client."""
        music_state = ctx.music_state

        if music_state.voice is not None:
            if music_state.voice.is_paused():
                await music_state.send(":no_entry_sign: I'm already paused!")
            else:
                music_state.voice.pause()
        else:
            await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="resume")
    @commands.guild_only()
    @is_dj()
    async def resume(self, ctx):
        """Resumes the voice client."""
        music_state = ctx.music_state

        if music_state.voice is not None:
            if not music_state.voice.is_paused():
                await ctx.send(":no_entry_sign: I'm not paused!")
            else:
                music_state.voice.resume()
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
            music_state = ctx.music_state
            music_state.volume = volume

            if music_state.voice:
                music_state.voice.source.volume = music_state.volume
                await ctx.send(
                    f":loud_sound: Changed volume to {music_state.volume}")
            else:
                await ctx.send(":no_entry_sign: I'm not connected to voice!")

    @commands.command(name="skip", aliases=["s"])
    @commands.guild_only()
    @is_dj()
    async def skip(self, ctx):
        """Skips to the next song."""
        ctx.music_state.voice.stop()
        await ctx.send(":track_next: Skipped!")

    @commands.command(name="repeat", aliases=["loop"])
    @commands.guild_only()
    @is_dj()
    async def repeat(self, ctx):
        ctx.music_state.repeat = True

    @commands.command(name="queue", aliases=["q"])
    @commands.guild_only()
    async def queue(self, ctx):
        music_state = ctx.music_state
        queue = music_state.queue
        if queue.qsize() < 1 and not music_state.current_song:
            await ctx.send(":no_entry_sign: Queue is empty!")
            return
        song = music_state.current_song
        embed = discord.Embed(title=f'Queue for {ctx.guild}',
                              colour=discord.Colour(0xf8e71c),
                              description=f":play_pause: Now Playing:\n "
                              f"[{song.title}]"
                              f"({song.url}) {song.duration} | Requested by "
                              f"{song.requested_by.mention}\n\n\n"
                              f":arrow_down: Up next :arrow_down:")
        songs = tuple(queue._queue)
        for song in songs:
            embed.add_field(name=f"{song.position}. [{song.title}]"
                            f"({song.url})", value=f"{song.duration} "
                            f"| Requested by {song.requested_by.mention}",
                            inline=False)
        await ctx.send(embed=embed)
