from typing import Any
from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
from discord.interactions import Interaction
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




            
class FeedbackCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_uri = None
        self.config = None  
        self.cluster = MongoClient(self.mongo_uri)
        
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.design_records = self.design_Db[self.config["collections"]["design"]["log_collection"]]

        





    @commands.hybrid_group(name="staff", description=f"Staff based commands")
    async def staff(self, ctx):
        pass
    
               
    @staff.command(name=f"feedback", description=f"Provide feedback on a design you recieved")
    @discord.app_commands.choices(
        rating=[
            discord.app_commands.Choice(name="⭐", value="1"), 
            discord.app_commands.Choice(name="⭐⭐", value="2"),
            discord.app_commands.Choice(name="⭐⭐⭐", value="3"),
            discord.app_commands.Choice(name="⭐⭐⭐⭐", value="4"),
            discord.app_commands.Choice(name="⭐⭐⭐⭐⭐", value="5")
        ]
    )
    async def feedback(self, ctx: commands.Context, rating: str, designer: discord.Member, *, product: str):
        embed = discord.Embed(title=f"{product} - Review", description=f"{ctx.author.mention} has rated their {product} a **{rating}** star!", color=discord.Color.gold())
        embed.set_footer(text=f"Shello Systems")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)       
        feedback_channel_id = await Base_Guild.get_feedback_channel(guild_id=ctx.guild.id)
        ctx.guild.member_count
        if feedback_channel_id is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** the feedback module has been incorrectly configured.")
        
        feedback_channel = ctx.guild.get_channel(feedback_channel_id)
        await feedback_channel.send(embed=embed, content=f"<:Approved:1163094275572121661> **{designer.mention},** you have recieved feedback!")
        await ctx.send(f"<:Approved:1163094275572121661> **{ctx.author.display_name},** succesfully sent your feedback!")
              
async def setup(client: commands.Bot) -> None:
    await client.add_cog(FeedbackCog(client))