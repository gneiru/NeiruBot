import disnake
from disnake.ext import commands
from modules import mongo
from modules import variables

class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command()
    async def leaderboard(inter: disnake.ApplicationCommandInteraction, type: str = commands.Param(choices=['Coin', 'Challenge'], default='Coin')):
        """
        View Leaderboard
        Parameters
        ----------
        type : Leaderboard Type
        """
        await inter.response.defer(ephemeral=False)
        embed = disnake.Embed()
        p = mongo.player()
        if type == 'Coin':
            ldb = await p.getRankings()
            for idx , ld in enumerate(ldb, 1):
                embed.add_field(name=f"{idx}. {ld['name']}", value=f"{ld['balance']} {variables.coin}" )
        elif type == 'Challenge':
            ldb = await p.getRankings(type="Challenge")
            for idx, ld in enumerate(ldb):
                #val = " ".join(f"{value}x {getattr(variables, key)}" for key, value in ld['difficulty_completed'].items() if value !=0)
                val = " ".join(f"{value}x {variables.RankIcons[key]}" for key, value in ld['difficulty_completed'].items() if value !=0)
                embed.add_field(name=f"{idx + 1}. {ld['name']} - {ld['total_points']}", value=val, inline=False)
        embed.title = f'{type} Leaderboard'
        embed.set_thumbnail(url= str(inter.guild.icon))
        await inter.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(Leaderboard(bot))