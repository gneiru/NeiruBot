from bs4 import BeautifulSoup as bts
import requests
import re
import asyncio
from datetime import datetime
import json
import pytz
class events:
    def __init__(self):
        self.timezone = pytz.timezone('US/Eastern')
        self.eventList = None
        self.content = None
        self.timestamp = None
        self.soup = None
        self.what = None
        self.boostHours = 48
        self.imgURL = "https://artix.com/media/1077/ae_mainbanner.jpg"
        
    def get_discord_timestamp(self, hours: int) -> int:
        now = datetime.now(self.timezone)
        now = datetime.now(self.timezone).timestamp()
        hours_in_seconds = hours * 60 * 60
        self.timestamp = int((now + hours_in_seconds))
    
    def regex(self, monster: bool = False, boost: bool = False):
        
        if monster:
            return self.content.split("Log in")[0]
            # children = (self.soup.find('div', {'class': 'newsPost'}).findChildren())
            # for i, child in enumerate(children, start=1):
            #     print(f"{i}. {child}")
            # monster = self.soup.find('span', {'class': 'css-901oao'}).find('span').text
            # mapAndReward = self.soup.find('span', {'class': 'css-901oao'}).text.strip().replace(monster, '')
            # getListForMap = mapAndReward.split('map')
            # map = getListForMap[0].split("the /")[1]
            # items = getListForMap[1].split("get")[1]
            # match = re.search(r'\d.+?(?=(\.|Log))', items)
            # matched_text = match.group().replace('AC', 'AC ') if match else ''
            # items = (matched_text.strip())

            
            # if "leave" in text:
            #     date = self.soup.select('em')[0].text.strip().split("leave ")[1].capitalize()
            #     return f'**Monster:** {monster.title()}\n**Map:** /join {map}\n**Item(s):** {items}\n**Until: ** {date.capitalize()}'
                
            # return f'**Monster:** {monster.title()}\n**Map:** /join {map}\n**Item(s):** {items}'
        
        if boost:
            
            matches = re.findall(r'(\d+)', self.content)
            self.boostHours = int(next((match for match in matches if int(match) in [24, 48, 72, 96]), 48))
            self.get_discord_timestamp(self.boostHours)
            return f'**Boost:** {self.what} \n**Duration:** {self.boostHours} Hours\n**End: **<t:{self.timestamp}:R>'
        
    async def get_urls(self):
        URL = "https://artix.com/calendar"
        response = requests.get(URL)
        # print(response.text)
        soup = bts(response.text, "html.parser")
        scripts = soup.find_all("script")
        script = scripts[14]
        script_content = script.text
        events_pattern = r"events: \[(.*)\]"
        events_match = re.search(events_pattern, script_content, re.DOTALL)
        date_events = (events_match.group(1).replace("' + '", ''))
        # regular expression pattern to match the URL and start date
        pattern = r"url:\s*'([^']*)',\s*start:\s*'(\d{4}-\d{2}-\d{2})'"

        # get the current date in the format "Y-m-d"
        current_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        print(current_date)
        current_date = '2023-03-26'

        # loop over all matches and extract URLs with the current date
        matches = re.findall(pattern, date_events)
        urls = [match[0] for match in matches if match[1] == current_date]

        # print the matching URLs
        return urls
    
    async def process_url(self, url):
        response = requests.get(url)
        soup = bts(response.text, "html.parser")
        self.soup = soup
        div = soup.select_one('div.newsPost')
        self.what = div.select_one('h1').text
        self.content = div.text
        img = div.select_one('img')
        if img:
            self.imgURL = f"https://artix.com{img['src']}"
        lowercase_content = self.content.lower()
        if "log in each day for a new" in lowercase_content:
            if "battle" in lowercase_content and ("get" in lowercase_content or "collect" in lowercase_content):
                data = self.regex(monster = True)
                return {
                    'title': "New Daily Gift",
                    "url": url,
                    "description": data,
                    "image_url": self.imgURL
                }
            elif 'Double' in self.what or 'Triple' in self.what or 'boost' in self.what.lower():
                data = self.regex(boost = True)
                return {
                    'title': "New Daily Boost",
                    "url": url,
                    "description": data,
                    "image_url": self.imgURL
                }
            # print(
            #     {
            #         "url": f"https://twitter.com/{self.author['username']}/status/{self.id}",
            #         "tweetID": self.id,
            #         "description": data,
            #         "author": self.author['name'],
            #         "author_icon_url": self.author['profile_image_url']
            #     }
            # )
            
class account:
    def __init__(self, name= None, user_id=None, discord_id=None):
        self.name = name # required
        self.user_id = user_id
        self.discord_id = discord_id
        self.status = None
        self.isClean = None
        self.items = None
        self.itemCount = None

    async def soup(self, id=None):
        if not id:
            ign = self.name.replace(" ", "%20")
            URL = f"https://account.aq.com/CharPage?id={ign}"
            r = requests.get(URL)
            return bts(r.content, 'html.parser')
            
        elif id:
            URL = f"https://account.aq.com/CharPage/Inventory?ccid={id}"
            r = requests.get(URL)
            return r.json()

    async def check(self):
        soup = await self.soup()
        notFound = soup.select_one("#serveralert")
        textstat = soup.select_one('.card-body p s')
        if notFound:
            self.status = notFound.text
            self.isClean = False
        elif textstat:
            self.isClean = False
            self.status = textstat.text
        else:
            self.isClean = True
        # GET GUILD
        try:
            string1 = soup.findAll('div', {'class': 'col-12 col-md-6'})[1]
            s = string1.findAll('label')
            self.guild =  [(lab.next_sibling).strip() for lab in s if lab.next_element == "Guild:"][0]
        except:
            self.guild = None

        # GET ID
        ccIDFound = re.search(r'ccid = (\d+)', str(soup))
        if ccIDFound:
            ccid = ccIDFound.group(1).strip()
            self.user_id = int(ccid)
    
    async def getItems(self, id=None):
        if id is None:
            id = self.user_id
        soupID = await self.soup(id)
        # self.items =  [{"itemName": item["strName"], "quantity": 1 if item["intCount"] == 302500 else item["intCount"]} for item in soupID]
        # self.itemCount = len(self.inventory.items)
        return [{"itemName": item["strName"], "quantity": 1 if item["intCount"] == 302500 else item["intCount"]} for item in soupID]

    async def getClasses(self, id=None):
        if id is None:
            id = self.user_id
        soupID = await self.soup(id)
        # self.items =  [{"itemName": item["strName"], "quantity": 1 if item["intCount"] == 302500 else item["intCount"]} for item in soupID]
        # self.itemCount = len(self.inventory.items)
        return [item["strName"] for item in soupID if item["strType"] == "Class"]

async def doStuffs():
    ev = events()
    urls = await ev.get_urls()
    for url in urls:
        dicx = await ev.process_url(url)
        print(dicx)

if __name__ == "__main__":
    asyncio.run(doStuffs())