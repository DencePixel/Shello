import discord

class GlobalFinishedButton(discord.ui.Button):
    def __init__(self, ctx, message):
        super().__init__(style=discord.ButtonStyle.green, label="Finished", row=2)
        self.ctx = ctx
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        from Cogs.Commands.Config.view import SelectView

        if interaction.user.id != self.ctx.author.id:
            return

        await interaction.response.defer()

        await self.message.edit(content="You are now setting up shello!", view=SelectView(ctx=self.ctx, message=self.message), embed=None)