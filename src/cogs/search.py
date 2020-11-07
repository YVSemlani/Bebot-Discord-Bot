import discord
from discord.ext import commands
import praw
import requests
import bs4
import urllib
import random

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

def setup(bot):
    bot.add_cog(SearchData(bot))
    bot.add_cog(Search(bot))