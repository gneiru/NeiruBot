import random
import asyncio
from modules.variables import coin
from modules.database import database as db
from modules.variables import Points

collection = db.challenges

class challenge:
    def __init__(self, challenge=None, items=None, reward=None, difficulty=None):
        self.challenge = challenge
        self.items = items
        self.reward = reward
        self.difficulty = difficulty
        self.completedList = None
        self.allDone = False

    async def get(self, current):
        filter = {'name': current} 
        doc = collection.find_one(filter)
        self.challenge = doc['name']
        self.items = doc['items']
        self.reward = doc['reward']
        self.difficulty = doc['difficulty']
    
    def getCompletedList(self, playerID = None)-> list:
        userChal = db.user_challenges
        if playerID is not None:
            chal = userChal.find_one({'player': playerID})
            if chal is not None:
                return chal['completed']
            else:
                return None
    
    def getAllChallenge(self):
        docs = collection.find({})
        return [doc['name'] for doc in docs]
    
    async def random(self, playerID=None):
        # generate a random challenge that is not completed by player
        filter = {} 
        
        if playerID:
            self.completedList = self.getCompletedList(playerID)
            if self.completedList:
                filter = {'name': {'$nin': self.completedList}}
            
        docs = collection.find(filter)
        try:
            doc = random.choice(list(docs))
        except IndexError:
            self.allDone = True
            return print(f"Player {playerID} has completed all challenges")
        self.challenge = doc['name']
        self.items = doc['items']
        self.reward = doc['reward']
        self.difficulty = doc['difficulty']
    
    async def check_items(self, itemList, challengeList):
        challenges = challengeList
        reqArray = []
        for challenge in challenges:
            found_item = [i for i in itemList if i['itemName'] == challenge['name']]
            quantity_is_met = False
            if found_item:
                item_quantity = found_item[0]['quantity']
                challenge_quantity = challenge['quantity']
                if item_quantity >= challenge_quantity:
                    quantity_is_met = True
                else:
                    quantity_is_met = False
                reqArray.append({'challenge': challenge["name"], 'value': f'{item_quantity}/{challenge_quantity}', 'reqMet': quantity_is_met})

            else:
                quantity_is_met = False
                reqArray.append({'challenge': challenge["name"], 'value': f'0/{challenge["quantity"]}', 'reqMet': quantity_is_met})
        # return print(reqArray)
        return reqArray

