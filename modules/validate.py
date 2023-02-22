import disnake
from modules.variables import guildName, PermIDS
from functools import wraps
from modules.database import database as db

collection = db.players

def id(func):
    @wraps(func)
    async def wrapper(self, inter, *args, **kwargs):
        # Check if user's ID is in MongoDB collection
        user_id = inter.author.id
        embed = disnake.Embed()
        user = collection.find_one({"discordID": user_id})
        if user is None:
            embed.description = "You are not yet registered, Please register first using `/register`."
            embed.color = disnake.Color.red()
            await inter.send(embed=embed)
            return
        elif user and user['guild'] != guildName:
            embed.description = f"Sorry, this command is only accessible to {guildName} members."
            embed.color = disnake.Color.red()
            await inter.send(embed=embed)
            return
        else:
            return await func(self, inter, *args, **kwargs)
    return wrapper

def isNeiruXp(func):
    @wraps(func)
    async def areYou(self, inter, *args, **kwargs):
        user_id = inter.author.id
        embed = disnake.Embed()
        if user_id in PermIDS:
            embed.description = "You can't use this command."
            await inter.send(embed=embed,ephemeral=True)
            return
        else:
            return await func(self, inter, *args, **kwargs)
    return areYou