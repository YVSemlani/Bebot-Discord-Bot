import discord
from discord.ext import commands
import nest_asyncio
import wavelink
import asyncio
from asyncio import sleep
import re
import requests
import bs4
import praw
import random
import urllib
from pretty_help import PrettyHelp, Navigation
import datetime as dt

#jupyter
nest_asyncio.apply()


#setup
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="b.", intents=intents, help_command=PrettyHelp(color=0x88B04B, active=60))
client.wavelink = wavelink.Client(bot=client)

@client.event
async def on_ready():
    print(f"{client.user} is active")

class Mod(commands.Cog):
    """Moderation Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def nuke(self, ctx):
        """Clear up to 1000 messages. Creates major lag."""
        await ctx.channel.purge(limit=1000)
        await ctx.send("Site of a nuke")
        await sleep(1.5)
        await ctx.channel.purge(limit=1)
        return

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def clear(self, ctx, amount=5):
        """Clear x amount of messages. X defaults to 5"""
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Cleared {str(amount)} messages.")
        await sleep(1.5)
        await ctx.channel.purge(limit=1)
        return

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        """Kick the specified user."""
        await member.kick(reason=reason)
        await ctx.send(f"Kicked <@{member.id}>. GTFO dumb dumb.")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        """Ban the specified user."""
        await member.ban(reason=reason)
        await ctx.send(f"Banned <@{member.id}>. GTFO dumb dumb.")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, ident: int):
        """Unban the specified user."""
        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def mute(self, ctx, member : discord.Member):
        """Mute the specified member."""
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
        """Unmute the specified member."""
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted"))
        await ctx.send(f"{member} has been unmuted. Maybe you were a good boy. Heres a :cookie: :)")

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def welcome(self, ctx, state: str, *, channel: str):
        """Set Up a welcome message in the specified channel."""
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
    """Welcome Message"""
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
        player = client.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            try:
                await ctx.invoke(client.get_command('join'))
            except Exception as e:
                print(e)
                await ctx.send("Join a voice channel motherfucker!!!")
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
                elapsed += 750
                if elapsed > song.length:
                    queue.skip()
                if len(channel.voice_states) == 1:
                    print("Leaving Now...")
                    await ctx.invoke(self.bot.get_command('leave'))
                    return

    @commands.command()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.latest()
        queue.skip()
        embed = discord.Embed(title=f"{song.title}", description="Skipping Now",color=0x88B04B)
        await ctx.send(embed=embed)
        player = client.wavelink.get_player(ctx.guild.id)
        await player.stop()

    @commands.command(aliases=["resume"])
    async def pause(self, ctx):
        """Pause or Unpause the current playing song."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.latest()
        player = client.wavelink.get_player(ctx.guild.id)
        if player.is_paused:
            await player.set_pause(False)
            await ctx.send(f"Resuming playing {song.title}")
        else:
            await player.set_pause(True)
            await ctx.send(f"Pausing playing {song.title}")

    @commands.command()
    async def queue(self, ctx):
        """Display the queue of songs."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        embed = discord.Embed(title=f"{ctx.guild.name}'s queue", description="Song Queue", color=0x88B04B)
        for x in queue.data():
            embed.add_field(name=f"{x.title}", value=f"Made by: [{x.author}]({x.uri}); Length: {round(x.length / 60000)};", inline=False)
        await ctx.send(embed=embed)

class AnimeData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def anisearchid(self, query):
        print(query)
        data = requests.get("https://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=anime&nlist=all&name=" + query)
        data = data.text
        print("Checkpoint 1")
        soup = bs4.BeautifulSoup(data, 'html5lib')
        items = soup.findAll('item')
        showid = {}
        for x in items:
            if x.find('name').text in showid.keys():
                showid[x.find('name').text + x.find('precision').text] = x.find('id').text
            else:
                showid[x.find('name').text] = x.find('id').text
        ids = []
        for x in showid.keys():
            if x == query or (query + "TV" in x):
                ids.append(showid[x])
        return ids[-1]
    async def anidetails(self, ident):
        data = requests.get("https://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=" + ident).text
        ani = bs4.BeautifulSoup(data, 'lxml')
        Plot = ani.find('info', {'type':'Plot Summary'}).text
        Plot = Plot[: len(Plot) - len("<em class=de-emphasized>(from manga)</em>") - 1]
        Rating = str(ani.find('ratings')['bayesian_score']) + "/10"
        last_episode = ani.find_all('title')[-1].text
        Url = "https://www.animenewsnetwork.com/encyclopedia/anime.php?id=" + ident
        return Plot, Rating, last_episode, Url

class Anime(commands.Cog):
    """Anime Commands"""
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def anisearch(self, ctx, *, query):
        """Gives you details on the queried anime. Make sure to spell correctly."""
        try:
            self.data = self.bot.get_cog('AnimeData')
            print(query)
            ident = await self.data.anisearchid(query)
            print(ident)
            Plot, Rating, last_episode, Url = await self.data.anidetails(ident)
            print(Url)
        except Exception as e:
            print("Error Encountered", e)
            await ctx.send("正しいダンバスを綴る")
            await ctx.send("^ Spell Right Dumbass ^")
            return
        embed = discord.Embed(title=query, description=query + " details.", color=0x88B04B)
        embed.add_field(name="Plot", value= "```"+ Plot + "```", inline=False)
        embed.add_field(name="Rating", value="```" + Rating + "```", inline=False)
        embed.add_field(name="Last Episode", value="```" + last_episode + "```", inline=False)
        embed.add_field(name="More Details from Anime News Network", value=f"[{query}]({Url})", inline=False)
        embed.add_field(name="Requested By", value="<@" + str(ctx.message.author.id) + ">")
        await ctx.send(embed=embed)
        return

class GamingData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mw_stats(self, platform, gamertag, gamemode="multiplayer"):
        try:
            url = "https://call-of-duty-modern-warfare.p.rapidapi.com/"+ gamemode + "/" + gamertag + "/" + platform
            print(url)
            headers = {
                'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
                'x-rapidapi-key': "cd8c290237msh39bd52e46714afbp19b68fjsncb8e461fb479"
                }

            response = requests.get(url, headers=headers).json()
            print(response)
            if gamemode == "multiplayer":
                data = response["lifetime"]["all"]["properties"]
                KD = data["kdRatio"]
                Accuracy = data["accuracy"]
                RecordKills = data["recordKillsInAMatch"]
                stats = discord.Embed(title=gamertag + "'s Multiplayer Stats", description="The true test of a man!!", color=0x88B04B)
                stats.add_field(name="KD", value=str(KD), inline=False)
                stats.add_field(name="Accuracy", value=str(Accuracy), inline=False)
                stats.add_field(name="RecordKills", value=str(RecordKills), inline=False)
                return stats
            else:
                data = response["br"]
                KD = data["kdRatio"]
                Kills = data["kills"]
                Wins = data["wins"]
                stats = discord.Embed(title=gamertag + "'s Warzone Stats", description="The true test of a man!!", color=0x88B04B)
                stats.add_field(name="KD", value=str(KD), inline=False)
                stats.add_field(name="Total Kills", value=str(Kills), inline=False)
                stats.add_field(name="Wins", value=str(Wins), inline=False)
                return stats
        except:
            return "Error was detected. Fuck off or Try Again."

    async def fortnite_stats(self, platform, region, epic):
        headers = {"TRN-Api-Key":"8a2ff3e2-5160-486b-a42b-4f8f68f6315f"}
        data = requests.get(f"https://api.fortnitetracker.com/v1/powerrankings/{platform}/{region}/{epic}", headers=headers)
        return data.json()
class Gaming(commands.Cog):
    """Gaming Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.data = self.bot.get_cog('GamingData')

    @commands.command()
    async def mw(self, ctx, platform, gamertag, gamemode):
        """Gets your Call of Duty Modern Warfare stats"""
        stats = await self.data.mw_stats(platform, gamertag, gamemode)
        if type(stats) != str:
            await ctx.send(embed=stats)
        else:
            await ctx.send(stats)

    @commands.command()
    async def fortnite(self, ctx, platform, region, *,epic):
        """Gets your Fortnite stats"""
        epic = epic.replace(" ", "%20")
        try:
            data = await self.data.fortnite_stats(platform, region, epic)
        except:
            await ctx.send("Input data is wrong numbskull")
            return
        name, region, rank = data["name"], data["region"], data["rank"]
        embed = discord.Embed(title=f"{name}s stats", description=f"{name}s Region {region}; {name}s Rank {rank}", color=0x88B04B)
        await ctx.send(embed=embed)
