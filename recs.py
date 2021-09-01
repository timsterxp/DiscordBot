import discord
from discord.ext import commands

class Recommendations(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="food", aliases=["foodspots","noms"], description= "Recommended Food Spots Around The Bay")   
    async def food_(self,ctx):
        embed = discord.Embed(title="Food Spots", description="", color=discord.Color.green())
        embed.add_field(name='Daeho Kalbijjim & Beef Soup', value="Serves tender short ribs with options of cheese/ox tail. https://www.yelp.com/biz/daeho-kalbi-jjim-and-beef-soup-milpitas", inline=False)
        embed.add_field(name='Gyu-Kaku', value="JBBQ with extensive menu (Better than Gen/QPot) https://www.yelp.com/biz/gyu-kaku-japanese-bbq-cupertino", inline=False)
        embed.add_field(name='Boiling Point', value="Taiwanese Hotpot with emphasis on Korean Bean Paste/Spice levels https://www.yelp.com/biz/boiling-point-san-jose", inline=False)
        embed.add_field(name='Cha Cha sushi', value="OG Bay Area Sushi Go-to spot https://www.yelp.com/biz/cha-cha-sushi-san-jose", inline=False)
        await ctx.send(embed=embed)
        
        
    @commands.command(name="boba", description= "Recommended Boba Spots Around The Bay")
    async def boba_(self,ctx):
        embed=discord.Embed(title="Boba Recommendations", color=discord.Color.green())
        embed.add_field(name='Mr.Sun',value='In-house made boba(Strawberry/Mango/Brown Sugar) w/ Seasonal(Grape/Passion Fruit) Boba https://www.yelp.com/biz/mr-sun-tea-cupertino-2',inline=False)
        embed.add_field(name='TeaZen Tea',value='Consistent Drinks, new unique flavors https://www.yelp.com/biz/teazentea-san-jose-san-jose-5',inline=False)
        embed.add_field(name='Tea Yomi',value='Fresh fruits guaranteed, Smoothies best in the area (P.S. Get the cherry smoothie) https://www.yelp.com/biz/tea-yomi-milpitas',inline=False)
        embed.add_field(name='Tisane',value='For the usual pick me up sweet milk teas https://www.yelp.com/biz/tisane-san-jose',inline=False)
        embed.add_field(name='Boba Bliss',value='IG-Worthy Drinks although a bit of a drive https://www.yelp.com/biz/boba-bliss-dublin-3',inline=False)
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Recommendations(bot))