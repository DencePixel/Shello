import discord 
from discord.ext import commands 
from Cogs.Commands.Config.Modules.design import DesignView
from Cogs.emojis import approved_emoji, denied_emoji
from Cogs.Commands.Config.Modules.payment import PaymentLinksActionSelect
from Cogs.Commands.Config.Modules.feedback import FeedbackView
from Cogs.Commands.Config.Modules.activity import ActivityModuleSelectView

class ModuleSelection(discord.ui.Select):
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        options=[
            discord.SelectOption(label="View Configuration",description="View this servers configuration.", value=f"Configuration"),
            discord.SelectOption(label="Designs",description="Configure the designs module.", value="Designs", emoji=f"<:design:1177878139611914321>"),
            discord.SelectOption(label="Feedback",description="Configure the feedback module.", value="Feedback", emoji=f"<:feedback:1177878141012803706>"),
            discord.SelectOption(label="Payment",description="Configure the payment module.", value="Payment Links", emoji=f"<:payment:1177878137674145833>"),
            discord.SelectOption(label=f"Activity", description=f"Configure the activity module.", value=f"Quota", emoji=f"<:order_updated:1177327822721794058>")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "Designs":
            if interaction.user.id != self.ctx.author.id:
                return
            
            TheView = DesignView(ctx=self.ctx, message=self.message)
            await interaction.response.defer()
            await self.message.edit(view=TheView, embed=None, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the design module.")
            
            
        if self.values[0] == "Feedback":
            if interaction.user.id != self.ctx.author.id:
                return
            
            view = FeedbackView(message=self.message, ctx=self.ctx, guild=interaction.guild)
            await interaction.response.defer()
            await self.message.edit(view=view, embed=None, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the feedback module.")

        if self.values[0] == "Payment Links":
            if interaction.user.id != self.ctx.author.id:
                return
            
            
            view = PaymentLinksActionSelect(message=self.message, user=self.ctx)
            await interaction.response.defer()
            await self.message.edit(embed=None, view=view, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the payment module.")
            
        if self.values[0] == "Quota":
            if interaction.user.id != self.ctx.author.id:
                return
            
            
            await interaction.response.defer()
            await self.message.edit(view=ActivityModuleSelectView(timeout=None, ctx=self.ctx, message=self.message), content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the activity module.")
        
            

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(ModuleSelection(ctx=self.ctx, message=self.message))
        
        


        
        
