import discord
from discord.ext import commands
import nest_asyncio
import wavelink
import asyncio
from asyncio import sleep
import re


#setup
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="b.", intents=intents)
client.remove_command("help")
client.wavelink = wavelink.Client(bot=client)

@client.event
async def on_ready():
    print(f"{client.user} is active")

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def nuke(self, ctx):
        await ctx.channel.purge(limit=1000)
        await sleep(1.5)
        await ctx.send("Site of a nuke")
        await ctx.channel.purge(limit=1)
        return

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        await sleep(1.5)
        await ctx.send(f"Cleared {str(amount)} messages.")
        await ctx.channel.purge(limit=1)
        return

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"Kicked <@{member.id}>. GTFO dumb dumb.")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"Banned <@{member.id}>. GTFO dumb dumb.")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, ident: int):
        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def mute(self, ctx, member : discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted") # retrieves muted role returns none if there isn't
        hell = discord.utils.get(ctx.guild.text_channels, name="hell") # retrieves channel named hell returns none if there isn't
        if not role: # checks if there is muted role
            muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            for channel in ctx.guild.channels: # removes permission to view and send in the channels
                await channel.set_permissions(muted, send_messages=False,
                                              read_message_history=True,
                                              read_messages=True, speak=False)
            await member.add_roles(muted) # adds newly created muted role
            await ctx.send(f"{member.mention} has been muted! What a numbskull XD.")
        else:
            await member.add_roles(role) # adds already existing muted role
            await ctx.send(f"{member.mention} has been muted! What a numbskull XD.")

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def unmute(self, ctx, member : discord.Member):
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted"))
        await ctx.send(f"{member} has been unmuted. Maybe you were a good boy. Heres a :cookie: :)")

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def welcome(self, ctx, state: str, *, channel: str):
        state = state.upper()
        try:
            channel = discord.utils.get(ctx.guild.channels, name=channel)
        except Exception as e:
            print(e)
            await ctx.send("Invalid Channel. Try again numbskull :kissing_heart:")
            return
        if state == "ON":
            self.bot.add_cog(welcome(self.bot, channel))
            await ctx.send("Welcome successfully set up!!!")
        elif state == "OFF":
            try:
                self.bot.remove_cog('welcome')
            except Exception as e:
                print(e)
                await ctx.send("Welcome message is not currently on.")
                return
        else:
            await ctx.send("You didn't put in a valid value.")
            return

class welcome(commands.Cog):
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("Member Incoming------>")
        await self.channel.send(f"Welcome to **{member.guild.name}** {member.mention}")

class QueueSystem(commands.Cog):
    def __init__(self, bot):
        self.guildtracker = {}
        self.bot = bot

    async def newqueue(self, guild_id):
        queue = Queue()
        self.guildtracker[guild_id] = queue
        print("New queue generated")
        return

    async def get_queue(self, guild_id):
        return self.guildtracker[guild_id]

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
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send('No channel to join. Please either specify a valid channel or join one. Dumbass :)')
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connecting to **`{channel.name}`**')
        await player.connect(channel.id)

    @commands.command()
    async def leave(self, ctx):
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
    async def play(self, ctx, *, query):
        await ctx.send(embed=await self.bot.get_cog('songdata').songdata(query, ctx.guild.id))
        player = client.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(client.get_command('join'))
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        while True:
            song = queue.latest()
            await player.play(song, replace=False)
            while player.is_playing:
                await sleep(3)

    @commands.command()
    async def skip(self, ctx):
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.latest()
        queue.skip()
        embed = discord.Embed(title=f"{song.title}", description="Skipping Now",color=0x88B04B)
        await ctx.send(embed=embed)
        player = client.wavelink.get_player(ctx.guild.id)
        await player.stop()

    @commands.command(aliases=["resume"])
    async def pause(self, ctx):
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.latest()
        player = client.wavelink.get_player(ctx.guild.id)
        if player.is_paused:
            await player.set_pause(False)
            await ctx.send(f"Resuming playing {song.title}")
        else:
            await player.set_pause(True)
            await ctx.send(f"Pausing playing {song.title}")
client.add_cog(Mod(client))
client.add_cog(Music(client))
client.add_cog(QueueSystem(client))
client.add_cog(songdata(client))
client.run('NzY5NDA5MTMwMzAwNDQwNTk2.X5OmFw.a_POKSLQSUIuoquvCSXE3QFTIfA')
