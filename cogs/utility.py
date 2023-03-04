import disnake
from disnake.ext import commands
import pytz
from datetime import datetime

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone('US/Eastern')
    
    @commands.slash_command(name="aqw-time")
    async def time(self, inter):
        """
        Check Server Time in AQW
        Parameters
        ----------
        
        """
        await inter.response.defer()
        current_date = datetime.now(self.timezone).strftime('%B %d, %Y')
        current_time = datetime.now(self.timezone).strftime('%H:%M:%S %Z')
        print(current_date)
        await inter.send(f"**AQW Date**: `{current_date}`\n**AQW Time**: `{current_time}`")
        

def setup(bot):
    bot.add_cog(Utility(bot))