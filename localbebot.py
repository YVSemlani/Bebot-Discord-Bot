import discord
from discord.ext import commands
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


#setup
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="b.", intents=intents, case_insensitive=True)
client.wavelink = wavelink.Client(bot=client)
client.remove_command('help')

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
        await ctx.message.delete()
        await ctx.channel.purge(limit=1000)
        await sleep(1)
        message = await ctx.send("Site of a nuke")
        await message.delete(delay=10)
        return
    
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def clear(self, ctx, amount=5):
        """Clear x amount of messages. X defaults to 5"""
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await sleep(1)
        message = await ctx.send(f"Cleared {str(amount)} messages.")
        await message.delete(delay=10)
        return
    
    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        """Kick the specified user."""
        await member.kick(reason=reason)
        await ctx.send(f"Kicked <@{member.id}>. GTFO dumb dumb.")
        await member.send(f"You have been kicked from {ctx.guild.name}! You were a bad boi!")
    
    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        """Ban the specified user."""
        await member.ban(reason=reason)
        await ctx.send(f"Banned <@{member.id}>. GTFO dumb dumb.")
        await member.send(f"You have been banned from {ctx.guild.name}! Dont do whatever you did!")
    
    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, ident):
        """Unban the specified user. Takes in user IDs. Requires developer mode to access user ID."""
        try:    
            print(type(ident))
            ident = int(ident)
            user = await self.bot.fetch_user(ident)
        except Exception as e:
            print(e)
            await ctx.send("Provide a valid User ID.")
            return
        print(type(user), user)
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been unbanned. You lucky bastard.")
        await member.send(f"You have been unbanned from {ctx.guild.name}! Tread lightly...")
    
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
        await member.add_roles(role) # adds already existing muted role
        await ctx.send(f"{member.mention} has been muted! What a numbskull XD.")
        await member.send(f"You have been muted in {ctx.guild.name}! Do better next time!")
        
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def unmute(self, ctx, member : discord.Member):
        """Unmute the specified member."""
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted"))
        await ctx.send(f"{member} has been unmuted. Maybe you were a good boy. Heres a :cookie: :)")
        await member.send(f"You have been unmuted in {ctx.guild.name}! Good Job :)")
    
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def welcome(self, ctx, state: str, *, channel):
        """Set Up a welcome message in the specified channel."""
        state = state.upper()
        ogchannel = channel
        print(type(channel), channel)
        try:
            channel = discord.utils.get(ctx.guild.channels, name=channel)
            if channel == None:
                channel = ogchannel
                raise Exception("Channel is None")
        except Exception as e:
            try:
                channel = await self.bot.fetch_channel(int(channel[2:len(channel)-1]))
            except Exception as e:
                print(e)
                await ctx.send("Invalid Channel. Try again numbskull :kissing_heart:")
                return
        if state == "ON":
            print(type(channel))
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
    
    @commands.command()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
        song = queue.data()[1]
        queue.skip()
        embed = discord.Embed(title=f"{song.title}", description="Playing Now",color=0x88B04B)
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
        print("Queueing")
        try:
            queue = await self.bot.QueueSystem.get_queue(ctx.guild.id)
            print("Chekpoint 1")
            embed = discord.Embed(title=f"{ctx.guild.name}'s queue", description="Song Queue", color=0x88B04B)
            print("Chekpoint 2")
            y = 0
            for x in queue.data():
                y += 1
                if len(queue.data()) < 10:
                    embed.add_field(name=f"{x.title}", value=f"Made by: [{x.author}]({x.uri}); Length: {round(x.length / 60000)};", inline=False)
                elif y == 10:
                    y = 0
                    await ctx.send(embed=embed)
                    embed = discord.Embed(title=f"{ctx.guild.name}'s queue", description="Song Queue", color=0x88B04B)
                    print("Chekpoint 3")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

class AnimeData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def anisearchid(self, query):
        print(query)
        data = requests.get("https://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=anime&nlist=all&name=" + query)
        data = data.text
        print("Checkpoint 1")
        soup = bs4.BeautifulSoup(data, 'lxml')
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

    async def anistream(self, query, episode):
        query = query.replace(" ", "-")
        return f"https://www9.gogoanimehub.tv/{query}-episode-{episode}"
