import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import yt_dlp,youtube_dl
import music,recs,misc
import asyncio

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
intents=discord.Intents.all()
intents.members=True
print("loading")
cogs=[music,recs,misc]
client = commands.Bot(command_prefix='-',intents=intents)

async def load_cogs():
    await music.setup(client)

 #   for i in range(len(cogs)):
 #      await cogs[i].setup(client)
    


async def main():
    await load_cogs()
    await client.start(DISCORD_TOKEN)
    
asyncio.run(main())