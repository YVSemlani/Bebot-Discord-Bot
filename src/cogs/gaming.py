import discord
from discord.ext import commands
import requests

class GamingData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def mw_stats(self, platform, gamertag, gamemode="multiplayer"):
        try:
            oggamertag = gamertag
            gamertag = gamertag.replace("#", "%2523")
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
                stats = discord.Embed(title=oggamertag + "'s Multiplayer Stats", description="The true test of a man!!", color=0x88B04B)
                stats.add_field(name="KD", value=str(KD), inline=False)
                stats.add_field(name="Accuracy", value=str(Accuracy), inline=False)
                stats.add_field(name="RecordKills", value=str(RecordKills), inline=False)
                return stats
            else:
                data = response["br"]
                KD = data["kdRatio"]
                Kills = data["kills"]
                Wins = data["wins"]
                stats = discord.Embed(title=oggamertag + "'s Warzone Stats", description="The true test of a man!!", color=0x88B04B)
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
    async def mw(self, ctx, platform, gamertag, gamemode="multiplayer"):
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

def setup(bot):
    bot.add_cog(Gaming(bot))
    bot.add_cog(GamingData(bot))