import asyncio
from modules import mongo, aqw, variables
import disnake
from anime_api.apis import AnimechanAPI

class quest:
    def __init__(self, playerID: int, challenge=None, inventory=None, embed=None):
        self.challenge = challenge
        self.inventory = inventory
        self.embed = embed
        self.playerID = playerID
        self.aqwID = None
        self.account = None
        self.player = None
        self.quote = None
    
    async def loadPlayer(self, ccid = None):
        self.aqwID = ccid
        self.player = mongo.player(discordID = self.playerID)
        if self.aqwID is None:
            self.aqwID = await self.player.getID()
        self.account = aqw.account(user_id = self.aqwID)
        self.inventory = await self.account.getItems(self.aqwID)
    
    async def loadChallenge(self, rr = True):
        self.challenge = mongo.challenge()
        if rr == False:
            await self.player.getCurrentChallenge(self.playerID)
            if not self.player.current:
                await self.challenge.random(playerID = self.playerID)
                
            elif self.player.current:
                await self.challenge.get(self.player.current)
        else:
            await self.challenge.random(playerID = self.playerID)
        
    async def givenChallenge(self, challenge):
        self.challenge = mongo.challenge()
        await self.challenge.get(challenge)      
    
    async def construct(self, quotate=True, done=False):
        self.embed = disnake.Embed()
        if done:
            self.embed.title = "Congratulations"
            self.embed.description = "You have completed all the challenges"
            self.embed.color = disnake.Color.blurple()
            return
        
        requirements = await self.challenge.check_items(self.inventory,self.challenge.items)
        
        self.embed.title = self.challenge.challenge
        
        if self.quote is None:
            api = AnimechanAPI()
            quote = api.get_random_quote()
            self.quote = quote
        if quotate is False:
            self.quote.quote = "Random quote"
            self.quote.character = "Random person"
        self.embed.description = f"{self.quote.quote} \n**- {self.quote.character}\n\nReward: {self.challenge.reward}** {variables.coin}"

        if self.challenge.difficulty in variables.RankImgLink:
            url = variables.RankImgLink[self.challenge.difficulty]
            self.embed.set_thumbnail(url=url)

        for item in requirements:
            self.embed.add_field(name=item['challenge'], value=item['value'], inline=False)
        if any(item['reqMet'] == False for item in requirements):
            self.embed.color = disnake.Color.red()
        else:
            self.embed.color = disnake.Color.green()
    
    async def roll(self):
        await self.loadPlayer()
        await self.loadChallenge(rr=False)
        if self.challenge.allDone:
            return await self.construct(done=True)
        await self.player.updateCurrent(self.challenge.challenge)
        await self.construct()

    async def reroll(self):
        await self.loadPlayer()
        await self.loadChallenge()
        if self.challenge.allDone:
            return await self.construct(done=True)
        await self.player.updateCurrent(self.challenge.challenge)
        await self.construct()
        
    async def preview(self, challenge): #used by /preview
        await self.loadPlayer(ccid=73424816)
        await self.givenChallenge(challenge)
        await self.construct(quotate=False)
        
    async def turn_in(self):
        desc = f"Congratulations! \n +**{self.challenge.reward}** {variables.coin}"
        completedList = self.challenge.getCompletedList(self.playerID)
        if completedList is None:
            completedList = []
        if self.challenge.challenge not in completedList:
            await self.player.updatePlayer(self.challenge.reward)
            await self.player.updateCompletedChallenge(self.challenge.challenge)
            await self.player.updateFinishedDifficulty(self.challenge.difficulty)
            await self.player.updateCurrent(None)
            self.embed.description = f"{desc}\n**New Balance:** {self.player.balance} {variables.coin}"
        else:
            self.embed.description = f"You already completed this challenge, thankyou!"
        self.embed.clear_fields()

    async def reload(self):
        
        await self.loadPlayer()
        await self.construct()

async def doStuffs():
    c = quest(666483486735073312)
    await c.reroll()

    print(c.challenge.challenge)

