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




            
class FeedbackCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
             
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = MongoClient(self.mongo_uri)

        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.feedback_records = self.design_Db[self.config["collections"]["design"]["feedback_records"]]

        





    @commands.hybrid_group(name="feedback", description=f"Feedback based commands")
    async def feedback(self, ctx):
        pass
    
               
    @feedback.command(name=f"provide", description=f"Provide feedback on a design you recieved")
    @discord.app_commands.choices(
        rating=[
            discord.app_commands.Choice(name="⭐", value="1"), 
            discord.app_commands.Choice(name="⭐⭐", value="2"),
            discord.app_commands.Choice(name="⭐⭐⭐", value="3"),
            discord.app_commands.Choice(name="⭐⭐⭐⭐", value="4"),
            discord.app_commands.Choice(name="⭐⭐⭐⭐⭐", value="5")
        ]
    )
    async def provide(self, ctx: commands.Context, rating: str, designer: discord.Member, *, feedback: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** processing your request.")
        embed = discord.Embed(title=f"Reviewed by {ctx.author.display_name}", description=f"<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Rating:** **{rating}/5**\n<:Shello_Right:1164269631062691880> **Feedback:** {feedback}", color=discord.Color.light_embed())
        feedback_id = random.randint(1, 9999)
        embed.set_footer(text=f"Feedback ID: {feedback_id} | Shello Systems")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)       
        feedback_channel_id = await Base_Guild.get_feedback_channel(guild_id=ctx.guild.id)
        ctx.guild.member_count
        if feedback_channel_id is None:
            return await message.edit(content=f"<:shell_denied:1160456828451295232> **{ctx.author.name},** the feedback module has been incorrectly configured.")
        
        
        await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** succesfully sent your feedback!")
        
        feedback_channel = ctx.guild.get_channel(feedback_channel_id)
        try:
            
            message = await feedback_channel.send(embed=embed, content=f"<:Approved:1163094275572121661> **{designer.mention},** you have recieved feedback!")
        except:
            await message.edit(content=f"<:Alert:1163094295314706552> **{ctx.author.display_name},** I can't send a message to that channel.")
            
            
        
        feedback_data = {
            "guild_id": ctx.guild.id,
            "feedback_id": feedback_id,
            "author": ctx.author.id,
            "designer": designer.id,
            "feedback": feedback,
            "timestamp": datetime.datetime.utcnow(),
            "message_id": message.id 
        }
        self.feedback_records.insert_one(feedback_data)
        
        
    @feedback.command(name=f"view", description=f"View the feedback that you recieved")
    async def feedbackview(self, ctx: commands.Context, feedback_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** fetching information for that feedback.")
        refund_request = self.feedback_records.find_one(
            {"guild_id": ctx.guild.id, "feedback_id": feedback_id}
        )
        
        
        if not refund_request:
            return await message.edit(content=f"<:shell_denied:1160456828451295232> **{ctx.author.name},** I can't find that specific feedback.")
        poster_id = refund_request.get("author")
        message_id = refund_request.get("message_id")
        timestamp = refund_request.get("timestamp")
        designer = refund_request.get("designer")
        format_timestamp = discord.utils.format_dt(timestamp, "R")
        feedback_str = refund_request.get("feedback")
        
        embed = discord.Embed(title=f"Feedback - {feedback_id}", color=discord.Color.light_embed(), description=f"<:Shello_Right:1164269631062691880> **Poster:** <@!{poster_id}>\n<:Shello_Right:1164269631062691880> **Designer:** <@!{designer}>\n<:Shello_Right:1164269631062691880> **Timestamp:** {format_timestamp}\n<:Shello_Right:1164269631062691880> **Feedback:** ``{feedback_str}``")
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        await message.edit(embed=embed, content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** here is the requested feedback log.")
            
              
async def setup(client: commands.Bot) -> None:
    await client.add_cog(FeedbackCog(client))