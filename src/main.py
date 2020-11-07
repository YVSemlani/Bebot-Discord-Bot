import discord
from discord.ext import commands
import wavelink
import os
from dotenv import load_dotenv

#setup
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="b.", intents=intents, case_insensitive=True)
client.wavelink = wavelink.Client(bot=client)
client.remove_command('help')
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
TOKEN = os.getenv('APIKEY')
print(TOKEN)

@client.event
async def on_ready():
    print(f"{client.user} is active")

client.load_extension("cogs.mod")
client.load_extension("cogs.music")
client.load_extension("cogs.anime")
client.load_extension("cogs.gaming")
client.load_extension("cogs.search")
client.load_extension("cogs.econ")
client.load_extension("cogs.help")
client.load_extension("cogs.XP")
client.run(TOKEN)

