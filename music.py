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
import youtube_dl
from youtube_dl import YoutubeDL
import time

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

joinedChannel=None
channelToPost=None

#one used for playlists, other used for only one search
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
    'source_address': '0.0.0.0',  # ipv6 addresses cause issues sometimes
    'rm_cache_dir': True,
    'postprocessors':[{
        'key':'FFmpegExtractAudio',
        'preferredcodec':'mp3',
        'preferredquality':'192'}]
}

ytdlopts1 = {
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
    'source_address': '0.0.0.0',  # ipv6 addresses cause issues sometimes
    'playlistend': 2,
    'rm_cache_dir': True,
    'postprocessors':[{
        'key':'FFmpegExtractAudio',
        'preferredcodec':'mp3',
        'preferredquality':'192'}]
}

ytdlMax= YoutubeDL(ytdlopts1)
ytdl = YoutubeDL(ytdlopts)
class YTDLSource(discord.PCMVolumeTransformer):
    #sets up options to resume streaming of music if FFMPEG receives corrupted data(and therefore wants to terminate)
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
        #retrieves information from search results
        return self.__getattribute__(item)
    @classmethod
    async def playlist_start(cls,ctx,search:str,*,loop,download=False):
        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        mySongUrl="";
        i=0;
        if 'entries' in data:
            mySongUrl=str(data['entries'][0])
            for x in data['entries']:
                data=x 
                mySongUrl=str(data['webpage_url'])
                break
        return mySongUrl
        
    @classmethod
    async def create_playlist(cls,ctx,search:str,*,loop,download=False):
        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        playlist = []

        for i in data['entries']:
            data=i
            playlist.append(str(data['webpage_url']))
        return playlist       

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdlMax.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        
        if 'entries' in data:
            data=data['entries'][0]
            
        embed = discord.Embed(title="", description=f"Queued [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]", color=discord.Color.green())
        await ctx.send(embed=embed)
        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source,**cls.ffmpeg_options), data=data, requester=ctx.author)
    
    @classmethod
    async def create_source_no_announce(cls,ctx,search:str,*,loop,download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source,**cls.ffmpeg_options), data=data, requester=ctx.author)
    
    @classmethod
    async def regather_stream(cls, data, *, loop):
        #Ensure seamless streaming of queue songs
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'],**cls.ffmpeg_options), data=data, requester=requester)


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
                async with timeout(1800):  #30 minutes...
                    #vc.pause()
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
            
            #embed = discord.Embed(title="Now playing", description=f"[{source.title}]({source.web_url}) [{source.requester.mention}]", color=discord.Color.green())
            #self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        #When disconnecting, delete instance of the bot (necessary for multiple servers)
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    #Contains all commands for Music-related inquiries

    __slots__ = ('bot', 'players')
    
    channelToPost=None
    
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

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        #Ensures a MusicPlayer class was generated
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player
    
    async def playlist_(self,ctx,myList):
        player = self.get_player(ctx)
      
        del myList[0]
        for url in myList:
            source = await YTDLSource.create_source_no_announce(ctx, str(url),loop=self.bot.loop, download=False)
            await player.queue.put(source)
            
    async def play_first_(self,ctx,mySong):
           player = self.get_player(ctx)
           print(mySong)
           source = await YTDLSource.create_source_no_announce(ctx, str(mySong),loop=self.bot.loop, download=False)
           await player.queue.put(source)

            
    @commands.command(name='join', aliases=['connect', 'j'], description="Tells bot to join your voice channel")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        #Informs the bot to join the voice channel you are currently in
        if not channel:
            try:
                channel = ctx.author.voice.channel
                joinedChannel=channel
            except AttributeError:
                embed = discord.Embed(title="", description="No channel to join. Please call `-join` from a voice channel.", color=discord.Color.green())
                await ctx.send(embed=embed)
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client
        player = self.get_player(ctx)
        

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)

                player.volume=0.15
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()

                player.volume=0.15
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')
        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction('👍')
        channelToPost=ctx.channel.id
        print("channel found" + str(channelToPost))
        await ctx.guild.change_voice_state(channel=channel,self_mute=False,self_deaf=True)
    

    @commands.command(name='play', aliases=['sing','p'], description="Plays a song with either given song name or URL")
    async def play_(self, ctx, *, search: str):
        #Play command takes a search string or URL and uses YT to play audio
        #Automatically joins the voice channel of requester
        #Sends a Queued Message
        
        await ctx.trigger_typing()

        vc = ctx.voice_client
        
        if not vc:
            await ctx.invoke(self.connect_)
            
     #   if (ctx.author.display_name=="Burritomoo"):
     #       embed=discord.Embed(title="",description="No " + ctx.author.mention + ", I don't take commands from you" ,color=discord.Color.green())
     #       await ctx.send(embed=embed)
     #       return;
    

        player = self.get_player(ctx)

        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)
        
        if 'playlist?list' in search:
            #firstSong = await YTDLSource.playlist_start(ctx, search,loop=self.bot.loop,download=False)
            #await self.play_first_(ctx, firstSong)
            listOfSongs= await YTDLSource.create_playlist(ctx,search,loop=self.bot.loop,download=False)
            lengthSongs = str(len(listOfSongs))
            embed=discord.Embed(title="", description=f"Queued " + lengthSongs+ f" songs [{ctx.author.mention}]", color=discord.Color.green())
            await ctx.send(embed=embed)
            await self.playlist_(ctx,listOfSongs)
        

    @commands.command(name='pause', aliases=["stop"], description="Pauses music")
    async def pause_(self, ctx):
        #Pauses the audio/queue
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
        #Resumes audio/queue
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send("Resuming ⏯️")
    @commands.command(name="orbs")
    async def orbs_(self,ctx):
        await ctx.send('Yes <@350708347525267456> open orbs')
        
    @commands.command(name='skip', aliases=['next'], description="Skips to next song")
    async def skip_(self, ctx):
        #Goes to next song in queue if there is one
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
    
    @commands.command(name='remove', aliases=['rm', 'rem'], description="Remove song number from queue")
    async def remove_(self, ctx, pos : int=None):
        #Remove song from queue (necessary to know position)
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if pos == None:
            player.queue._queue.pop()
        else:
            try:
                s = player.queue._queue[pos-1]
                del player.queue._queue[pos-1]
                embed = discord.Embed(title="", description=f"Removed [{s['title']}]({s['webpage_url']}) [{s['requester'].mention}]", color=discord.Color.green())
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="", description=f'Could not find a track for "{pos}"', color=discord.Color.green())
                await ctx.send(embed=embed)
    
    @commands.command(name='clear', aliases=['clr', 'cl', 'cr'], description="Clear all songs in queue")
    async def clear_(self, ctx):
        #Resets queue to empty
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.send('💣 **Cleared**')

    @commands.command(name='queue', aliases=['q', 'playlist', 'que'], description="Display songs in queue")
    async def queue_info(self, ctx):
        #Displays the queue of songs
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="", description="queue is empty", color=discord.Color.green())
            return await ctx.send(embed=embed)

        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(f"`{(upcoming.index(_)) + 1}.` [{_['title']}]({_['webpage_url']}) | ` {duration} Requested by: {_['requester']}`\n" for _ in upcoming)
        fmt = f"\n__Now Playing__:\n[{vc.source.title}]({vc.source.web_url}) | ` {duration} Requested by: {vc.source.requester}`\n\n__Up Next:__\n" + fmt + f"\n**{len(upcoming)} songs in queue**"
        embed = discord.Embed(title=f'Queue for {ctx.guild.name}', description=fmt, color=discord.Color.green())
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='np', aliases=['song', 'current', 'currentsong', 'playing'], description="Display Song Title, Requester and Duration of Song")
    async def now_playing_(self, ctx):
        #Display Song Title, Requester and Duration of Song
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if not player.current:
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            return await ctx.send(embed=embed)
        
        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        embed = discord.Embed(title="", description=f"[{vc.source.title}]({vc.source.web_url}) [{vc.source.requester.mention}] | `{duration}`", color=discord.Color.green())
        embed.set_author(icon_url=self.bot.user.avatar_url, name=f"Now Playing 🎶")
        await ctx.send(embed=embed)

    @commands.command(name='volume', aliases=['vol', 'v'], description="Changes volume of songs, value of 0-100")
    async def change_volume(self, ctx, *, vol: float=None):
        #Changes the bot's volume, recommended volume according to Discord is 15%
        
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I am not currently connected to voice", color=discord.Color.green())
            return await ctx.send(embed=embed)
        
        if not vol:
            embed = discord.Embed(title="", description=f"🔊 **{(vc.source.volume)*100}%**", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if not 0 < vol < 101:
            embed = discord.Embed(title="", description="Please enter a value between 1 and 100", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)

#         if vc.source:
#             vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed(title="", description=f'**`{ctx.author}`** set the volume to **{vol}%**', color=discord.Color.green())
        await ctx.send(embed=embed)
    
    
    @commands.command(name='leave', aliases=["dc", "disconnect", "bye"], description="stops music and disconnects from voice")
    async def leave_(self, ctx):
        #Tells bot to leave voice channel (and therefore runs destroy command on MusicPlayer)
        
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel so I couldn't leave", color=discord.Color.green())
            return await ctx.send(embed=embed)

        #await ctx.send('**Successfully disconnected**')

        await self.cleanup(ctx.guild)
    
    @commands.command(name='leaveg', description="Leaves guild")
    async def leaveg(ctx,GID):
        guild = bot.get_guild(int(GID))
        await guild.leave()
        await ctx.send(f"Successfully left{guild.name}")
 
    @commands.Cog.listener()
    async def on_voice_state_update(self,members,before,after):
        voice_state = members.guild.voice_client
        if voice_state is not None and len(voice_state.channel.members)==1:
       
            
            await self.cleanup(members.guild)
        
   

def setup(bot):
    bot.add_cog(Music(bot))