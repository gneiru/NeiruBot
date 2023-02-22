import disnake
from disnake.ext import commands
from modules import mongo, variables

class Perm(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="give-coins", default_member_permissions=disnake.Permissions(administrator=True))
    async def give(self, inter, receiver: disnake.Member, amount: int):
        """
        Give Coins to a player
        Parameters
        ----------
        receiver: Registered player
        amount: Amount of Coins to be given
        """
        if not isinstance(amount, int):
            await inter.response.send_message(f"Please enter a valid amount of coins to give to {receiver.display_name}", ephemeral=True)
            return
        player = mongo.player()
        playerlist = await player.getPlayerList()
        player.discordID = receiver.id
        embed = disnake.Embed()
        # print(receiver.id)
        if receiver.id not in playerlist:
            embed.description = f"Player {receiver.display_name} is not yet registered."
            return await inter.send(embed=embed)
        await player.updatePlayer(amount)
        embed.set_author(name=receiver.display_name, icon_url=str(receiver.display_avatar))
        # embed.title = f"Player {receiver.display_name}"
        embed.description = f"{player.response}\n**Balance: **{player.balance} {variables.coin}"
        await inter.send(embed=embed)
    
    # @commands.slash_command(name="reset-challenges", default_member_permissions=disnake.Permissions(administrator=True))
    # async def reset(self, inter):
    #     """
    #     Resets completed challenges
    #     Parameters
    #     ----------
    #     """
    #     await inter.response.defer(ephemeral=True)
    #     player = mongo.player()
    #     await player.resetAllCompleted()
    #     resetMsg = player.response
    #     embed = disnake.Embed(description=resetMsg)
    #     await inter.edit_original_message("Msg sent")
    #     await inter.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Perm(bot))