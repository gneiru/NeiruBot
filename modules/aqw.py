from bs4 import BeautifulSoup as bts
import requests
import re
import asyncio
import datetime
import json
class events:
    def __init__(self, eventList: list= None):
        self.eventList = eventList
        
    async def get_scripts(self):
        URL = "https://artix.com/calendar"
        response = requests.get(URL)
        # print(response.text)
        soup = bts(response.text, "html.parser")
        scripts = soup.find_all("script")
        script = scripts[14]
        script_content = script.text
        events_pattern = r"events: \[(.*)\]"
        events_match = re.search(events_pattern, script_content, re.DOTALL)
        if events_match:
            events_string = events_match.group(1)
            events_string = events_string.replace("' + '", '')
            events_string = events_string.replace("title", '"title"')
            events_string = events_string.replace("url", '"url"')
            events_string = events_string.replace("start", '"start"')
            events_string = events_string.replace("end", '"end"')
            events_string = events_string.replace("'", '"')
            events_string = events_string.replace('cal"end"ar', 'calendar')
            # further processing of events_string can be done here
            print(events_string)
            s = eval(f"[{events_string}]")
            print(json.loads(s))
        # script = soup.find('script', text=lambda t: 'events:' in t)
        # if script:
        #     start = script.text.index("events: [") + len("events: [")
        #     end = script.text.rindex("}]});")
        #     events_string = script.text[start:end]
        #     events = eval(events_string)
        #     print(events)
        # print(soup)
        # else:
        #     print("No events found.")
    
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
    c = events()
    await c.get_scripts()

if __name__ == "__main__":
    asyncio.run(doStuffs())