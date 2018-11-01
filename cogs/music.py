"""Music commands."""
import asyncio
import pathlib
import os

import discord
from discord.ext import commands
import youtube_dl

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

    def create(self, query):
        """Creates song info."""
        extracted_info = self.from_youtube(query)
        self.video_id = extracted_info.get("id", None)
        self.url = extracted_info.get("webpage_url", None)
        self.title = extracted_info.get("title", None)
        self.duration = extracted_info.get("duration", None)
        self.filename = self.video_id + ".mp3"

    def download(self):
        """Downloads video."""
        if not pathlib.Path(self.filename).exists():
            self.youtube.extract_info(self.url, download=True)

    def from_youtube(self, request):
        """Gets video info."""
        if request.startswith("https://"):
            info = self.youtube.extract_info(request, download=False)
        else:
            info = self.youtube.extract_info("ytsearch:" + str(request), download=False)
        entries = info.get("entries", None)
        extracted_info = entries[0]
        return extracted_info

class Music:
    """Main music cog"""

    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue(maxsize=50)
        self.voice_client = None
        self._volume = 0.5
        self.loop = asyncio.get_event_loop()

    @staticmethod
    async def on_ready():
        """Prints a message when the cog is ready."""
        print('Music is ready!')

    @staticmethod
    def clear_song_cache():
        """Clears downloaded songs."""
        directory = 'C:/Users/Jamie/PyCharmProjects/mom-bot'
        songs = os.listdir(directory)
        for item in songs:
            if item.endswith(".mp3"):
                os.remove(os.path.join(directory, item))

    def next_song_info(self):
        if self.queue.empty():
            return None
        return self.queue.get_nowait()

    async def play_next_song(self, song=None):
        """Plays next song."""
        if song is None:
            self.voice_client.stop()
            self.clear_song_cache()
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            self.voice_client.play(discord.FFmpegPCMAudio(song),
                                   after=lambda e: self.loop.run_until_complete(self.play_next_song
                                                                                (self.next_song_info())))
            self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
            self.voice_client.volume = self._volume

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx):
        """Joins author's channel."""
        voice_state = ctx.author.voice
        self.voice_client = ctx.guild.voice_client
        if voice_state is None:
            await ctx.send("You aren't in a voice channel!")
        elif not self.voice_client:
            voice_channel = voice_state.channel
            self.voice_client = await voice_channel.connect()
        else:
            await ctx.send("I'm already in a voice channel!")

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, request):
        """Plays a song or adds a song to queue. Searches on youtube."""
        song = Song()
        song.create(request)
        voice_channel = ctx.author.voice.channel
        if self.voice_client is None or voice_channel != self.voice_client.channel:
            await ctx.invoke(self.join)
        if not self.voice_client.is_playing():
            song.download()
            await self.play_next_song(song.filename)
            await ctx.send("I'm playing %s for %s seconds!" % (song.title, song.duration))
        elif self.queue.full():
            await ctx.send("The queue is full! Please try again later.")
        else:
            song = self.yt.download(request)
            self.queue.put_nowait(song)
            await ctx.send("I queued up %s!" % song.title)

    @commands.command()
    async def stop(self, ctx):
        """Stops the voice client."""
        self.voice_client = ctx.guild.voice_client
        if self.voice_client is not None:
            if self.voice_client.is_playing():
                self.voice_client.stop()
            await self.voice_client.disconnect()
            del self.queue
            self.queue = asyncio.Queue(maxsize=50)
        else:
            await ctx.send("I'm not connected to voice!")

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses the voice client."""
        self.voice_client = ctx.guild.voice_client
        if self.voice_client is not None:
            if self.voice_client.is_paused():
                await ctx.send("I'm already paused!")
            else:
                self.voice_client.pause()
        else:
            await ctx.send("I'm not connected to voice!")

    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        """Resumes the voice client."""
        self.voice_client = ctx.guild.voice_client
        if self.voice_client is not None:
            if not self.voice_client.is_paused():
                await ctx.send("I'm not paused!")
            else:
                self.voice_client.resume()
        else:
            await ctx.send("I'm not connected to voice!")

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, volume):
        """Changes voice client volume."""
        self.voice_client = ctx.guild.voice_client
        self._volume = volume
        if self.voice_client:
            self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
            self.voice_client.volume = self._volume
        else:
            await ctx.send("I'm not connected to voice!")

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        """Skips next song."""
        self.voice_client = ctx.guild.voice_client
        if self.queue.empty():
            self.voice_client.stop()
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            source = self.queue.get_nowait()
            self.voice_client.source = discord.FFmpegPCMAudio(source)
            self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
            self.voice_client.volume = self._volume

def setup(bot):
    """Sets up the cog."""
    bot.add_cog(Music(bot))