class Anime(commands.Cog):
    """Anime Commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        with open("beboplinks.txt", "rb") as beboplinks:
            self.lines = list(beboplinks)
            beboplinks.close()

    @commands.command()
    async def watchbebop(self, ctx, episode):
        episodelink = self.lines[int(episode) - 1]
        embed = discord.Embed(title=f"Episode {episode}", description="Watch Cowboy Bebop Here. Episode 7 doesn't work.", color=0x88B04B)
        embed.add_field(name="Episode Link", value=f"[Episode {episode}]({episodelink.decode('utf-8')})", inline=False)
        embed.set_footer(text="Provided to you by Anime Jacks Paradise")
        embed.set_thumbnail(url="https://media0.giphy.com/media/4ilFRqgbzbx4c/giphy.gif")
        await ctx.send(embed=embed)

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
        except:
            print("Error Encountered")
            await ctx.send("正しいダンバスを綴る")
            await ctx.send("^ Spell Right Dumbass ^")
        embed = discord.Embed(title=query, description=query + " details.", color=0x88B04B)
        embed.add_field(name="Plot", value= "```"+ Plot + "```", inline=False)
        embed.add_field(name="Rating", value="```" + Rating + "```", inline=False)
        embed.add_field(name="Last Episode", value="```" + last_episode + "```", inline=False)
        embed.add_field(name="More Details from Anime News Network", value=f"[{query}]({Url})", inline=False)
        embed.add_field(name="Requested By", value="<@" + str(ctx.message.author.id) + ">")
        await ctx.send(embed=embed)
        return
    
    @commands.command()
    async def anistream(self, ctx, episode, *, query):
        self.data = self.bot.get_cog('AnimeData')
        url = await self.data.anistream(query, episode)
        embed = discord.Embed(title=f"Results for {query}", description=url, color=0x88B04B)
        embed.add_field(name="If this query didnt return a valid url then try adding tv to the end of it.", value="https://www9.gogoanimehub.tv", inline=False)
        embed.set_thumbnail(url=url)
        await ctx.send(embed=embed)
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
    
    async def porndata(self, query):
        query = query.replace(" ", "+")
        base = "https://www.pornhub.com"
        url = "https://www.pornhub.com/video/search?search=" + query
        resp = requests.get(url)
        soup = bs4.BeautifulSoup(resp.text, 'html5lib')
        findata = soup.findAll('a', {"class":"fade fadeUp videoPreviewBg linkVideoThumb js-linkVideoThumb img"})
        vids = []
        img = []
        try:
            for x in findata:
                img.append(x.find('img')["data-src"])
                vids.append(x["href"])
        except:
            pass
        vid = random.randint(0, len(vids)-1)
        suffix = vids[vid]
        thumb = img[vid]
        return base + suffix, thumb

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
            return
        if not ctx.message.channel.is_nsfw():
            if finalpost.over_18:
                await ctx.send("Not an nsfw channel bud. Begone horny.")
                return
        print(finalpost.permalink)
        embed = discord.Embed(title=finalpost.title, description=f"Upvotes: {finalpost.score}\n{finalpost.selftext}", color=0x88B04B, url=f"https://reddit.com{finalpost.permalink}")
        embed.set_footer(text=f"{finalpost.author} posted this in r/{finalpost.subreddit.display_name}")
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
        
    @commands.command()
    async def safesearch(self, ctx, *, query):
        """Gives you the safest videos on the internet based on your search"""
        self.SD = self.bot.get_cog('SearchData')
        if not ctx.message.channel.is_nsfw():
            await ctx.send("Take your horniness elsewhere.")
            return
        url, img = await self.SD.porndata(query)
        embed = discord.Embed(title=f"Results for {query}", description=" ", color=0x88B04B, url=url)
        embed.set_thumbnail(url=img)
        await ctx.send(embed=embed)
class User():
    def __init__(self, user_id):
        self.user_id = user_id
        self.balance = {"hand":0,"bank":0}
        self.daily = [dt.datetime.now() - dt.timedelta(days=2)]
    def bal(self):
        return self.balance
    
    def bank(self):
        return self.balance["bank"]
    
    def hand(self):
        return self.balance["hand"]
    
    def collected(self):
        self.daily = [dt.datetime.now()]
        return
    
    def last_collected(self):
        return self.daily[0]
class UserBalance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balancetracker = {}
        self.tophand = []
        self.topbank = []

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
    async def validateavailable(self, user_id, destination, amount):
        destination = destination.upper()
        if destination == "HAND":    
            if amount <= self.balancetracker[user_id].hand():
                return True
            else:
                return False
        elif destination == "BANK":
            if amount <= self.balancetracker[user_id].bank():
                return True
            else:
                return False
    async def leaderboards(self):
        print(self.balancetracker.keys())
        self.tophand, self.topbank = [], []
        for user_id in self.balancetracker.keys():
            print(user_id)
            self.tophand.append([user_id, self.balancetracker[user_id].hand()])
            self.topbank.append([user_id, self.balancetracker[user_id].bank()])
        self.tophand = sorted(self.tophand, key = lambda i: i[1], reverse=True)[:3]
        self.topbank = sorted(self.topbank, key = lambda i: i[1], reverse=True)[:3]
        banktop = discord.Embed(title="Bank Leaderboards", description="Rich Bois of the bank", color=0x88B04B)
        handtop = discord.Embed(title="Hand Leaderboards", description="Rich Bois of the hand", color=0x88B04B)
        print(self.topbank, self.tophand)
        for user in self.topbank:
            print(user)
            mention = await self.bot.fetch_user(user[0])
            amount = user[1]
            banktop.add_field(name=f"{mention.name}s Balance", value=f"Amount: {amount}$$$", inline=False)
        for user in self.tophand:
            print(user)
            mention = await self.bot.fetch_user(user[0])
            amount = user[1]
            handtop.add_field(name=f"{mention.name}s Balance", value=f"Amount: {amount}$$$", inline=False)
        return banktop, handtop

class BlackJack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ogbjdeck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]*4
        self.bjdeck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]*4
        self.games = {}
        self.message = None
        self.more = None
        self.playing = False

    async def deal(self, deck):
        hand = []
        for i in range(2):
            random.shuffle(self.bjdeck)
            card = self.bjdeck.pop()
            if card == 11:card = "J"
            if card == 12:card = "Q"
            if card == 13:card = "K"
            if card == 14:card = "A"
            hand.append(card)
        return hand

    async def total(self, hand):
        total = 0
        for card in hand:
            if card == "J" or card == "Q" or card == "K":
                total+= 10
            elif card == "A":
                if total >= 11: 
                    total+= 1
                else: 
                    total+= 11
            else:
               total += card
        return total

    async def hit(self, hand):
        card = self.bjdeck.pop()
        if card == 11:
            card = "J"
        if card == 12:
            card = "Q"
        if card == 13:
            card = "K"
        if card == 14:
            card = "A"
        hand.append(card)
        return hand

    async def score(self, dealer_hand, player_hand):
        dealer_total = await self.total(dealer_hand)
        player_total = await self.total(player_hand)
        if dealer_total == 21:
            return "BlackJack by the dealer. You Lose..."
        elif player_total == 21:
            return "BlackJack by the player. You Win..."
        elif dealer_total > 21:
            return "Dealer Bust. You Win..."
        elif player_total > 21:
            return "You Bust. You Lose..."
        elif dealer_total > player_total:
            return "Dealer has a better hand. You Lose..."
        elif dealer_total < player_total:
            return "You have a better hand. You Win..."
        elif dealer_total == player_total:
            return "You have equal hands. You Tie..."
        
    async def run(self, channel, author, amount):
        self.games[author.id] = {"bjdeck":self.bjdeck[:]}
        print(author.id)
        playerhand = "playerhand"
        dealerhand = "dealerhand"
        self.games[author.id]["dealerhand"] = await self.deal(self.games[author.id]["bjdeck"])
        self.games[author.id]["playerhand"] = await self.deal(self.games[author.id]["bjdeck"])
        self.games[author.id]["total"] = await self.total(self.games[author.id]["playerhand"])
        self.games[author.id]["embed"] = discord.Embed(title=f"{author.name}s BJ game", description=f"Playing for {amount}$", color=0x88B04B)
        self.games[author.id]["embed"].add_field(name=f"Dealer is showing", value=f"**{self.games[author.id][dealerhand]}**", inline=False)
        self.games[author.id]["embed"].add_field(name=f"Your hand is", value=f"**{self.games[author.id][playerhand]}**", inline=False)
        self.games[author.id]["hit"] = None
        self.games[author.id]["message"] = await channel.send(embed=self.games[author.id]["embed"])
        await self.games[author.id]["message"].add_reaction(emoji="⬅️")
        await self.games[author.id]["message"].add_reaction(emoji="⏹️")
        while self.games[author.id]["total"] < 21:
            while self.games[author.id]["hit"] == None:
                await sleep(1)
            if self.games[author.id]["hit"]:
                print("Hit")
                await self.hit(self.games[author.id]["playerhand"])
                self.games[author.id]["embed"].remove_field(1)
                self.games[author.id]["embed"].add_field(name=f"Your hand is", value=f"**{self.games[author.id][playerhand]}**", inline=False)
                self.games[author.id]["hit"] = None
                await self.games[author.id]["message"].edit(embed=self.games[author.id]["embed"])
            else:
                self.games[author.id]["embed"].remove_field(0)
                print("Player Portion is over")
                break
            self.games[author.id]["total"] = await self.total(self.games[author.id]["playerhand"])
        if self.games[author.id]["total"] > 21:
            self.games[author.id]["state"] = await self.score(self.games[author.id]["dealerhand"], self.games[author.id]["playerhand"])
            self.games[author.id]["embed"].add_field(name=f"Dealer is showing", value=f'**{self.games[author.id][dealerhand]}**', inline=False)  
            self.games[author.id]["embed"].add_field(name=self.games[author.id]["state"], value=f"**{amount}$$$**", inline=False)
            self.games[author.id]["message"].edit(embed=self.games[author.id]["embed"])
            return self.games[author.id]["state"]
        self.games[author.id]["totaldealer"] = await self.total(self.games[author.id]["dealerhand"])
        while self.games[author.id]["totaldealer"] < 17:
            await self.hit(self.games[author.id]["dealerhand"])
            self.games[author.id]["totaldealer"] = await self.total(self.games[author.id]["dealerhand"])
        self.games[author.id]["state"] = await self.score(self.games[author.id][dealerhand], self.games[author.id][playerhand])
        if "Win" in self.games[author.id]["state"] and "BlackJack" in self.games[author.id]["state"]:
            amount = amount * 2
        self.games[author.id]["embed"].add_field(name=f"Dealer is showing", value=f"**{self.games[author.id][dealerhand]}**", inline=False)
        self.games[author.id]["embed"].add_field(name=self.games[author.id]["state"], value=f"**{amount}$$$**", inline=False)
        await self.games[author.id]["message"].edit(embed=self.games[author.id]["embed"])
        return self.games[author.id]["state"]
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            print(user.id)
            if reaction.message == self.games[user.id]["message"] and user != self.bot.user:
                if reaction.emoji == "⬅️":
                    self.games[user.id]["hit"] = True
                else:
                    self.games[user.id]["hit"] = False
                await self.games[user.id].remove_reaction(reaction.emoji, user)
        except:
            print("Non Black Jack Reaction")
class Economy(commands.Cog):
    """Economy Commands"""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.UB = self.bot.get_cog('UserBalance')
    
    @commands.command()
    async def daily(self, ctx):
        """Daily reward of 5000 woolongs will be sent to your hand."""
        user_id = ctx.author.id
        try:
            await self.UB.get_user(user_id)
        except:
            await self.UB.create_user(user_id)
        if (await self.UB.validatedaily(user_id)):
            await self.UB.deposit(user_id, "hand", 5000)
            await self.UB.collected(user_id)
            print("Daily Collected")
            await ctx.send("Daily rations of 5000 woolong has been sent to your hand!")
        else:
            await ctx.send("You've already collected today GTFO of my shop!")
    
    @commands.command(aliases=["bal"])
    async def balance(self, ctx, user=None):
        """Returns the balance of the @mentioned user or if all returns the leaderboards for the Economy."""
        if user == None:
            user = ctx.message.author
            user_id = ctx.message.author.id
        elif user == "All" or user == "all":
            embed = await self.UB.leaderboards()
            banktop = embed[0]
            handtop = embed[1]
            await ctx.send(embed=banktop)
            await ctx.send(embed=handtop)
            return
        else:
            user_id = int(user[3:len(user) - 1])
            user = await self.bot.fetch_user(user_id)
            user_id = user.id
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
        
    @commands.command()
    async def give(self, ctx, user, amount):
        """Be a generous one and give some money to someone else. Funded by Daddy Bebot of course."""
        user_id = int(user[3:len(user) - 1])
        user = await self.bot.fetch_user(user_id)
        reciever = user.id
        giver = ctx.author.id
        givermention = ctx.author.mention
        recievermention = user.mention
        amount = int(amount)
        try:
            giverbal = await self.UB.get_user(giver)
        except:
            await self.UB.create_user(giver)
            giverbal = await self.UB.get_user(giver)
        try:
            recieverbal = await self.UB.get_user(reciever)
        except:
            await self.UB.create_user(reciever)
            recieverbal = await self.UB.get_user(reciever)
        if giverbal.hand() >= amount:
            await self.UB.extract(giver, "hand", amount)
            await self.UB.deposit(reciever, "hand", amount)
            await ctx.send(f"{amount} deposited in {recievermention}s account. Transaction funded by {givermention} and of course Daddy Bebot.")
        else:
            await ctx.send("Insufficient Funds broke boi!")
            return
        
    @commands.command()
    async def bj(self, ctx, amount):
        """Play some blackjack at the Bebot Casino."""
        self.bj = self.bot.get_cog('BlackJack')
        if int(amount) < 0:
            await ctx.send("You think your smart huh. You cant cheat the almighty Bebot.")
            return
        try:
            await self.UB.get_user(ctx.author.id)
        except:
            await self.UB.create_user(ctx.author.id)
        avail = await self.UB.validateavailable(ctx.author.id, "hand", int(amount))
        if not avail:
            await ctx.send("Hold your horses big better. You don't have the facilities for that.")
            return
        state = await self.bj.run(ctx.channel, ctx.author, amount)
        if "Win" in state:
            if "BlackJack" in state:
                await self.UB.deposit(ctx.author.id, "hand", int(amount)*2)
                return
            else:
                await self.UB.deposit(ctx.author.id, "hand", int(amount))
                return
        if "Lose" in state:
            await self.UB.extract(ctx.author.id, "hand", int(amount))
            return

    @commands.command()
    async def tohand(self, ctx, amount):
        try:
            avail = await self.UB.validateavailable(ctx.author.id, "bank", int(amount))
        except Exception as e:
            print(e)
            await ctx.send("You didn't enter a number to transfer")
            return
        if avail:
            await self.UB.extract(ctx.author.id, "bank", int(amount))
            await self.UB.deposit(ctx.author.id, "hand", int(amount))
            await ctx.send(f"{amount}$ was transferred to your hand.")
        else:
            await ctx.send("Sry but you dont have the funds for that ")
            
    @commands.command()
    async def tobank(self, ctx, amount):
        try:
            avail = await self.UB.validateavailable(ctx.author.id, "hand", int(amount))
        except Exception as e:
            print(e)
            await ctx.send("You didn't enter a number to transfer")
            return
        if avail:
            await self.UB.extract(ctx.author.id, "hand", int(amount))
            await self.UB.deposit(ctx.author.id, "bank", int(amount))
            await ctx.send(f"{amount}$ was transferred to your bank.")
        else:
            await ctx.send("Sry but you dont have the funds for that ")
       
class XP(commands.Cog):
    """XP Commands"""
    def __init__(self, bot):
        self.bot = bot
        self.users = {}
        self.levels = {}
        self.userlevel = {}
    @commands.Cog.listener()
    async def on_ready(self):
        for x in range(100 , 100001, 100):
            self.levels[x] = "Level " + str(x // 100)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        try:
            self.users[message.author.id] += 2.5
        except:
            self.users[message.author.id] = 0
        if self.users[message.author.id] in self.levels.keys():
            self.userlevel[message.author.id] = self.levels[self.users[message.author.id]]
            await message.channel.send(f"{message.author.mention} has attained {self.levels[self.users[message.author.id]]}")
    
    @commands.command()
    async def level(self, ctx, user=None):
        """Get your level in the current server"""
        if user == None:
            user = ctx.message.author
        else:
            user = user[3:len(user)-1]
            print(user)
            user = await self.bot.fetch_user(int(user))
        try:
            level = self.userlevel[user.id]
        except:
            self.userlevel[user.id] = "No Level"
            level = self.userlevel[user.id]
        embed = discord.Embed(title=f"{user.name} is {level}", description="Each level requires 100 points. You get 2.5 points per message you send.", color=0x88B04B)
        await ctx.send(embed=embed)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx, query=None):
        if query == None:
            embed = discord.Embed(title="Bebot Help Menu", description="Everything Bebot can do.", color=0x88B04B)
            embed.set_thumbnail(url="https://i.pinimg.com/originals/01/2e/71/012e716ba09bab32c9f3ea163b7663af.gif")
            embed.add_field(name="Mod Commands", value="Commands available only to people with permission to do these things manually. Useful for Moderators.", inline=False)
            embed.add_field(name="Music Commands", value="Commands for Playing Music", inline=False)
            embed.add_field(name="Anime Commands", value="Commands for Anime. Anything anime related is here.", inline=False)
            embed.add_field(name="Gaming Commands", value="Commands for Gaming. Do things like look up your stats or see active streams.", inline=False)
            embed.add_field(name="Economy Commands", value="Commands for your $$$. Do things like play BlackJack and collect money daily", inline=False)
            embed.add_field(name="XP Commands", value="Check what level you are and the top leaders of the Bebot Level game.", inline=False)
            embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
            await ctx.send(embed=embed)
            return
        else:
            query = query.upper()
            if query == "MOD":
                embed = discord.Embed(title="Mod Help Menu", description="All the mod commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/01/2e/71/012e716ba09bab32c9f3ea163b7663af.gif")
                embed.add_field(name="Clear", value="Clears the specified amount of messages. Defaults to 5.", inline=False)
                embed.add_field(name="Nuke", value="Clears 1000 messages. Causes major lag. Use at your own risk.", inline=False)
                embed.add_field(name="Kick", value="Kicks specified member from the server.", inline=False)
                embed.add_field(name="Ban", value="Bans specified member from the server.", inline=False)
                embed.add_field(name="Unban", value="Unbans the specified member from the server. Takes in an @mention or an id number. An id is not the 4 digits at the end of a username.", inline=False)
                embed.add_field(name="Mute", value="Mutes the specified member. Gives them the mute role and text mutes them as well as voice muting them. If they are in a VC they need to leave before voice mute takes effect.", inline=False)
                embed.add_field(name="Unmute", value="Unmutes the specified member. Takes away the unmuted role. If they are in a VC they need to leave for it to be active.", inline=False)
                embed.add_field(name="Welcome", value="Sets up a welcome message for new members in a specified channel. Used by typing b.welcome on #textchannel or b.welcome off #textchannel.", inline=False)
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "MUSIC":
                embed = discord.Embed(title="Music Help Menu", description="All the Music commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/01/2e/71/012e716ba09bab32c9f3ea163b7663af.gif")
                embed.add_field(name="Join", value="Joins the users current voice channel.", inline=False)
                embed.add_field(name="Leave/Stop", value="Leaves the bots current voice channel.", inline=False)
                embed.add_field(name="Play", value="Play the specified song. Use b.play dont stop believing or b.play video/playlist url", inline=False)
                embed.add_field(name="Pause", value="Pause the current playing song.", inline=False)
                embed.add_field(name="Unpause/Resume", value="Resume the current paused song.", inline=False)
                embed.add_field(name="Queue", value="Show the current queue.", inline=False)
                embed.add_field(name="Volume", value="Set the volume of the current player to a number. IE b.volume 10 sets the volume to 10.")
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "ANIME":
                embed = discord.Embed(title="Anime Help Menu", description="All the Anime commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/01/2e/71/012e716ba09bab32c9f3ea163b7663af.gif")
                embed.add_field(name="Anisearch", value="Get data of an anime by it's name. Spelling is very finnicky so try spelling it different ways. Capitalize the first letter.", inline=False)
                embed.add_field(name="Anistream", value="Get a stream of an anime by its name and episode number. Summoned using b.anistream")
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "GAMING":
                embed = discord.Embed(title="Gaming Help Menu", description="All the Gaming commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/01/2e/71/012e716ba09bab32c9f3ea163b7663af.gif")
                embed.add_field(name="MW", value="Get your modern warfare stats based on platform(xbl, psn, acti) gamertag and gamemode(warzone, mp). IE b.mw xbl Halfblood1223", inline=False)
                embed.add_field(name="Fortnite", value="Get your Fortnite stats based on platform(pc or console) server region(NAW, NAE, EU) and gamertag IE b.fortnite pc NAE Ninja", inline=False)
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
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
client.add_cog(BlackJack(client))
client.add_cog(XP(client))
client.add_cog(Help(client))
client.run('NzY5NDA5MTMwMzAwNDQwNTk2.X5OmFw.omDEZarxQyWWRY-Y2LPbEWjhi_0')