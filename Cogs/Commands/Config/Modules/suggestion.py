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

class SuggestionChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, message):
        self.ctx = ctx
        self.mongo_uri = None
        self.message = message
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["suggestion"]["database"]]
        self.suggestion_config = self.db[self.config["collections"]["suggestion"]["config"]]

        super().__init__(placeholder="Select a suggestion channel", max_values=1, min_values=1, row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)

        await interaction.response.defer()
        guild_id = interaction.guild_id
        
        suggestion_channel = int(self.values[0].id)

        existing_config = self.suggestion_config.find_one({"guild_id": guild_id})

        if existing_config:
            self.suggestion_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"suggestion_channel": suggestion_channel}}
            )
            
        else:
            new_record = {
                "guild_id": guild_id,
                "suggestion_channel": suggestion_channel
            }
            self.suggestion_config.insert_one(new_record)
            
            
        return await self.message.edit(
            content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** this server's suggestion channel has been set to <#{suggestion_channel}>!")



        
            

