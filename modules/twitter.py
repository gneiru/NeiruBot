import TwitterAPI as TApi
import asyncio
import re
from TwitterAPI import HydrateType
import datetime
import pytz
import json
from modules import dotenv

class Tweet:
    
    def __init__(self):
        self.text = None
        self.data = None
        self.id = None
        self.imgURL = None
        self.timestamp = None
        self.author = None
        TApi.TwitterOAuth.consumer_key = dotenv.consumer_key
        TApi.TwitterOAuth.consumer_secret = dotenv.consumer_secret
        TApi.TwitterOAuth.access_token_key = dotenv.access_token_key
        TApi.TwitterOAuth.access_token_secret = dotenv.access_token_secret
        self.o = TApi.TwitterOAuth
        # print(self.o.consumer_key)
        # print(self.o.consumer_secret)
        # print(self.o.access_token_key)
        # print(self.o.access_token_secret)
        self.api = TApi.TwitterAPI(self.o.consumer_key, self.o.consumer_secret, self.o.access_token_key, self.o.access_token_secret, api_version='2')

    def get_discord_timestamp(self, hours: int) -> int:
        tz = pytz.timezone("UTC")
        now = datetime.datetime.now(tz)
        now = datetime.datetime.now().timestamp()
        hours_in_seconds = hours * 60 * 60
        self.timestamp = int((now + hours_in_seconds))

    def regex(self, monster=False, boost=False):
        tweet_text = self.text.lower()
        if monster:
            monster_regex = re.compile(r"battle (?:the )?(.*?) in")
            map_regex = re.compile(r"in (?:the ) /(.*?) map")
            items_regex = re.compile(r"to (?:get|unlock) (.*?)(?: until|\.|!)")
            

            monster = re.search(monster_regex, tweet_text ).group(1)
            try:
                map = re.search(map_regex, tweet_text ).group(1)
            except Exception as e:
                map = "somewhere? map(word not specified)"
            items = re.search(items_regex, tweet_text ).group(1)
            
            if "until" in tweet_text:
                until_date_regex = re.compile(r"until (.*?)(?: to|\.|!)")
                until_date_match = re.search(until_date_regex, tweet_text).group(1)
                return f'**Monster:** {monster.title()}\n**Map:** /join {map}\n**Item(s):** {items.capitalize()}\n**Until: ** {until_date_match.capitalize()}'
                
            return f'**Monster:** {monster.title()}\n**Map:** /join {map}\n**Item(s):** {items.capitalize()}'
        if boost:
            match = re.search(r"Happening now: (\d+) hour (.*?)!", self.text)
            if match:
                hour = match.group(1)
                hour = int(hour)
                type = match.group(2)
            self.get_discord_timestamp(hour)
            return f'**Boost:** {type} \n**Duration:** {hour} Hours\n**End: **<t:{self.timestamp}:R>'
        
    # def getRecent(self, id=None):
    #     if id is None:
    #         return
        
    #     api = self.api
    #     params = {'max_results': 10, 'tweet.fields': 'created_at,text'}
    #     tweets = api.request(f'users/:{id}/tweets', params)
    #     tweet = [{"tweet": t['text'], "created_at": t['created_at'], "id": t['id']} for t in tweets if 'new reward, boost,' in t['text'].lower()][0]
        
    def process_tweet(self, dikc):
        tweetLowered = dikc['text'].lower()
        if "log in each day for a new" in tweetLowered:
            self.text = dikc['text']
            self.author = dikc['author_id_hydrate']
            self.id = dikc['id']
            self.imgURL = dikc['attachments']['media_keys_hydrate'][0]['url']
            if "battle" in tweetLowered and ("get" in tweetLowered or "collect" in tweetLowered):
                data = self.regex(monster = True)
            elif "happening now" in tweetLowered and ('double' in tweetLowered or 'triple' in tweetLowered):
                data = self.regex(boost = True)
            # print(
            #     {
            #         "url": f"https://twitter.com/{self.author['username']}/status/{self.id}",
            #         "tweetID": self.id,
            #         "description": data,
            #         "author": self.author['name'],
            #         "author_icon_url": self.author['profile_image_url']
            #     }
            # )
            self.data =  {
                "url": f"https://twitter.com/{self.author['username']}/status/{self.id}",
                "tweetID": self.id,
                "description": data,
                "author": self.author['name'],
                "author_icon_url": self.author['profile_image_url'],
                "image_url": self.imgURL
            }
        # for t in tweets:
            
        #     print(t)
        #     tweet = t['text'].lower()
        #     self.created_at = t['created_at']
        #     self.id = t['id']
        #     if not t['text'].startswith('RT @'):
        #         if "new reward, boost," in tweet:
        #             self.text = t['text']
        #             if "happening now" in tweet and ('double' in tweet or 'triple' in tweet):
        #                 print("new double or triple boost")
        #                 data = self.regex(boost = True)
        #             if "battle" in tweet and ("get" in tweet):
        #                 data = self.regex(monster = True)
        #                 print("new monster daily drop")
        #             self.data =  {
        #                     "url": f"https://twitter.com/{id}/status/{t['id']}",
        #                     "tweetID": t['id'],
        #                     "description": data,
        #                 }
        #             return

    def lookup_tweet(self, id):
        if id is None:
            TWEET_ID = self.id
        TWEET_ID = id
        EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
        MEDIA_FIELDS = 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics'
        TWEET_FIELDS = 'created_at,author_id,public_metrics,context_annotations,entities'
        USER_FIELDS = 'location,profile_image_url,verified'

        api = self.api
        r = api.request(f'tweets/:{TWEET_ID}', 
            {
                'expansions': EXPANSIONS,
                'tweet.fields': TWEET_FIELDS,
                'user.fields': USER_FIELDS,
                'media.fields': MEDIA_FIELDS,
            }, 
            hydrate_type=HydrateType.APPEND)

        for item in r:
            # print(json.dumps(item))
            self.process_tweet(item)
            
            # self.imgURL = item['entities']['urls'][1]['media_key_hydrate']['url']
    # def lookup_user(self, userid):
    #     api = self.api
    #     r = api.request(f'users/by/username/:{userid}')

    #     for item in r:
    #         print(item)

    #     print(r.get_quota())
        
async def doStuffs():
    c = Tweet()
    c.lookup_tweet(1621878744880144385)
    print(c.data)
    
if __name__ == "__main__":
    asyncio.run(doStuffs())