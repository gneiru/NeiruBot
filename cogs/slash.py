import disnake
from disnake.ext import commands
from modules import mongo, validate, aqw, quest
from modules.buttons import Reroll
from modules.variables import guildName
from modules.builder import embed as EmbedBuilder
class Slash(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command()
    async def register(self, inter, name):
        """Register AQW Account
        Parameters
        ----------
        name: AQW Account Name
        """
        await inter.response.defer()
        account = aqw.account(name=name)
        await account.check()
        if account.isClean:
            p = mongo.player(ccid = account.user_id, discordID = inter.author.id, guild = account.guild, name = account.name)
            await p.register()
            await inter.send(content=p.response)  
        else:
            await inter.send(content=account.status)
    
    @commands.slash_command(name="force-register")
    async def force_register(self, inter, name):
        """Force register account, Note that this will reset your progress if you are registered
        Parameters
        ----------
        name: AQW Account Name
        """
        await inter.response.defer()
        account = aqw.account(name=name)
        await account.check()
        if account.isClean:
            p = mongo.player(ccid = account.user_id, discordID = inter.author.id, guild = account.guild, name = account.name)
            await p.register(force=True)
            await inter.send(content=p.response)  
        else:
            await inter.send(content=account.status)
    
    @commands.slash_command()
    @validate.id
    async def profile(self, inter):
        """Check AQW Player Profile
        Parameters
        ----------
        """
        await inter.response.defer(ephemeral=False)
        player = mongo.player()
        player.discordID = inter.author.id
        await player.getPlayerData()
        embed = disnake.Embed()
        embed.title = f"{player.name}'s Profile"
        embed.description = f"**Guild: **{player.guild}" 
        embed.color = disnake.Color.green()
        await inter.edit_original_message(embed=embed)

    @commands.cooldown(5, 3600, type=commands.BucketType.user)
    @commands.slash_command(name="challenge")
    @validate.id
    async def challenge(self, inter):
        """AQW Challenge is like an AQW quest
        Parameters
        ----------
        """
        await inter.response.defer()
        q = quest.quest(playerID = inter.author.id)
        await q.roll()
        view = Reroll(inter.author.id, q) # button
        if q.embed.color == disnake.Color.red():
            view.turn.disabled = True 
        elif q.embed.color == disnake.Color.green():
            view.reroll.disabled = True
            view.reload.disabled = True 
            view.turn.disabled = False

        message = await inter.edit_original_message(embed=q.embed, view=view)
        await view.wait()
        if view.value is None:
            await message.edit(embed=q.embed, view = None)

    @commands.slash_command()
    @validate.id
    async def balance(self, inter):
        """
        Check AQW Account Balance
        Parameters
        ----------
        """
        await inter.response.defer(ephemeral=False)
        player = mongo.player(discordID = inter.author.id)
        balance = await player.getPlayerBalance()
        embed = EmbedBuilder()
        embed.balance = balance #tbr
        embed.handler = inter.author.id
        # TODO: make an inventory list then past it to inventoryEmbed, replace lines with "tbr" comments
        await inter.edit_original_message(embed=embed.inventoryEmbed())
    
    @commands.slash_command()
    async def preview(inter: disnake.ApplicationCommandInteraction, challenge: str):
        """
        Preview Challenge
        Parameters
        ----------
        challenge : AQW Items challenge
        """
        await inter.response.defer(ephemeral=False)
        q = quest.quest(playerID = inter.author.id)
        await q.preview(challenge)
        await inter.edit_original_message(embed=q.embed)

    @preview.autocomplete("challenge")
    async def preview_autocomp(inter: disnake.ApplicationCommandInteraction, challenge: str):
        c = mongo.challenge()
        CHALS = c.getAllChallenge()
        if challenge:
            string = challenge.lower()  
            return [lang for lang in CHALS if string in lang.lower()]
        else:
            return [lang for lang in CHALS][-25:]
        
        ...
        

def setup(bot):
    bot.add_cog(Slash(bot))