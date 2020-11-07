import discord
from discord.ext import commands
import requests
import bs4


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
        query = query.replace(" ", "%20")
        data = requests.get(f"https://www9.gogoanimehub.tv/search.html?keyword={query}").text
        soup = bs4.BeautifulSoup(data, "html5lib")
        links = soup.findAll('p', {"class":"name"})
        y = 0
        topthree = []
        for x in links:
            y += 1
            topthree.append(x.find('a')["href"])
            if y == 3:
                return topthree

class Anime(commands.Cog):
    """Anime Commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        with open("src/files/beboplinks.txt", "rb") as beboplinks:
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
        urls = await self.data.anistream(query, episode)
        embed = discord.Embed(title=f"Results for {query}", description="Hosted on GoGoAnime", color=0x88B04B)
        embed.add_field(name="Top Three Results", value=f"https://www9.gogoanimehub.tv{urls[0]}\nhttps://www9.gogoanimehub.tv{urls[1]}\nhttps://www9.gogoanimehub.tv{urls[2]}", inline=False)
        embed.set_thumbnail(url="https://art.ngfiles.com/images/1045000/1045801_shademeadows_ed-edward-cowboy-bebop-gif.gif?f1570486791")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AnimeData(bot))
    bot.add_cog(Anime(bot))
