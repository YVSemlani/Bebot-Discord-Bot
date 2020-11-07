import discord
from discord.ext import commands

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

def setup(bot):
    bot.add_cog(XP(bot))