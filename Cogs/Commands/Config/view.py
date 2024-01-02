import discord 
from discord.ext import commands 
from Cogs.Commands.Config.Modules.design import DesignView
from Cogs.emojis import approved_emoji, denied_emoji
from Cogs.Commands.Config.Modules.payment import PaymentLinksActionSelect
from Cogs.Commands.Config.Modules.feedback import FeedbackView
from Cogs.Commands.Config.Modules.activity import ActivityModuleSelectView
from Cogs.Commands.Config.Modules.welcome import WelcomeModuleSelectionView
from Cogs.Commands.Config.Modules.suggestion import SuggestionChannel
from Cogs.Commands.Config.Modules.customization import CustomizationModuleView
from Cogs.Commands.Config.Modules.alerts import AlertsModuleSelection
from Cogs.Commands.Config.Modules.leaves import LeavesModuleSelection

class ModuleSelection(discord.ui.Select):
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        options=[
            discord.SelectOption(label="Designs",description="Configure the designs module.", value="Designs", emoji=f"<:design:1177878139611914321>"),
            discord.SelectOption(label="Feedback",description="Configure the feedback module.", value="Feedback", emoji=f"<:feedback:1177878141012803706>"),
            discord.SelectOption(label="Payment",description="Configure the payment module.", value="Payment Links", emoji=f"<:payment:1177878137674145833>"),
            discord.SelectOption(label="Activity", description=f"Configure the activity module.", value=f"Quota", emoji=f"<:order_updated:1177327822721794058>"),
            discord.SelectOption(label="Welcome", description=f"Configure the welcome module.", value=f"Welcome", emoji=f"<:person_check:1178413964531609652>"),
            discord.SelectOption(label=f"Suggestions", description=f"Configure the suggestions module.", value=f"Suggestions", emoji=f"<:suggestion:1181708198521090189>"),
            discord.SelectOption(label=f"Customization", description=f"Configure the customization module.", value=f"Customization", emoji=f"<:customization:1181651424627662868>"),
            discord.SelectOption(label=f"Alerts", description=f"Configure the alerts module.", emoji=f"<:Alert:1163094295314706552>", value=f"Alerts"),
            discord.SelectOption(label=f"Leaves", description=f"Configure the LOA module.", emoji=f"<:leaves:1184437355424251934>", value=f"leaves"),
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.values[0] == "Designs":
            if interaction.user.id != self.ctx.author.id:
                return
            
            TheView = DesignView(ctx=self.ctx, message=self.message)
            await self.message.edit(view=TheView, embed=None, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the design module.")
            
            
        if self.values[0] == "Feedback":
            if interaction.user.id != self.ctx.author.id:
                return
            
            view = FeedbackView(message=self.message, ctx=self.ctx, guild=interaction.guild)
            await self.message.edit(view=view, embed=None, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the feedback module.")

        if self.values[0] == "Payment Links":
            if interaction.user.id != self.ctx.author.id:
                return
            
            
            view = PaymentLinksActionSelect(message=self.message, user=self.ctx)
            await self.message.edit(embed=None, view=view, content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the payment module.")
            
        if self.values[0] == "Quota":
            if interaction.user.id != self.ctx.author.id:
                return
            
            
            await self.message.edit(view=ActivityModuleSelectView(timeout=None, ctx=self.ctx, message=self.message), content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the activity module.")
        
        if self.values[0] == "Welcome":
            if interaction.user.id != self.ctx.author.id:
                return
            await self.message.edit(view=WelcomeModuleSelectionView(timeout=None, ctx=self.ctx, message=self.message), content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the welcome module.")
            
        if self.values[0] == "Suggestions":
            if interaction.user.id != self.ctx.author.id:
                return
            
            
            view = discord.ui.View(timeout=None)
            view.add_item(SuggestionChannel(self.ctx, message=self.message))
            from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
            view.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
            await self.message.edit(view=view, content=f"<:Approved:1163094275572121661> **@{self.ctx.author.display_name},** you are now setting up the suggestion channel.")
            
            
        if self.values[0] == "Customization":
            if interaction.user.id != self.ctx.author.id:
                return
            await self.message.edit(view=CustomizationModuleView(timeout=None, ctx=self.ctx, message=self.message), content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the customization module.")
            
        if self.values[0] == "Alerts":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await self.message.edit(view=AlertsModuleSelection(timeout=None, ctx=self.ctx, message=self.message), content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the alerts module.")
        
        if self.values[0] == "leaves":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await self.message.edit(view=LeavesModuleSelection(timeout=None, ctx=self.ctx, message=self.message), content=f"{approved_emoji} **@{interaction.user.display_name},** you are now setting up the LOA module.")
        


class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(ModuleSelection(ctx=self.ctx, message=self.message))
        
        


        
        
