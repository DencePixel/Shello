import discord
from Cogs.emojis import approved_emoji, denied_emoji

class GlobalFinishedButton(discord.ui.Button):
    def __init__(self, ctx, message):
        super().__init__(style=discord.ButtonStyle.gray, label="Return", row=2)
        self.ctx = ctx
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        from Cogs.Commands.Config.view import SelectView

        if interaction.user.id != self.ctx.author.id:
            return

        await interaction.response.defer()

        await self.message.edit(content=f"{approved_emoji} **{interaction.user.display_name},** are now setting up shello!", view=SelectView(ctx=self.ctx, message=self.message), embed=None)