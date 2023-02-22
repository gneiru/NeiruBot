import disnake
from disnake.ext import commands
from datetime import datetime, timedelta

class OnError(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_time = error.retry_after
            print(cooldown_time)
            cooldown_timestamp = int((datetime.now() + timedelta(seconds=cooldown_time)).timestamp())
            timestamp_str = f"Try again <t:{cooldown_timestamp}:R>"
            embed = disnake.Embed(description=timestamp_str)
            embed.title = "You are on cooldown"
            embed.colour = disnake.Color.red()
            await inter.send(embed=embed, ephemeral=False)

# @bot.event
# async def on_message_command_error(inter, error):
#     await inter.send(embed=disnake.Embed.from_dict({"description": error}),ephemeral=True)

# @bot.event
# async def on_user_command_error(inter, error):
#     await inter.send(embed=disnake.Embed.from_dict({"description": error}),ephemeral=True)

# @bot.event
# async def on_slash_command_completion(inter):
#     channel = bot.get_channel(int(os.environ.get('LOGS_CHANNEL')))
#     await channel.send(embed=disnake.Embed.from_dict({"description": f"`/{inter.application_command.name}` used by {inter.user} in **{inter.guild}** "}))

# @bot.event
# async def on_message_command_completion(inter):
#     channel = bot.get_channel(int(os.environ.get('LOGS_CHANNEL')))
#     await channel.send(embed=disnake.Embed.from_dict({"description": f"`{inter.application_command.name}` used by {inter.user} in **{inter.guild}**\nType: Message Command "}))

# @bot.event
# async def on_user_command_completion(inter):
#     channel = bot.get_channel(int(os.environ.get('LOGS_CHANNEL')))
#     await channel.send(embed=disnake.Embed.from_dict({"description": f"`{inter.application_command.name}` used by {inter.user} in **{inter.guild}**\nType: User Command "}))
    

def setup(bot):
    bot.add_cog(OnError(bot))