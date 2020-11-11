import discord
from discord.ext import commands
import asyncio
from asyncio import sleep
import datetime as dt
import pymongo
from pymongo import MongoClient
import os
from profanity import profanity

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
        await user.send(f"You have been unbanned from {ctx.guild.name}! Tread lightly...")
    @commands.command()
    async def softban(self, ctx, user: discord.Member, reason=None):
        await user.ban(reason=reason)
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} has been softbanned")
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def mute(self, ctx, member : discord.Member):
        """Mute the specified member."""
        role = discord.utils.get(ctx.guild.roles, name="Muted") # retrieves muted role returns none if there isn't 
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
    async def welcome(self, ctx, state: str, *, channel=None):
        """Set Up a welcome message in the specified channel."""
        state = state.upper()
        ogchannel = channel
        print(type(channel), channel)
        try:
            channel = discord.utils.get(ctx.guild.channels, name=channel)
            if channel == None and state == "OFF":
                channel = ogchannel
                await ctx.send("You need to set a channel if your trying to turn it on.")
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
    
    @commands.command()
    async def cursemod(self, ctx, state):
        state = state.upper()
        if state == "ON":
            try:
                if self.on:
                    await ctx.send("Curse Mod is already on")
            except:
                pass
            self.bot.add_cog(cursefilter(self.bot))
            self.on = True
            await ctx.send("Curse Filter is now on.")
        elif state == "OFF":
            self.on = False 
            self.bot.remove_cog('cursefilter')
            await ctx.send("Cursefilter is now off")
        else:
            return 

class cursefilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        custom_badwords = ["bitch", "shit", "ass", "dumbass"]                           
        profanity.load_words(custom_badwords)
        if profanity.contains_profanity(message.content):
            await message.delete()
            await message.channel.send("Stop cursing this server doesn't allow it.")
            
class welcome(commands.Cog):
    """Welcome Message"""
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("Member Incoming------>")
        await self.channel.send(f"Welcome to **{member.guild.name}** {member.mention}")

class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.MONGOCONNECT = os.getenv("MONGOCONNECT")
    @commands.command()
    async def ticket(self, ctx, *, ticketcontent):
        post = {"user_id":str(ctx.author.id), "name":ctx.author.name, "ticketcontent":ticketcontent, "timecreated":dt.datetime.now(), "guild":ctx.guild.id, "type":"Ticket"}
        cluster = pymongo.MongoClient(self.MONGOCONNECT)
        db = cluster["Bebot"]
        collection = db["Mod"]
        collection.insert_one(post)
        await ctx.send("Your ticket has been made!")
        
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def warn(self, ctx, user: discord.Member, *, reason=None):
        post = {"user_id":str(user.id), "name":user.name, "ticketcontent":reason, "timecreated":dt.datetime.now(), "guild":ctx.guild.id, "type":"Warning"}
        cluster = pymongo.MongoClient(self.MONGOCONNECT)
        db = cluster["Bebot"]
        collection = db["Mod"]
        collection.insert_one(post)
        await ctx.send(f"{user.mention} has been warned. Be a good boy from now on.")
        
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def gettickets(self, ctx, user:discord.Member=None):
        cluster = pymongo.MongoClient(self.MONGOCONNECT)
        db = cluster["Bebot"]
        collection = db["Mod"]
        if user != None:
            print(ctx.guild.id, type(ctx.guild.id), user.id, type(user.id))
            for post in collection.find({"guild":ctx.guild.id, "type":"Ticket", "user_id": str(user.id)}):
                name = post["name"]
                content = post["ticketcontent"]
                time = post["timecreated"].strftime("%m/%d/%Y")
                embed = discord.Embed(title=f"{name}s Ticket", description=f"Created on {time}", color=0x0FCF55)
                embed.add_field(name="Ticket Info", value=content, inline=False)
                await ctx.send(embed=embed)
            return
        else:
            print(ctx.guild.id, type(ctx.guild.id))
            for post in collection.find({"guild":ctx.guild.id, "type":"Ticket"}):
                name = post["name"]
                content = post["ticketcontent"]
                time = post["timecreated"].strftime("%m/%d/%Y")
                embed = discord.Embed(title=f"{name}s Ticket", description=f"Created on {time}", color=0x0FCF55)
                embed.add_field(name="Ticket Info", value=content, inline=False)
                await ctx.send(embed=embed)
            return
    
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def getwarnings(self, ctx, user:discord.Member=None):
        cluster = pymongo.MongoClient(self.MONGOCONNECT)
        db = cluster["Bebot"]
        collection = db["Mod"]
        if user != None:
            print(ctx.guild.id, type(ctx.guild.id), user.id, type(user.id))
            for post in collection.find({"guild":ctx.guild.id, "type":"Warning", "user_id": str(user.id)}):
                name = post["name"]
                content = post["ticketcontent"]
                time = post["timecreated"].strftime("%m/%d/%Y")
                embed = discord.Embed(title=f"{name}s Warning", description=f"Created on {time}", color=0x0FCF55)
                embed.add_field(name="Warning Info", value=content, inline=False)
                await ctx.send(embed=embed)
            return
        else:
            print(ctx.guild.id, type(ctx.guild.id))
            for post in collection.find({"guild":ctx.guild.id, "type":"Warning"}):
                name = post["name"]
                content = post["ticketcontent"]
                time = post["timecreated"].strftime("%m/%d/%Y")
                embed = discord.Embed(title=f"{name}s Warning", description=f"Created on {time}", color=0x0FCF55)
                embed.add_field(name="Warning Info", value=content, inline=False)
                await ctx.send(embed=embed)
            return
    @commands.has_permissions(manage_guild=True)    
    @commands.command()
    async def clearwarnings(self, ctx, user:discord.Member=None):
        cluster = pymongo.MongoClient(self.MONGOCONNECT)
        db = cluster["Bebot"]
        collection = db["Mod"]
        if user != None:
            collection.delete_many({"guild":ctx.guild.id, "type":"Warning", "user_id": str(user.id)})
            await ctx.send(f"The users infractions were cleared. {user.mention} you have a fresh start.")
        else:
            collection.delete_many({"guild":ctx.guild.id, "type":"Warning"})
            await ctx.send(f"The infractions of this guild have been cleared.")
    
    @commands.has_permissions(manage_guild=True)        
    @commands.command()
    async def cleartickets(self, ctx, user:discord.Member=None):
        cluster = pymongo.MongoClient(self.MONGOCONNECT)
        db = cluster["Bebot"]
        collection = db["Mod"]
        if user != None:
            collection.delete_many({"guild":ctx.guild.id, "type":"Ticket", "user_id": str(user.id)})
            await ctx.send(f"The users tickets were cleared. {user.mention} you have a fresh start.")
        else:
            collection.delete_many({"guild":ctx.guild.id, "type":"Ticket"})
            await ctx.send(f"The tickets of this guild have been cleared.")


def setup(bot):
    bot.add_cog(Mod(bot))
    bot.add_cog(ModMail(bot))