if __name__ == "__main__":
    asyncio.run(doStuffs())
    
    # itemList = [{'itemName': 'Arachnomancer', 'quantity': 1}, {'itemName': 'ArchPaladin', 'quantity': 1}, {'itemName': 'Chaos Avenger', 'quantity': 1}, {'itemName': 'Chronomancer Prime', 'quantity': 1}, {'itemName': 'Dragon of Time', 'quantity': 1}, {'itemName': 'Legion Revenant', 'quantity': 1}, {'itemName': 'LightCaster', 'quantity': 1}, {'itemName': 'Lord Of Order', 'quantity': 1}, {'itemName': 'Quantum Chronomancer', 'quantity': 1}, {'itemName': 'Shaman', 'quantity': 1}, {'itemName': 'StoneCrusher', 'quantity': 1}, {'itemName': 'Void Highlord', 'quantity': 1}, {'itemName': 'Warrior', 'quantity': 1}, {'itemName': 'Yami no Ronin', 'quantity': 1}, {'itemName': 'Academy Uniform', 'quantity': 1}, {'itemName': 'Awescended', 'quantity': 1}, {'itemName': "Delinquent Leader's Garb", 'quantity': 1}, {'itemName': 'Ducky Naval Commander', 'quantity': 1}, {'itemName': 'EbilCorp Standard Player', 'quantity': 1}, {'itemName': "Fire Champion's Armor", 'quantity': 1}, {'itemName': 'Hollowborn DoomKnight', 'quantity': 1}, {'itemName': 'Hollowborn Envoy of Chaos', 'quantity': 1}, {'itemName': 'Infernal Flame Pyromancer', 'quantity': 1}, {'itemName': 'Pretty Sailor Mate', 'quantity': 1}, {'itemName': "Delinquent's Glasses + Locks Morph", 'quantity': 1}, {'itemName': "Dragonsworn Commander's Morph + Locks", 'quantity': 1}, {'itemName': 'Hollowborn Chaos Morph', 'quantity': 1}, {'itemName': "NightStalker's Locks", 'quantity': 1}, {'itemName': 'Sassy Melon Locks', 'quantity': 1}, {'itemName': "Shadow BoogieMan's Mask", 'quantity': 1}, {'itemName': 'Underworld ArchFiend Shade', 'quantity': 1}, {'itemName': 'Chaos Dragon Flames', 'quantity': 1}, {'itemName': "Elegant Siren's Tail", 'quantity': 1}, {'itemName': 'Eternal Flame of Loyalty', 'quantity': 1}, {'itemName': 'Fiendish Eternal Flame', 'quantity': 1}, {'itemName': 'Pretty Eternal Flame', 'quantity': 1}, {'itemName': 'Sugar-Sweet Wings', 'quantity': 1}, {'itemName': 'Yokai Oni Aura', 'quantity': 1}, {'itemName': 'Derpblivion Blade', 'quantity': 1}, {'itemName': "Empowered Chaos Avenger's Greatsword", 'quantity': 1}, {'itemName': 'Exalted Apotheosis', 'quantity': 1}, {'itemName': 'Fest-EBIL Katana', 'quantity': 1}, {'itemName': 'Hollowborn Sword of Doom', 'quantity': 1}, {'itemName': 'Necrotic Blade of Doom', 'quantity': 1}, {'itemName': 'Necrotic Blade of the Underworld', 'quantity': 1}, {'itemName': 'Necrotic Sword of Doom', 'quantity': 1}, {'itemName': 'Sin of the Abyss', 'quantity': 1}, {'itemName': 'Dual Exalted Apotheosis', 'quantity': 1}, {'itemName': 'High Formal Cane', 'quantity': 1}, {'itemName': 'Providence', 'quantity': 1}, {'itemName': 'Pink Quibble Bank Pet', 'quantity': 1}, {'itemName': 'Polly Roger', 'quantity': 1}, {'itemName': 'Endurance Draught', 'quantity': 80}, {'itemName': 'Fate Tonic', 'quantity': 287}, {'itemName': 'Potent Battle Elixir', 'quantity': 290}, {'itemName': 'Potent Destruction Elixir', 'quantity': 292}, {'itemName': 'Potent Honor Potion', 'quantity': 266}, {'itemName': 'Potent Malevolence Elixir', 'quantity': 292}, {'itemName': 'Potent Malice Potion', 'quantity': 295}, {'itemName': 'Potent Revitalize Elixir', 'quantity': 283}, {'itemName': 'Sage Tonic', 'quantity': 286}, {'itemName': 'Scroll of Enrage', 'quantity': 28}, {'itemName': 'Super-Fan Swag Token B', 'quantity': 44}, {'itemName': 'Treasure Potion', 'quantity': 292}, {'itemName': 'Unstable Malevolence Elixir', 'quantity': 292}, {'itemName': 'Zealous Ink', 'quantity': 13}, {'itemName': 'Insatiable Hunger', 'quantity': 1}, {'itemName': 'Treasure Chest', 'quantity': 250}, {'itemName': 'Gold Voucher 100k', 'quantity': 300}, {'itemName': 'Gold Voucher 500k', 'quantity': 272}, {'itemName': 'Northlands Getaway House', 'quantity': 1}, {'itemName': 'Skull Island House of DOOM', 'quantity': 1}, {'itemName': 'Summer Night', 'quantity': 1}, {'itemName': 'Holiday Party Piggy Guard', 'quantity': 6}, {'itemName': 'Arctic Fox Guard', 'quantity': 6}, {'itemName': 'Arctic Fox Guard At Rest', 'quantity': 6}, {'itemName': 'BlightStalker Guard (R)', 'quantity': 1}, {'itemName': 'Chaos Portal', 'quantity': 1}, {'itemName': 'Hollowborn Blade of Chaos (Floor)', 'quantity': 1}, {'itemName': 'Kitty Yu-Yule Guard', 'quantity': 6}, {'itemName': 'Twig & Forest Friends', 'quantity': 8}]
    # c.check_items(itemList)