class player:

    def __init__(self, name=None, guild=None, ccid=None, discordID=None):
        self.response = None
        self.name = name
        self.guild = guild
        self.ccid = ccid
        self.discordID = discordID
        self.isRegistered = None
        self.balance = None
        self.current = None
        self.compeleted = None

    async def register(self, force=False):
        collection = db.players
        filter = { "discordID": self.discordID }
        player = collection.find_one(filter)
        if player and force is False:
            self.response = f"<@{self.discordID}>'s player name is updated to `{self.name}`"
            collection.update_one(filter, {"$set": { "name": self.name}})
            return
        new_values = {"$set": { "name": self.name, "guild": self.guild, "ccid": self.ccid, "discordID": self.discordID , "balance": 0, "difficulty_completed": {"D": 0, "C": 0, "B": 0, "A": 0, "S": 0, "M": 0}} }
        result = collection.update_one(filter, new_values, upsert=True)
        if result.modified_count:
            self.response = f'Player has been updated into `{self.name}`\n**New Balance: **0\nCompleted Challenges Resetted.'
        else:
            self.response = f'Player `{self.name}` has been registered.'
            
    def checkPlayerRegistration(self):
        collection = db.players
        filter = { "discordID": self.discordID }
        players = collection.find(filter)
        if len(players) == 0:
            self.isRegistered = False
            self.response = f'Player `{self.name}` is not yet registered.'
        else:
            self.isRegistered = True
            self.ccid = players[0]['gameID']
            self.name = players[0]['name']
            self.guild = players[0]['guild']

    async def getID(self):
        collection = db.players
        filter = { "discordID": self.discordID }
        players = collection.find(filter)
        return players[0]['ccid']

    async def getPlayerList(self):
        collection = db.players
        players = collection.find({})
        playerList = [player['discordID'] for player in players]
        return playerList
    
    async def getRankings(self, type="Coin"):
        collection = db.players
        if type == "Coin":
            docx = collection.find().sort("balance",-1)
            return [{'name': doc['name'], 'balance': doc['balance'], 'difficulty_completed': doc['difficulty_completed']} for doc in docx]
            
        elif type == "Challenge":
            points = Points
            documents = list(collection.find())
            for doc in documents:
                doc["total_points"] = sum(points[key] * value for key, value in doc["difficulty_completed"].items())
            documents.sort(key=lambda x: x["total_points"], reverse=True)
            return [{'name': doc['name'], 'total_points': doc['total_points'], 'difficulty_completed': doc['difficulty_completed']} for doc in documents]
            
    
    async def getPlayerData(self):
        collection = db.players
        filter = { "discordID": self.discordID }
        player = collection.find_one(filter)
        self.name = player['name']
        self.guild = player['guild']
        self.ccid = player['ccid']
        self.discordID = player['discordID']

    async def updatePlayer(self, reward):
        collection = db.players
        filter = { "discordID": self.discordID }
        player = collection.find_one(filter)
        self.name = player['name']
        if player and 'balance' in player:
            balance = player['balance'] + reward
            update = {"$set": {"balance": balance}}
            result = collection.update_one(filter, update)
            if result.modified_count:
                sign = "+" if reward > 0 else ""
                self.response = f'**IGN: **{self.name}\n {sign}{reward} {coin}'
                self.balance = balance
            else:
                self.response = f'An error occurred while updating player balance.'
        elif 'balance' not in player:
            update = {"$set": {"discordID": self.discordID, "balance": reward}}
            result = collection.update_one(filter, update, upsert=True)
            if result.modified_count or result.upserted_id:
                self.response = f'**IGN: **{self.name}'
                self.balance = reward
            else:
                self.response = f'An error occurred while setting player balance.'
        
    async def updateCompletedChallenge(self, completed):
        playerID = self.discordID
        docs = db.user_challenges
        player = docs.find_one({'player':playerID})
        if player:
            docs.update_one({"player":playerID}, {'$push': {'completed': completed}})
        else:
            docs.insert_one({"player":playerID})
            docs.update_one({"player":playerID}, {'$push': {'completed': completed}})
    
    async def resetAllCompleted(self):
        docs = db.user_challenges
        result = docs.find()
        if len(list(result)) != 0:
            docs.delete_many({})
            self.response = "Reseted all completed challenges."
        else:
            self.response = "There are no completed challenges"

    async def updateFinishedDifficulty(self, difficulty):
        playerID = self.discordID
        filter = {"discordID":playerID}
        docs = db.players
        doc = docs.find_one(filter)
        diffCount = doc['difficulty_completed'].get(difficulty, 0)
        diffCount = diffCount + 1
        docs.update_one(filter, {'$set': {f'difficulty_completed.{difficulty}': diffCount }})

    async def getPlayerBalance(self):
        collection = db.players
        filter = { "discordID": self.discordID }
        player = collection.find_one(filter)
        if player and 'balance' in player:
            return player['balance']
        elif 'balance' not in player:
            return 0
    
    #TODO: Make a db and methods for shops and inventory items
    
    async def getCurrentChallenge(self, discordID=None):
        if discordID is None:
            discordID = self.discordID
        collection = db.players
        filter = { "discordID": discordID }
        player = collection.find_one(filter)
        if player and 'current' in player:
            self.current =  player['current']

    async def updateCurrent(self, current=None):
        if current is None:
            current = self.current
        collection = db.players
        filter = { "discordID": self.discordID }
        update = { '$set': { 'current': current}}
        collection.update_one(filter, update)

class ultra:
    def __init__(self):
        self.boss = None
    
    def random(self):
        # generate a random challenge that is not completed by player
        docs = db.bosses.find({})
        doc = random.choice(list(docs))
        return doc
    

async def doStuffs():
    c = challenge()
    await c.random()

