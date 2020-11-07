import discord
from discord.ext import commands

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
            embed.add_field(name="Economy Commands", value="Commands for your $$$. Do things like play Games and collect money daily", inline=False)
            embed.add_field(name="XP Commands", value="Check what level you are and the top leaders of the Bebot Level game.", inline=False)
            embed.add_field(name="User Support Commands", value="Get support from the server staff.", inline=False)
            embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
            await ctx.send(embed=embed)
            return
        else:
            query = query.upper()
            if query == "MOD":
                embed = discord.Embed(title="Mod Help Menu", description="All the mod commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://24.media.tumblr.com/57407804c86056de4a3bae164972261c/tumblr_msroypBO801rjlu67o1_500.gif")
                embed.add_field(name="Clear", value="Clears the specified amount of messages. Defaults to 5. Summoned using b.clear", inline=False)
                embed.add_field(name="Nuke", value="Clears 1000 messages. Causes major lag. Use at your own risk. Summoned using b.nuke", inline=False)
                embed.add_field(name="Kick", value="Kicks specified member from the server. Summoned using b.kick @person", inline=False)
                embed.add_field(name="Ban", value="Bans specified member from the server. b.ban @person", inline=False)
                embed.add_field(name="Unban", value="Unbans the specified member from the server. Takes in an @mention or an id number. An id is not the 4 digits at the end of a username. Summoned using b.unban userid", inline=False)
                embed.add_field(name="Mute", value="Mutes the specified member. Gives them the mute role and text mutes them as well as voice muting them. If they are in a VC they need to leave before voice mute takes effect. Summoned using b.mute @person", inline=False)
                embed.add_field(name="Unmute", value="Unmutes the specified member. Takes away the unmuted role. If they are in a VC they need to leave for it to be active. Turned on using b.welcome on #channelname and Turned off using b.welcome off #channelname", inline=False)
                embed.add_field(name="Welcome", value="Sets up a welcome message for new members in a specified channel. Summoned using b.welcome on #textchannel or b.welcome off", inline=False)
                embed.add_field(name="Get Warnings", value="Get the warnings of the entire guild or just the specific user. Summoned using b.getwarnings if you want the entire guild or b.getwarning @person to get the warnings of a specific user.", inline=False)
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "MUSIC":
                embed = discord.Embed(title="Music Help Menu", description="All the Music commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/01/2e/71/012e716ba09bab32c9f3ea163b7663af.gif")
                embed.add_field(name="Join", value="Joins the users current voice channel. Summoned using b.play", inline=False)
                embed.add_field(name="Leave/Stop", value="Leaves the bots current voice channel. Summoned using b.leave or b.stop", inline=False)
                embed.add_field(name="Play", value="Play the specified song. Use b.play dont stop believing or b.play url", inline=False)
                embed.add_field(name="Pause", value="Pause the current playing song. Summoned using b.pause", inline=False)
                embed.add_field(name="Unpause/Resume", value="Resume the current paused song. Summoned using b.resume of b.unpause", inline=False)
                embed.add_field(name="Queue", value="Show the current queue. Summoned using b.queue", inline=False)
                embed.add_field(name="Volume", value="Set the volume of the current player to a number. IE b.volume 10 sets the volume to 10.")
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "ANIME":
                embed = discord.Embed(title="Anime Help Menu", description="All the Anime commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/3b/31/03/3b3103df897011165b21afd57c3aa7fa.gif")
                embed.add_field(name="Anisearch", value="Get data of an anime by it's name. Spelling is very finnicky so try spelling it different ways. Capitalize the first letter.", inline=False)
                embed.add_field(name="Anistream", value="Get a stream of an anime by its name and episode number. If the first time doesnt work add tv to the end. Summoned using b.anistream IE b.anistream Black Clover TV")
                embed.add_field(name="WatchBebop", value="Get an episode of Cowboy Bebop from the google drive archive. Episode 7 isn't available. Summoned using b.watchbebop episodenum IE b.watchbebop 12", inline=False)
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "GAMING":
                embed = discord.Embed(title="Gaming Help Menu", description="All the Gaming commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.imgur.com/jEsFoj9.gif")
                embed.add_field(name="MW", value="Get your modern warfare stats based on platform(xbl, psn, acti) gamertag and gamemode(warzone, mp). IE b.mw xbl Halfblood1223", inline=False)
                embed.add_field(name="Fortnite", value="Get your Fortnite stats based on platform(pc or console) server region(NAW, NAE, EU) and gamertag IE b.fortnite pc NAE Ninja", inline=False)
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return
            elif query == "ECONOMY" or query == "ECON":
                embed = discord.Embed(title="Economy Help Menu", description="All the Economy commands Bebot has.", color=0x88B04B)
                embed.set_thumbnail(url="https://i.pinimg.com/originals/bb/a9/ed/bba9ed0e94dc334cdc385122ecdacc13.gif")
                embed.add_field(name="Daily", value="Get your 5000 woolongs every 24 hours. Summoned using b.daily", inline=False)
                embed.add_field(name="ToHand", value="Send money from your bank to your hand. Summoned using b.tohand amount.", inline=False)
                embed.add_field(name="ToBank", value="Send money from your hand to your bank. Summoned using b.tobank amount.", inline=False)
                embed.add_field(name="Balance/Bal", value="Get the balance of yourself, another player, or the leaderboards. Defaults to you. Summoned using b.bal @person or b.bal or b.bal all", inline=False)
                embed.add_field(name="BlackJack", value="Play a game of BlackJack for up to double your cash. Summoned using b.bj amount", inline=False)
                embed.set_footer(text="b.help <category> returns all the commands in a category. For example b.help mod returns all the Mod commands")
                await ctx.send(embed=embed)
                return

def setup(bot):
    bot.add_cog(Help(bot))