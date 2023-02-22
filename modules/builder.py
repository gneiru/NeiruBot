import disnake
from modules.variables import coin

class embed:
    def __init__(self):   
        self.embed = None
        self.balance = None
        self.handler = None
    
    def inventoryEmbed(self):
        e = disnake.Embed()
        e.description = "Something went wrong."
        if self.balance:
            
            desc_header = f"Items carried by <@{self.handler}>" 
            desc_body = f"{coin} **{self.balance}** · `coin`"
            e.description = f"{desc_header}\n\n{desc_body}"
        return e
