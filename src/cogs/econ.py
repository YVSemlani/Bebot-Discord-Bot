import discord
from discord.ext import commands
import datetime as dt
import random
import asyncio
from asyncio import sleep

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
            await self.games[author.id]["message"].edit(embed=self.games[author.id]["embed"])
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

def setup(bot):
    bot.add_cog(BlackJack(bot))
    bot.add_cog(UserBalance(bot))
    bot.add_cog(Economy(bot))