if __name__ == "__main__":
    asyncio.run(doStuffs())
    
    # itemList = [{'itemName': 'Arachnomancer', 'quantity': 1}, {'itemName': 'ArchPaladin', 'quantity': 1}, {'itemName': 'Chaos Avenger', 'quantity': 1}, {'itemName': 'Chronomancer Prime', 'quantity': 1}, {'itemName': 'Dragon of Time', 'quantity': 1}, {'itemName': 'Legion Revenant', 'quantity': 1}, {'itemName': 'LightCaster', 'quantity': 1}, {'itemName': 'Lord Of Order', 'quantity': 1}, {'itemName': 'Quantum Chronomancer', 'quantity': 1}, {'itemName': 'Shaman', 'quantity': 1}, {'itemName': 'StoneCrusher', 'quantity': 1}, {'itemName': 'Void Highlord', 'quantity': 1}, {'itemName': 'Warrior', 'quantity': 1}, {'itemName': 'Yami no Ronin', 'quantity': 1}, {'itemName': 'Academy Uniform', 'quantity': 1}, {'itemName': 'Awescended', 'quantity': 1}, {'itemName': "Delinquent Leader's Garb", 'quantity': 1}, {'itemName': 'Ducky Naval Commander', 'quantity': 1}, {'itemName': 'EbilCorp Standard Player', 'quantity': 1}, {'itemName': "Fire Champion's Armor", 'quantity': 1}, {'itemName': 'Hollowborn DoomKnight', 'quantity': 1}, {'itemName': 'Hollowborn Envoy of Chaos', 'quantity': 1}, {'itemName': 'Infernal Flame Pyromancer', 'quantity': 1}, {'itemName': 'Pretty Sailor Mate', 'quantity': 1}, {'itemName': "Delinquent's Glasses + Locks Morph", 'quantity': 1}, {'itemName': "Dragonsworn Commander's Morph + Locks", 'quantity': 1}, {'itemName': 'Hollowborn Chaos Morph', 'quantity': 1}, {'itemName': "NightStalker's Locks", 'quantity': 1}, {'itemName': 'Sassy Melon Locks', 'quantity': 1}, {'itemName': "Shadow BoogieMan's Mask", 'quantity': 1}, {'itemName': 'Underworld ArchFiend Shade', 'quantity': 1}, {'itemName': 'Chaos Dragon Flames', 'quantity': 1}, {'itemName': "Elegant Siren's Tail", 'quantity': 1}, {'itemName': 'Eternal Flame of Loyalty', 'quantity': 1}, {'itemName': 'Fiendish Eternal Flame', 'quantity': 1}, {'itemName': 'Pretty Eternal Flame', 'quantity': 1}, {'itemName': 'Sugar-Sweet Wings', 'quantity': 1}, {'itemName': 'Yokai Oni Aura', 'quantity': 1}, {'itemName': 'Derpblivion Blade', 'quantity': 1}, {'itemName': "Empowered Chaos Avenger's Greatsword", 'quantity': 1}, {'itemName': 'Exalted Apotheosis', 'quantity': 1}, {'itemName': 'Fest-EBIL Katana', 'quantity': 1}, {'itemName': 'Hollowborn Sword of Doom', 'quantity': 1}, {'itemName': 'Necrotic Blade of Doom', 'quantity': 1}, {'itemName': 'Necrotic Blade of the Underworld', 'quantity': 1}, {'itemName': 'Necrotic Sword of Doom', 'quantity': 1}, {'itemName': 'Sin of the Abyss', 'quantity': 1}, {'itemName': 'Dual Exalted Apotheosis', 'quantity': 1}, {'itemName': 'High Formal Cane', 'quantity': 1}, {'itemName': 'Providence', 'quantity': 1}, {'itemName': 'Pink Quibble Bank Pet', 'quantity': 1}, {'itemName': 'Polly Roger', 'quantity': 1}, {'itemName': 'Endurance Draught', 'quantity': 80}, {'itemName': 'Fate Tonic', 'quantity': 287}, {'itemName': 'Potent Battle Elixir', 'quantity': 290}, {'itemName': 'Potent Destruction Elixir', 'quantity': 292}, {'itemName': 'Potent Honor Potion', 'quantity': 266}, {'itemName': 'Potent Malevolence Elixir', 'quantity': 292}, {'itemName': 'Potent Malice Potion', 'quantity': 295}, {'itemName': 'Potent Revitalize Elixir', 'quantity': 283}, {'itemName': 'Sage Tonic', 'quantity': 286}, {'itemName': 'Scroll of Enrage', 'quantity': 28}, {'itemName': 'Super-Fan Swag Token B', 'quantity': 44}, {'itemName': 'Treasure Potion', 'quantity': 292}, {'itemName': 'Unstable Malevolence Elixir', 'quantity': 292}, {'itemName': 'Zealous Ink', 'quantity': 13}, {'itemName': 'Insatiable Hunger', 'quantity': 1}, {'itemName': 'Treasure Chest', 'quantity': 250}, {'itemName': 'Gold Voucher 100k', 'quantity': 300}, {'itemName': 'Gold Voucher 500k', 'quantity': 272}, {'itemName': 'Northlands Getaway House', 'quantity': 1}, {'itemName': 'Skull Island House of DOOM', 'quantity': 1}, {'itemName': 'Summer Night', 'quantity': 1}, {'itemName': 'Holiday Party Piggy Guard', 'quantity': 6}, {'itemName': 'Arctic Fox Guard', 'quantity': 6}, {'itemName': 'Arctic Fox Guard At Rest', 'quantity': 6}, {'itemName': 'BlightStalker Guard (R)', 'quantity': 1}, {'itemName': 'Chaos Portal', 'quantity': 1}, {'itemName': 'Hollowborn Blade of Chaos (Floor)', 'quantity': 1}, {'itemName': 'Kitty Yu-Yule Guard', 'quantity': 6}, {'itemName': 'Twig & Forest Friends', 'quantity': 8}]
    # c.check_items(itemList)