import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
class Miscellaneous(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
    
    richie_pic=os.getenv("richie_pic")
    ivan_pic=os.getenv("ivan_pic")
    royce_pic=os.getenv("royce_pic")
    mark_pic=os.getenv("mark_pic")
        
    @commands.command(name="ivan", aliases=["owner"], description = "Explain Ivan")
    async def ivan_(self,ctx):
        embed = discord.Embed(title="About Ivan", description="I'm Ivan(<@533210066883444737>), I'm a giant full-time weeb,talk to me about anime or manga :]", color=discord.Color.green())
        embed.add_field(name="Fav Jungler", value="Kayn", inline=False)
        embed.add_field(name="Birthday", value="July 22nd", inline=False)
        embed.add_field(name="Weeb?", value="Very much so, lets play Dokkan Battle!", inline=False)
        embed.set_thumbnail(url=ivan_pic)
        
    @commands.command(name="richie", aliases=["arifan"], description = "Explain Richie")
    async def richie_(self,ctx):
        embed = discord.Embed(title="About Richie", description="I'm Richie(<@350708347525267456>), I'm an aspiring professional voice actor and can be super dramatic at times. I like buff dudes so... hit me up if you're one ;)", color=discord.Color.green())
        embed.add_field(name="Fav Support", value="Seraphine", inline=False)
        embed.add_field(name="Birthday", value="March 9th", inline=False)
        embed.set_thumbnail(url=richie_pic)
        await ctx.send(embed=embed)
        
    @commands.command(name="royce",description="Explain Royce")
    async def royce_(self,ctx):
        embed=discord.Embed(title="About Royce",description="Hi I'm Royce(<@145310838134276096>), I'm either on apex legends, dead by daylight or at an 'appointment' :shushing_face:")
        embed.add_field(name="Fav Champion",value="Horizon",inline=False)
        embed.add_field(name="Birthday",value="August 11th",inline=False)
        embed.set_thumbnail(url=royce_pic)
        await ctx.send(embed=embed)
        
    @commands.command(name="mark", description="Explain Mark")
    async def mark_(self,ctx):
        embed=discord.Embed(title="About Mark",description="Itz...Mark(<@378860708047224837>) :D Professional BM'er. Drives a civic")
        embed.add_field(name="Fav Champ",value="A Yasuo Main...smh.:face_vomiting:",inline=False)
        embed.add_field(name="Birthday",value="December 17th",inline=False)
        embed.set_thumbnail(url=mark_pic)
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Miscellaneous(bot))
    
#     
#         embed=discord.Embed(title="",description="")
#         embed.add_field(name="",value="",inline=False)
#         embed.add_field(name="",value="",inline=False)
#         await ctx.send(embed=embed)