import discord
from discord.ext import commands

class Miscellaneous(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        
        
    @commands.command(name="ivan", aliases="owner", description = "Explain Ivan")
    async def ivan_(self,ctx):
        embed = discord.Embed(title="About Ivan", description="I'm Ivan, I'm a giant weeb,talk to me about anime or manga :]", color=discord.Color.green())
        embed.add_field(name="Fav Jungler", value="Kayn", inline=False)
        embed.add_field(name="Birthday", value="July 22nd", inline=False)
        embed.add_field(name="Weeb?", value="Very much so", inline=False)
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Miscellaneous(bot))