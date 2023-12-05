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

class CurrencyCreation(discord.ui.Modal):
    def __init__(self, title='Create a custom currency for your guild'):
        self.mongo_uri = None
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["Customization"]["database"]]
        self.customization_config = self.db[self.config["collections"]["Customization"]["config_collection"]]
        super().__init__(title=title)

        self.Message = discord.ui.TextInput(
            label='Custom Currency',
            style=discord.TextStyle.short,
            placeholder='E.g: Dollars',
            required=True,
            max_length=500,
        )

        self.add_item(self.Message)


    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = interaction.guild_id

        existing_config = self.customization_config.find_one({"guild_id": guild_id})

        if existing_config:
            self.customization_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"custom_currency": self.Message.value}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "custom_currency": self.Message.value
            }
            self.customization_config.insert_one(new_record)

        return await interaction.followup.send(
            content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** this server's custom currency has been set to **{self.Message.value}**!")


class CustomizationModuleSelection(discord.ui.Select):
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        options=[
            discord.SelectOption(label="Custom Currency",description="What should the bot refer to your currency as?", value="currency")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options, row=1)
    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "currency":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await interaction.response.send_modal(CurrencyCreation())                  

class CustomizationModuleView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(CustomizationModuleSelection(ctx=self.ctx, message=self.message))
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
        