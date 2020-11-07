import discord
from discord.ext import commands
import wavelink
import asyncio
from asyncio import sleep
import sys
import re

class QueueSystem(commands.Cog):
    def __init__(self, bot):
        self.guildtracker = {}
        self.channeltracker = {}
        self.bot = bot
    
    async def newqueue(self, guild_id):
        queue = Queue()
        self.guildtracker[guild_id] = queue
        print("New queue generated")
        return
    
    async def get_queue(self, guild_id):
        return self.guildtracker[guild_id]
    
    async def newchannel(self, guild_id, channel):
        self.channeltracker[guild_id] = channel
        return
    
    async def get_channel(self, guild_id):
        return self.channeltracker[guild_id]

class Queue():
    def __init__(self):
        self.queue = []
        
    def clear(self):
        self.queue = []
    
    def add(self, item):
        self.queue.append(item)
        
    def skip(self, amount=1):
        for x in range(amount):
            self.queue.pop(0)
        
    def data(self):
        return self.queue
    
    def latest(self):
        return self.queue[0]

class songdata(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def songdata(self, query, guild_id):
        url_rx = re.compile(r'https?://(?:www\.)?.+')
        if url_rx.match(query) and "playlist" in query:
            print("Playlist searching now.....")
            playlist = await self.bot.wavelink.get_tracks(query)
            embed = discord.Embed(title=f"Playlist", description=f"Adding {len(playlist.tracks)} songs.", color=0x88B04B)
            for track in playlist.tracks:
                embed.add_field(name=f"{track.title}", value=f"Link to [{track.title}]({track.uri})", inline=False)
                queue = await self.bot.QueueSystem.get_queue(guild_id)
                queue.add(track)
            print(queue.data())
            return embed
        elif url_rx.match(query):
            print("Song searching now")
            track = await self.bot.wavelink.get_tracks(query)
            track = track[0]
            embed = discord.Embed(title=f"{track.title} was added to the queue", description=f"Url: {track.uri}; Length: {track.length}", color=0x88B04B)
            queue = await self.bot.QueueSystem.get_queue(guild_id)
            queue.add(track)
            return embed
        else:
            print("Song searching now")
            track = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")
            track = track[0]
            embed = discord.Embed(title=f"{track.title} was added to the queue", description=f"Url: {track.uri}; Length: {track.length}", color=0x88B04B)
            queue = await self.bot.QueueSystem.get_queue(guild_id)
            queue.add(track)
            return embed
class Music(commands.Cog):
    """Music Commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.bot.QueueSystem = self.bot.get_cog('QueueSystem')
        for guild in self.bot.guilds:
            await self.bot.QueueSystem.newqueue(guild.id)
        await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password='youshallnotpass',
                                              identifier='TEST',
                                              region='us_central')
    
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel=None):
        """Join the users current voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')
        player = self.bot.wavelink.get_player(ctx.guild.id)
        _ = await self.bot.QueueSystem.newchannel(ctx.guild.id, channel)
        await ctx.send(f'Connecting to **`{channel.name}`**')
        await player.connect(channel.id)
        
    @commands.command(aliases=["stop"])
    async def leave(self, ctx):
        """Leave the bots current voice channel."""
        try:
            queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
            queue.clear()
            player = self.bot.wavelink.get_player(ctx.guild.id)
            await player.destroy()
            queue.clear()
            await ctx.send("Bebot has left. Bebot doesn't miss you.")
        except Exception as e:
            print(e)
            await ctx.send("There is no active player... Dumbass")
            
    @commands.command()
    async def loop(self, ctx):
        """Loops the queue one time once it ends."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        data = queue.data()[:]
        try:
            for x in data:
                queue.add(x)
        except Exception as e:
            print(e)
            await ctx.send("Something thing went wrong and it was probably your fault!")
            return
        await ctx.send("Your queue will now loop once.")
    
    @commands.command()
    async def volume(self, ctx, *, query):
        """Set the volume to the queried amount"""
        try:
            player = self.bot.wavelink.get_player(ctx.guild.id)
            await player.set_volume(int(query))
        except Exception as e:
            print(e)
            await ctx.send("Either you put in something other than a number or theres nothing playing. Either way your retarded.")

        
    @commands.command()
    async def play(self, ctx, *, query):
        """Play the queried song or playlist. Songs and Playlist; Urls and Searches; are acceptable."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            try:
                await ctx.invoke(self.bot.get_command('join'))
            except Exception as e:
                print(e)
                await ctx.send("Join a voice channel motherfucker!!!")
                return
        if ctx.author.voice == None:
            await ctx.send("Sorry to control the music you have to be in a VC.")
            return
        await ctx.send(embed=await self.bot.get_cog('songdata').songdata(query, ctx.guild.id))
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        channel = await self.bot.QueueSystem.get_channel(ctx.guild.id)
        while True:
            song = queue.latest()
            if song == None:
                return
            if player.is_playing:
                pass
            else:
                await player.play(song)
            elapsed = 0
            while queue.latest() == song:
                await sleep(1)
                elapsed += 975
                if elapsed > song.length:
                    queue.skip()
    
    @commands.command()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.data()[1]
        queue.skip()
        embed = discord.Embed(title=f"{song.title}", description="Playing Now",color=0x88B04B)
        await ctx.send(embed=embed)
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await player.stop()
        
    @commands.command(aliases=["resume"])
    async def pause(self, ctx):
        """Pause or Unpause the current playing song."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.latest()
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if player.is_paused:
            await player.set_pause(False)
            await ctx.send(f"Resuming playing {song.title}")
        else:
            await player.set_pause(True)
            await ctx.send(f"Pausing playing {song.title}")
            
    @commands.command()
    async def queue(self, ctx):
        """Display the queue of songs."""
        print("Queueing")
        try:
            queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
            print("Chekpoint 1")
            embed = discord.Embed(title=f"{ctx.guild.name}'s queue", description="Song Queue", color=0x88B04B)
            print("Chekpoint 2")
            y = 0
            for x in queue.data():
                y += 1
                print(x.title.encode(sys.stdout.encoding, errors='replace'))
                embed.add_field(name=f"{x.title}", value=f"Made by: [{x.author}]({x.uri}); Length: {round(x.length / 60000)};", inline=False)
                if y == 10:
                    y = 0
                    await ctx.send(embed=embed)
                    embed = discord.Embed(title=f"{ctx.guild.name}'s queue", description="Song Queue", color=0x88B04B)
                    print("Chekpoint 3")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

def setup(bot):
    bot.add_cog(Music(bot))
    bot.add_cog(QueueSystem(bot))
    bot.add_cog(songdata(bot))