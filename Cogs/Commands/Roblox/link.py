import os

import discord
from discord.ext import commands
import time
import traceback
import sqlite3
from random import randint
import random
import roblox

from roblox import Client
from pymongo import MongoClient

from Util.Yaml import Load_yaml, initalize_yaml
import string
import aiohttp
import json
rclient = Client()

class RobloxProfile(discord.ui.View):
    def __init__(self, roblox):
        super().__init__()
        self.roblox = roblox
        link = f"https://www.roblox.com/users/{self.roblox.id}/profile"
        self.add_item(discord.ui.Button(label='Profile', url=link))




class Done(discord.ui.View):
    def __init__(self, user, random_string, interaction, message):
        super().__init__()
        self.value = None
        self.user = user
        self.code = random_string
        self.message = message
        self.interaction = interaction
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        


    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def done(self, interaction: discord.Interaction, button: discord.Button):
        if self.config is None:
            await self.initialize()
        mongo_uri = self.mongo_uri
        cluster = MongoClient(mongo_uri)
        db = cluster[self.config["collections"]["Roblox"]["database"]]
        verify_config = db[self.config["collections"]["Roblox"]["accounts_collection"]]

        user = await rclient.get_user_by_username(self.user, expand=True)
        description = user.description

        if self.code in description:
            user_data = {
                "discord_user_id": str(self.interaction.user.id),
                "roblox_user_id": user.id 
            }
            verify_config.replace_one(
                {"discord_user_id": str(self.interaction.user.id)},
                user_data,
                upsert=True
            )

            view = RobloxProfile(user)
            await interaction.response.defer()

            await self.interaction.edit_original_response(
                content=f"**<:Approved:1163094275572121661> {self.interaction.user.display_name},** I have succesfully linked this account to ``{user.name}``.",
                embed=None,
                view=None
            )

            return await self.message.edit(
                content=f"**<:Approved:1163094275572121661> {self.interaction.user.display_name},** I have succesfully linked this account to ``{user.name}``.",
                embed=None,
                view=None
            )

        if self.code not in description:
            await self.message.edit(
                content=f"**{self.interaction.user.name},** I could not find ``{self.code}`` in your description. Please run the command again if you believe this is a mistake.",
                view=None,
                embed=None
            )
            
            
        

class Username(discord.ui.Modal):

    def __init__(self, message, ctx, mongo_uri, config):
        
        self.mongo_uri = mongo_uri
        self.config = config
        self.message = message
        self.db = self.config["collections"]["Roblox"]["database"]
        self.verify_config = self.config["collections"]["Roblox"]["accounts_collection"]
        self.ctx= ctx



        super().__init__(title="title")
        self.message = message
        
        self.name = discord.ui.TextInput(
            label='Roblox Username',
            placeholder='What is your roblox username?',
            style=discord.TextStyle.short,
            required=True
        )
        
        self.add_item(self.name)
        

        

        



    async def on_submit(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(f"<:Denied:1163095002969276456> **{interaction.user.display_name},** this is not your view!", ephemeral=True)
        user = await rclient.get_user_by_username(self.name.value, expand=True)
        random_string = f"SHELLO_ROBLOX_VERIFICATION_{interaction.user.id}{randint(100000, 999999)}"
        view = Done(self.name.value, random_string, interaction, message=self.message)
        embed = discord.Embed(color=discord.Color.dark_embed(), description=f"Hello **{interaction.user.name},** to verify ownership of the account ``{self.name.value}``, please put the provided code in the description of your roblox account, after that click the **Done** button\n\n **Account Information**\n> **Username:** ``{self.name.value}``\n> **User ID:** ``{user.id}``\n> **Profile Link:** https://roblox.com/users/{user.id}/profile\n\n**Enter This Code:**\n```{random_string}```")

        async with  aiohttp.ClientSession() as session:

            async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user.id},0&size=100x100&format=Png&isCircular=true") as resp:

                if resp.status == 200:

                    data = json.loads(await resp.text())


                    image_url = data['data'][0]['imageUrl']

                    embed.set_thumbnail(url=image_url)
        await interaction.response.send_message(ephemeral=True, view=view, embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)


class ApprovedMen2u(discord.ui.View):
    def __init__(self, message, ctx):
        super().__init__(timeout=None)
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.message = message
        self.ctx=ctx

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id=f"persistent_view:verify")
    async def verify(self, interaction: discord.Interaction, button: discord.Button):

                  
        await interaction.response.send_modal(Username(message=self.message, ctx=self.ctx, config=self.config, mongo_uri=self.mongo_uri))
        
        
class LinkAccountCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()

    @commands.hybrid_group(name=f"roblox", aliases=["Roblox","Rblx","rblx"])
    async def roblox_group(self, ctx: commands.Context):
        pass

    @roblox_group.command(name=f"link")
    async def link(self, ctx: commands.Context):
        message = await ctx.send(content=f"<:Badge:1163094257238806638> **{ctx.author.display_name},** please click the button below to link your roblox account.")
        view = ApprovedMen2u(message=message, ctx=ctx)
        try:
            await message.edit(view=view)
        except Exception as e:
            return await ctx.channel.send(content=e)        
        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(LinkAccountCog(client))
