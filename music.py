import discord
from discord.ext import commands
from discord.ext.commands import Bot
import random
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
import yt_dlp
from yt_dlp import YoutubeDL
import time

# Suppress yt_dlp bug report spam

yt_dlp.utils.bug_reports_message = lambda *a, **k: ''
joinedChannel = None
channelToPost = None

ytdlopts = {
    'format': 'bestaudio/best[height<=480]',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192'
    }]
}
ytdl = YoutubeDL(ytdlopts)

class YTDLSource(discord.PCMVolumeTransformer):

    # sets up options to resume streaming of music if FFMPEG receives corrupted data(and therefore wants to terminate)

    ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    ytdl = YoutubeDL(ytdlopts)

    def __init__(self, source, *, data, requester):

        super().__init__(source)
        self.requester = requester
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')
        # YTDL info dicts (data) have other useful information you might want

        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        # retrieves information from search results

        return self.__getattribute__(item)

    @classmethod
    async def playlist_start(cls, ctx, search:str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        mySongUrl = "";
        i = 0;
        if 'entries' in data:
            mySongUrl = str(data['entries'][0])
            for x in data['entries']:
                data = x
                mySongUrl = str(data['webpage_url'])
                break
        return mySongUrl

@classmethod
async def create_playlist(cls, ctx, search: str, *, loop, download=False):
    loop = loop or asyncio.get_event_loop()
    data = await asyncio.to_thread(ytdl.extract_info, search, download=download)
    playlist = []

    for entry in data.get('entries', []):
        if not is_official(entry):
            playlist.append(str(entry['webpage_url']))

    if not playlist:
        await ctx.send("No non-official videos found in the playlist.")
        return []

    return playlist

#helper method for create_source below
#... Some videos are official without having vevo; so not using this yet
def is_official(info_dict):
    title = info_dict.get('title', '').lower()
    uploader = info_dict.get('uploader', '').lower()
    if any(x in title for x in ["official", "vevo"]) or any(x in uploader for x in ["official", "vevo", "music"]):
        return True
    return False

    @classmethod

    async def create_source(cls, ctx, search: str, *, loop, download=False):

        try:
          #  data = await loop.run_in_executor(None, ytdl.extract_info(search, download=download))
            data = await asyncio.to_thread(ytdl.extract_info, search, download=download)
            print(data)
        except Exception as e:
            await ctx.send(f"An error occured while processing: {e}")
            return None
        if 'entries' in data:
            data = data['entries'][0]
        embed = discord.Embed(title="", description=f"Queued [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]", color=discord.Color.green())
        await ctx.send(embed=embed)
        return cls(
            discord.FFmpegPCMAudio(
                data['url'],  # direct audio URL
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"  # ignore video
            ),
            data=data,
            requester=ctx.author
        )

    @classmethod
    async def create_source_no_announce(cls, ctx, search:str, *, loop, download=False):

        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}
        return cls(discord.FFmpegPCMAudio(source, **cls.ffmpeg_options), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        # Ensure seamless streaming of queue songs
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']
        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        return cls(discord.FFmpegPCMAudio(data['url'], **cls.ffmpeg_options), data=data, requester=requester)

class MusicPlayer:

    # Assistant class for Music. Sets up the queue and ensures the bot can be used across multiple servers if necessary.
    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')
    
    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.np = None  # Now playing message
        self.volume = .5
        self.current = None
        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.next.clear()
            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(1800):  # 30 minutes...
                    # vc.pause()
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)
            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue
            source.volume = self.volume
            self.current = source
            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self._guild.voice_client.pause();
            await asyncio.sleep(1);
            self._guild.voice_client.resume();
            # embed = discord.Embed(title="Now playing", description=f"[{source.title}]({source.web_url}) [{source.requester.mention}]", color=discord.Color.green())
            # self.np = await self._channel.send(embed=embed)
            await self.next.wait()
            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None
            
    def destroy(self, guild):

        # When disconnecting, delete instance of the bot (necessary for multiple servers)
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):

    # Contains all commands for Music-related inquiries
    __slots__ = ('bot', 'players')
    channelToPost = None
    
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        try:
            del self.players[guild.id]
        except KeyError:
            pass
        
    def get_player(self, ctx):
        # Ensures a MusicPlayer class was generated
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def playlist_(self, ctx, myList):

        player = self.get_player(ctx)
        del myList[0]
        for url in myList:
            source = await YTDLSource.create_source_no_announce(ctx, str(url), loop=self.bot.loop, download=False)
            await player.queue.put(source)

    async def play_first_(self, ctx, mySong):

           player = self.get_player(ctx)
           print(mySong)
           source = await YTDLSource.create_source_no_announce(ctx, str(mySong), loop=self.bot.loop, download=False)
           await player.queue.put(source)

    @commands.command(name='join', aliases=['connect', 'j'], description="Tells bot to join your voice channel")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):

        if channel is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
            else:
                await ctx.send("You are not in a channel")
                return
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command(name='play', aliases=['sing', 'p'], description="Plays a song with either given song name or URL")
    async def play_(self, ctx, *, search: str):
        # Play command takes a search string or URL and uses YT to play audio
        # Automatically joins the voice channel of requester
        # Sends a Queued Message
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You must be in a voice channel!")
                return
        elif vc.channel != ctx.author.voice.channel:
            await vc.move_to(ctx.author.voice.channel)
        player = self.get_player(ctx)
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)
        await player.queue.put(source)

    @commands.command(name='pause', aliases=["stop"], description="Pauses music")
    async def pause_(self, ctx):

        # Pauses the audio/queue
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif vc.is_paused():
            return
        vc.pause()
        await ctx.send("Paused ⏸️")
        
    @commands.command(name='resume', description="Resumes paused music")
    async def resume_(self, ctx):
        # Resumes audio/queue
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()

        await ctx.send("Resuming ⏯️")

    @commands.command(name="orbs")
    async def orbs_(self, ctx):
        await ctx.send('Yes <@350708347525267456> open orbs')

    @commands.command(name='leave', aliases=["dc", "disconnect", "bye"], description="stops music and disconnects from voice")
    async def leave_(self, ctx):
        # Tells bot to leave voice channel (and therefore runs destroy command on MusicPlayer)
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel so I couldn't leave", color=discord.Color.green())
            return await ctx.send(embed=embed)
        # await ctx.send('**Successfully disconnected**')
        await self.cleanup(ctx.guild)

    @commands.command(name='leaveg', description="Leaves guild")
    async def leaveg_(self, ctx, *, guild_name):

        guild = self.bot.get_guild(int(guild_name))
        await guild.leave()
        await ctx.send(f"Successfully left{guild.name}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, members, before, after):
        voice_state = members.guild.voice_client
        if voice_state is not None and len(voice_state.channel.members) == 1:
            await self.cleanup(members.guild)

async def setup(bot):
    await bot.add_cog(Music(bot))

