import discord 
from discord.ext import commands 
from Cogs.Commands.Config.Modules.design import DesignView
from Cogs.emojis import approved_emoji, denied_emoji
from Cogs.Commands.Config.Modules.payment import PaymentLinksActionSelect

class ModuleSelection(discord.ui.Select):
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        options=[
            discord.SelectOption(label="View Configuration",description="View this servers configuration.", value=f"Configuration"),
            discord.SelectOption(label="Configure Designs",description="Configure the designs module.", value="Designs"),
            discord.SelectOption(label="Configure Payment",description="Configure the payment module.", value="Payment Links")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.values[0] == "Designs":
            if interaction.user.id != self.ctx.author.id:
                return
            
            TheView = DesignView(ctx=self.ctx, message=self.message)
            await self.message.edit(view=TheView, embed=None, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the design module.")
            
            
        if self.values[0] == "Payment Links":
            if interaction.user.id != self.ctx.author.id:
                return
            
            
            view = PaymentLinksActionSelect(message=self.message, user=self.ctx)
            await self.message.edit(embed=None, view=view, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the payment module.")
            

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(ModuleSelection(ctx=self.ctx, message=self.message))
        
        


        
        
