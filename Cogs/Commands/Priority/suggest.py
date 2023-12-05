from typing import Any
from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
import datetime
from pymongo import MongoClient
from DataModels.guild import BaseGuild
import os
from DataModels.user import BaseUser
from dotenv import load_dotenv
load_dotenv()
import random
from Util.Yaml import Load_yaml


Base_User = BaseUser()
Base_Guild = BaseGuild()




            
class SuggestionCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["suggestion"]["database"]]
        self.suggestion_config = self.db[self.config["collections"]["suggestion"]["config"]]






    @commands.hybrid_group(name="suggestion", description=f"Suggestion based commands")
    async def suggestion(self, ctx):
        pass
    
               
    @suggestion.command(name=f"create", description=f"Create a suggestion")
    async def createsuggest(self, ctx: commands.Context, *, suggestion: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** processing your request.")
        embed = discord.Embed(title=f"Suggested by {ctx.author.display_name}", description=suggestion, color=discord.Color.light_embed())
        feedback_id = random.randint(1, 9999)
        embed.set_footer(text=f"Shello Systems")
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.name)       
        feedback_channel_id = await Base_Guild.get_suggestion_channel(guild_id=ctx.guild.id)
        if feedback_channel_id is None:
            return await message.edit(content=f"<:shell_denied:1160456828451295232> **{ctx.author.name},** the suggestion module has been incorrectly configured.")
        
        
        await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** succesfully sent your suggestion!")
        
        feedback_channel = ctx.guild.get_channel(feedback_channel_id)
        message2 = await feedback_channel.send(embed=embed, content=f"<:Approved:1163094275572121661> **{ctx.author.mention},** thank you for your suggestion!")
        await message2.add_reaction("<:Approved:1163094275572121661>")
        await message2.add_reaction("<:Denied:1163095002969276456>")
                     
async def setup(client: commands.Bot) -> None:
    await client.add_cog(SuggestionCog(client))