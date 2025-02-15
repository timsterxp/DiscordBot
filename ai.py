import discord
from discord.ext import commands
import openai
import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
clientAI = OpenAI(api_key= OPENAI_API_KEY)
BackendURL = os.getenv("BACKEND_URL")

class openAI(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ask", aliases=["how","leaguehelp"], description= "ChatGPT Help")   
    async def ask_(self,ctx,*, message: str):
        
        extraPrompt = "Try to keep answers concise and under 100 words if possible. Avoid cursing and inappropriate content entirely. Use text answers only. The prompt will be here: "
        message = extraPrompt + message
        try:
            response = requests.post(BackendURL, json= {"prompt": message} )
            
            if response.status_code==200:
                data = response.json()
                if "response" in data:
                    await ctx.send(data["response"])
                else:
                    await ctx.send("Sorry, I could not generate an answer with that prompt, please try again")
            else:
                await ctx.send("Dino may not have the ChatGPT option currently running, try again later")
        except Exception as e:
            await ctx.send("There was an error sorry, ChatGPT option may currently be off")
    

        
async def setup(bot):
    await bot.add_cog(openAI(bot))