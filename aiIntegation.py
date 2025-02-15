import discord
from discord.ext import commands
import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
clientAI = OpenAI(api_key= OPENAI_API_KEY)

class openAI(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ask", aliases=["how","leaguehelp"], description= "ChatGPT Help")   
    async def ask_(self,ctx, message: str):
        
      prompt = message.content[len("!ask "):]
      try:
          response = clientAI.chat.completions.create(
              model = "gpt-4o-mini",
              messages = [{"role": "user","content": prompt}],
              max_tokens = 200 
              )
          await message.channel.send(response.choices[0].message.content.strip())
      except Exception as e:
         await message.channel.send(f"Error: {str(e)}")
    

        
async def setup(bot):
    await bot.add_cog(openAI(bot))