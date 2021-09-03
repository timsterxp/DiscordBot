import discord
from discord.ext import commands

class Miscellaneous(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        
        
    @commands.command(name="ivan", aliases=["owner"], description = "Explain Ivan")
    async def ivan_(self,ctx):
        embed = discord.Embed(title="About Ivan", description="I'm Ivan, I'm a giant weeb,talk to me about anime or manga :]", color=discord.Color.green())
        embed.add_field(name="Fav Jungler", value="Kayn", inline=False)
        embed.add_field(name="Birthday", value="July 22nd", inline=False)
        embed.add_field(name="Weeb?", value="Very much so, lets play Dokkan Battle!", inline=False)
        embed.set_thumbnail(url="https://scontent-sjc3-1.xx.fbcdn.net/v/t1.18169-9/10606489_708208505919810_4978127567445276728_n.jpg?_nc_cat=106&ccb=1-5&_nc_sid=09cbfe&_nc_ohc=vuQlqFFCCv0AX-tNrGq&_nc_ht=scontent-sjc3-1.xx&oh=4cff94312635cf90fa32f27d2937379b&oe=61550937")
        await ctx.send(embed=embed)
        
    @commands.command(name="richie", aliases=["arifan"], description = "Explain Richie")
    async def richie_(self,ctx):
        embed = discord.Embed(title="About Richie", description="I'm Richie, I'm an aspiring professional voice actor and can be super dramatic at times. I like buff dudes so... hit me up if you're one ;)", color=discord.Color.green())
        embed.add_field(name="Fav Support", value="Seraphine", inline=False)
        embed.add_field(name="Birthday", value="March 9th", inline=False)
        embed.set_thumbnail(url="https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-9/106453746_3452398688124582_8963541812202887666_n.jpg?_nc_cat=110&ccb=1-5&_nc_sid=09cbfe&_nc_ohc=_ug1rG3c9ggAX_jMAAi&_nc_ht=scontent-sjc3-1.xx&oh=8f729dc4b6a67147ef945a828855bda4&oe=61577A07")
        await ctx.send(embed=embed)
        
    @commands.command(name="royce",description="Explain Royce")
    async def royce_(self,ctx):
        embed=discord.Embed(title="About Royce",description="Hi I'm Royce, I'm either on apex legends, dead by daylight or at an 'appointment' :shushing_face:")
        embed.add_field(name="Fav Champion",value="Horizon",inline=False)
        embed.add_field(name="Birthday",value="August 11th",inline=False)
        embed.set_thumbnail(url="https://scontent-sjc3-1.xx.fbcdn.net/v/t1.6435-9/73006787_447636122534644_4737515091182747648_n.jpg?_nc_cat=103&ccb=1-5&_nc_sid=09cbfe&_nc_ohc=w0KhZNAM1S0AX_N19PL&_nc_ht=scontent-sjc3-1.xx&oh=4a323b8137cae06ea018d32184d13a82&oe=615744AB")
        await ctx.send(embed=embed)
        
    @commands.command(name="mark", description="Explain Mark")
    async def mark_(self,ctx):
        embed=discord.Embed(title="About Mark",description="Professional BM'er. Drives a civic")
        embed.add_field(name="Fav Champ",value="???",inline=False)
        embed.add_field(name="Birthday",value="",inline=False)
        embed.set_thumbail(url="https://scontent-sjc3-1.xx.fbcdn.net/v/t31.18172-8/26063634_1776578549042749_3190478789563495658_o.jpg?_nc_cat=106&ccb=1-5&_nc_sid=09cbfe&_nc_ohc=0OoN7rGePF4AX8DMYpO&_nc_ht=scontent-sjc3-1.xx&oh=6cef796ee8be576447e28b5f29f5cf65&oe=6158AB46")
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Miscellaneous(bot))
    
#     
#         embed=discord.Embed(title="",description="")
#         embed.add_field(name="",value="",inline=False)
#         embed.add_field(name="",value="",inline=False)
#         await ctx.send(embed=embed)