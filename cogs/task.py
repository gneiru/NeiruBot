from disnake.ext import commands, tasks
import disnake
from modules.twitter import Tweet
from modules.database import twtDB as db
import modules.variables as vaR
import requests

class Task(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tweet_task.start()
    
    def cog_unload(self):
        self.tweet_task.cancel()

    @tasks.loop(seconds=15)  # task runs every 15 seconds
    async def tweet_task(self):
        
        channel = self.bot.get_channel(vaR.NewsChannel)
                
        try:
            response = requests.get('https://game.aq.com/game/api/data/servers')
            server_list = response.json()
            total_players = [server["iCount"] for server in server_list]
            activity = disnake.Activity(name=f"AQW with {sum(total_players)} players", type=disnake.ActivityType.playing)
            await self.bot.change_presence(status=disnake.Status.idle, activity = activity)
            
            async for msg in channel.history(limit=3):
                if "Alina_AE/status/" in msg.content or "YoshinoAE/status/" in msg.content:
                    m = msg.content.split("/status/")
                    id = int(m[1])
                    res = db.tweets.find_one({'tweetID': f"{id}" })
                    if not res:
                        tsk = Tweet()
                        tsk.lookup_tweet(id) # Twitter ID
                        if tsk.data:
                            dicx = tsk.data
                            db.tweets.insert_one(dicx)
                            embed = disnake.Embed()
                            embed.set_image(url = dicx['image_url'])
                            if "Monster" in dicx['description']:
                                embed.title = 'New Daily Gift'
                            else:
                                embed.title = 'New Boost'
                            embed.description = dicx['description']
                            embed.url = dicx['url']
                            embed.colour = disnake.Color.dark_blue()
                            embed.set_author(name=dicx['author'], icon_url=dicx['author_icon_url'])
                            receiverChannel = self.bot.get_channel(vaR.Gifts['channel'])
                            await receiverChannel.send(content = f"||<@&{vaR.Gifts['role']}>||" , embed = embed)
        except Exception as e:
            print(e)
        
    @tweet_task.before_loop
    async def b4_tweet_task(self):
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(Task(bot))

