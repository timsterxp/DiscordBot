import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl
import music,recs,misc

cogs=[music,recs,misc]
#test rebase
#misc is a personal file used for personal commands in server

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")


client = commands.Bot(command_prefix='-',intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)
    
client.run(DISCORD_TOKEN)


#@bot.event
# async def on_member_join(member):
#      for channel in member.guild.text_channels :
#          if str(channel) == "general" :
#              on_mobile=False
#              if member.is_on_mobile() == True :
#                  on_mobile = True
#              await channel.send("Welcome to the Server {}!!\n On Mobile : {}".format(member.name,on_mobile))             
#         
# # TODO : Filter out swear words from messages

