import disnake

class Reroll(disnake.ui.View):
    def __init__(self, author, quest):
        # super().__init__(timeout=3600)
        super().__init__(timeout=60)
        self.value = None
        self.author = author
        self.quest = quest

        self._toggleBTN()

    def _toggleBTN(self):
        if self.reroll.label == "Roll Anew":
            self.add_item(self.turn)
            self.add_item(self.reload)
            self.reload.disabled = False
            self.reroll.label = "Reroll"
        if self.quest.embed.color == disnake.Color.red():
            self.turn.disabled = True 
        elif self.quest.embed.color == disnake.Color.green():
            self.reroll.disabled = True
            self.reload.disabled = True 
            self.turn.disabled = False
        elif self.quest.embed.color == disnake.Color.blurple():
            self.clear_items()
        else:
            self.remove_item(self.turn)
            self.remove_item(self.reload)
            self.reroll.disabled = False
            self.reroll.label = "Roll Anew"

    @disnake.ui.button(label="Reroll", style=disnake.ButtonStyle.green)
    async def reroll(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.author:
            return await inter.send("You are not allowed to reroll this challenge!",ephemeral=True)
        await self.quest.reroll()
        self._toggleBTN()
        await inter.response.edit_message(embed=self.quest.embed, view=self)

    @disnake.ui.button(label="Turn In", style=disnake.ButtonStyle.grey)
    async def turn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.author:
            return await inter.send("You are not allowed to turn in this challenge!",ephemeral=True)
        await self.quest.turn_in()
        self.quest.embed.color = disnake.Color.dark_blue()
        self._toggleBTN()
        self.quest.embed.set_author(name=inter.author.display_name, icon_url=str(inter.author.display_avatar))
        await inter.response.edit_message(embed=self.quest.embed, view=self)

    @disnake.ui.button(label="Reload", style=disnake.ButtonStyle.blurple)
    async def reload(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.author:
            return await inter.send("You are not allowed to reload this challenge!",ephemeral=True)
        await self.quest.reload()
        self._toggleBTN()
        await inter.response.edit_message(embed=self.quest.embed, view=self)