class SearchData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def rpost(self, query):
        reddit = praw.Reddit(client_id="FEWgDeuBkOyexA",
                         client_secret="cM0USkMCWVgX-B_-4CFj9zoh0tw",
                         password="Yashveer1",
                         user_agent="testscript by u/fakebot3",
                         username="Halfblood1223")
        posts = reddit.subreddit(query).hot(limit=25)
        data = []
        for post in posts:
            data.append(post)
        finalpost = data[random.randint(0,24)]
        return finalpost

class Search(commands.Cog):
    """Search Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rsearch(self, ctx, query):
        """Searches the queried subreddit for a random post of the top 25 most popular posts."""
        try:
            finalpost = await self.bot.get_cog('SearchData').rpost(query)
        except Exception as e:
            print(e)
            await ctx.send("Sub doesn't exist!!!")
        embed = discord.Embed(title=finalpost.title, description=finalpost.selftext, color=0x88B04B)
        print(finalpost.selftext, finalpost.url, finalpost.media_embed)
        req = urllib.request.Request(finalpost.url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req)
        contenttype = r.getheader('Content-Type')
        if finalpost.url.endswith((".jpg",".png",".gif")):
            embed.set_image(url=finalpost.url)
            print(finalpost.url)
            await ctx.send(embed=embed)
            return
        elif "image" not in contenttype and "video" not in contenttype or "youtube" in finalpost.media_embed:
            embed.add_field(name="Attachments", value=f"[Url]({finalpost.url})", inline=False)
            await ctx.send(embed=embed)
            return
        elif finalpost.media_embed != None:
            try:
                url = "http://old.reddit.com" + finalpost.permalink + ".json"
                print(url)
                response = requests.get(url, headers={'User-agent': 'testscript by u/fakebot3'}).json()
                media_url = response[0]['data']['children'][0]['data']['preview']['reddit_video_preview']['fallback_url']
                print(media_url)
                await ctx.send(embed=embed)
                await ctx.send(media_url)
                return
            except:
                try:
                    url = "http://old.reddit.com" + finalpost.permalink + ".json"
                    print(url)
                    response = requests.get(url, headers={'User-agent': 'testscript by u/fakebot3'}).json()
                    media_url = response[0]['data']['children'][0]['data']['preview']['reddit_video']['fallback_url']
                    print(media_url)
                    await ctx.send(embed=embed)
                    await ctx.send(media_url)
                    return
                except Exception as e:
                    print(e)
            return
        await ctx.send(embed=embed)
class User():
    def __init__(self, user_id):
        self.user_id = user_id
        self.balance = {"hand":0,"bank":0}
        self.daily = [dt.datetime.now() - dt.timedelta(days=2)]
    def bal(self):
        return self.balance

    def bank(self):
        return self.balance.bank

    def hand(self):
        return self.balance.hand

    def collected(self):
        self.daily = [dt.datetime.now()]
        return

    def last_collected(self):
        return self.daily[0]
class UserBalance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balancetracker = {}

    async def create_user(self, user_id):
        self.balancetracker[user_id] = User(user_id)

    async def get_user(self, user_id):
        return self.balancetracker[user_id]

    async def deposit(self, user_id, destination, amount):
        self.balancetracker[user_id].bal()[destination] += amount
        return

    async def extract(self, user_id, destination, amount):
        self.balancetracker[user_id].bal()[destination] -= amount
        return

    async def collected(self, user_id):
        self.balancetracker[user_id].collected()

    async def validatedaily(self, user_id):
        if (dt.datetime.now() - dt.timedelta(days=1)) > self.balancetracker[user_id].last_collected():
            return True
        else:
            return False

    async def leaderboards(self):
        pass
class Economy(commands.Cog):
    """Economy Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.UB = self.bot.get_cog('UserBalance')

    @commands.command()
    async def daily(self, ctx):
        user_id = ctx.author.id
        try:
            await self.UB.get_user(user_id)
        except:
            await self.UB.create_user(user_id)
        if (await self.UB.validatedaily(user_id)):
            await self.UB.deposit(user_id, "hand", 5000)
            await self.UB.collected(user_id)
            print("Daily Collected")
            await ctx.send("Daily rations of 5000 has been sent to your hand!")
        else:
            await ctx.send("You've already collected today GTFO of my shop!")

    @commands.command()
    async def balance(self, ctx, user):
        """Returns the balance of the @mentioned user or if all returns the leaderboards for the Economy."""
        user_id = int(user[3:len(user) - 1])
        user = await self.bot.fetch_user(user_id)
        user_id = user.id
        if user_id == None and (user != "All" or user != "all"):
            await ctx.send("Specify a real user dumbass!")
            return
        elif user == "All" or user == "all":
            embed = await self.UB.leaderboards()
            await ctx.send(embed=embed)
            return
        try:
            await self.UB.get_user(user_id)
        except:
            await self.UB.create_user(user_id)
        userbal = await self.UB.get_user(user_id)
        userbal = userbal.bal()
        bank = userbal["bank"]
        hand = userbal["hand"]
        embed = discord.Embed(title=f"{user.name}s Balance", description=f"On Hand: {hand}; In Bank: {bank}", color=0x88B04B)
        await ctx.send(embed=embed)

client.add_cog(Mod(client))
client.add_cog(Music(client))
client.add_cog(QueueSystem(client))
client.add_cog(songdata(client))
client.add_cog(Anime(client))
client.add_cog(AnimeData(client))
client.add_cog(GamingData(client))
client.add_cog(Gaming(client))
client.add_cog(SearchData(client))
client.add_cog(Search(client))
client.add_cog(UserBalance(client))
client.add_cog(Economy(client))
client.run('NzY5NDA5MTMwMzAwNDQwNTk2.X5OmFw.a_POKSLQSUIuoquvCSXE3QFTIfA')
