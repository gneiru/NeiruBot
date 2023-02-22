import disnake
from disnake.ext import commands
import asyncio
class OnStart(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        act = [disnake.Activity(name="Bot Restart", type=disnake.ActivityType.listening),disnake.Activity(name="AQW", type=disnake.ActivityType.playing)]
        await self.bot.change_presence(status=disnake.Status.dnd, activity = act[0])
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        
        await asyncio.sleep(15)
        await self.bot.change_presence(status=disnake.Status.idle, activity = act[1])

def setup(bot):
    bot.add_cog(OnStart(bot))