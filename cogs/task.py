from disnake.ext import commands, tasks
import disnake
from modules.aqw import events
from modules.database import aqwDB as db
import modules.variables as vaR
import requests
import pytz
from datetime import datetime

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
            
            # async for msg in channel.history(limit=3):
            #     if "Alina_AE/status/" in msg.content or "YoshinoAE/status/" in msg.content:
            #         m = msg.content.split("/status/")
            #         id = int(m[1])
            #         res = db.tweets.find_one({'tweetID': f"{id}" })
            #         if not res:
            #             tsk = Tweet()
            #             tsk.lookup_tweet(id) # Twitter ID
            #             if tsk.data:
            #                 dicx = tsk.data
            #                 db.tweets.insert_one(dicx)
            #                 embed = disnake.Embed()
            #                 embed.set_image(url = dicx['image_url'])
            #                 if "Monster" in dicx['description']:
            #                     embed.title = 'New Daily Gift'
            #                 else:
            #                     embed.title = 'New Boost'
            #                 embed.description = dicx['description']
            #                 embed.url = dicx['url']
            #                 embed.colour = disnake.Color.dark_blue()
            #                 embed.set_author(name=dicx['author'], icon_url=dicx['author_icon_url'])
            #                 receiverChannel = self.bot.get_channel(vaR.Gifts['channel'])
            #                 await receiverChannel.send(content = f"||<@&{vaR.Gifts['role']}>||" , embed = embed)
            
            # Set timezone to UTC
            tz = pytz.timezone('UTC')
            now = datetime.now(tz)
            
            
            # if now.hour != 5 and now.minute != 0 or now.minute != 1: # 5th hour is server daily reset
            if now.hour == 5 and (now.minute == 0 or now.minute == 1):
                ev = events()
                urls = await ev.get_urls()
                for url in urls:
                    res = db.events.find_one({'url': f"{url}" })
                    if not res:
                        dicx = await ev.process_url(url)
                        if dicx:
                            db.events.insert_one(dicx)
                            embed = disnake.Embed()
                            embed.title = dicx['title']
                            embed.description = dicx['description']
                            embed.url = dicx['url']
                            embed.colour = disnake.Color.dark_blue()
                            embed.set_image(url=dicx['image_url'])
                            receiverChannel = self.bot.get_channel(vaR.Gifts['channel'])
                            await receiverChannel.send(content = f"||<@&{vaR.Gifts['role']}>||" , embed = embed)
                    else:
                        print("This embed already sent")
            # else:
            #     return print(f"Current hour: {now.hour} \nNot yet 1:00 to 1:01pm")
        except Exception as e:
            print(e)
        
    @tweet_task.before_loop
    async def b4_tweet_task(self):
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(Task(bot))

