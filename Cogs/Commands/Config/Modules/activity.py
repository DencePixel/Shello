import discord
import pymongo
from pymongo import MongoClient
from Util.Yaml import Load_yaml

import discord
from discord.ext import commands
from pymongo import MongoClient

import discord
from discord.ext import commands
from pymongo import MongoClient

class ActivityChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, message):
        self.ctx = ctx
        self.mongo_uri = None
        self.message = message
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.db[self.config["collections"]["design"]["config_collection"]]

        super().__init__(placeholder="Select a activity log channel", max_values=1, min_values=1, row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)

        await interaction.response.defer()
        guild_id = interaction.guild_id
        
        activity_channel = int(self.values[0].id)

        existing_config = self.design_config.find_one({"guild_id": guild_id})

        if existing_config:
            self.design_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"activity_channel": activity_channel}}
            )
            
            return await self.message.edit(
                content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** this server's activity channel has been set to <#{activity_channel}>!",
                ephemeral=True
                )
        else:
            return await self.message.edit(
            content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** you need to setup the design module before you can use this!",
            ephemeral=True)




class QuotaCreation(discord.ui.Modal):
    def __init__(self, title='Create a quota for your designs'):
        self.mongo_uri = None
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.db[self.config["collections"]["design"]["config_collection"]]
        super().__init__(title=title)

        self.Message = discord.ui.TextInput(
            label='Weekly design quota',
            style=discord.TextStyle.short,
            placeholder='E.g: 1',
            required=True,
            max_length=500,
        )

        self.add_item(self.Message)


    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = interaction.guild_id
        if not self.Message.value.isdigit():
            return await interaction.followup.send(
                content=f"<:Denied:1163095002969276456> **{interaction.user.display_name},** please enter a valid number of designs.",
                ephemeral=True
            )
        weekly_quota = int(self.Message.value)

        existing_config = self.design_config.find_one({"guild_id": guild_id})

        if existing_config:
            self.design_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"weekly_quota": weekly_quota}}
            )
        else:
            return await interaction.followup.send(
            content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** you need to setup the design module before you can use this!")

        return await interaction.followup.send(
            content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** this server's weekly quota has been set to {weekly_quota} designs!")


class ActivityModuleSelection(discord.ui.Select):
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        options=[
            discord.SelectOption(label="Quota Channel",description="What channel the Quota log sends to", value="Channel"),
            discord.SelectOption(label=f"Quota Requirement", description=f"How many designs are required per week", value=f"Quota")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options, row=1)
    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "Quota":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await interaction.response.send_modal(QuotaCreation())            

        if self.values[0] == "Channel":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await interaction.response.defer()
            
            view = discord.ui.View(timeout=None)
            view.add_item(ActivityChannel(self.ctx, message=self.message))
            from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
            view.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
            await self.message.edit(view=view, content=f"<:Approved:1163094275572121661> **{self.ctx.author.display_name},** you are now setting up the activity channel.")
            

        
            

class ActivityModuleSelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(ActivityModuleSelection(ctx=self.ctx, message=self.message))
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
        