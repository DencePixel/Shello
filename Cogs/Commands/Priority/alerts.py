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



        
        



    
class AlertsCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.alertsdb = self.cluster[self.config["collections"]["Alerts"]["database"]]
        self.alertsconfig = self.alertsdb[self.config["collections"]["Alerts"]["config"]]
        self.alertslogs = self.alertsdb[self.config["collections"]["Alerts"]["logs"]]
        





    @commands.hybrid_group(name="alert", description=f"Alert based commands")
    async def alert(self, ctx):
        pass
    
    
    @alert.command(name="create", description="Log an alert on someone")
    async def createalert(self, ctx: commands.Context, user: discord.Member, *, reason: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await message.edit(content=f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. ")
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        designer_channel = self.client.get_channel(designer_log_channel_id)
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if staff_role not in ctx.author.roles:
            return await message.edit(content=f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you can't use this command.")

        try:
            alerts_config = self.alertsconfig.find_one({"guild_id": guild_id})
            if not alerts_config:
                return
                  

            channel_id = alerts_config.get("alert_channel")
            channel = ctx.guild.get_channel(channel_id)
            alert_id = random.randint(0, 9999)
            await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** I have succesfully created that alert.")
            record = {
                "guild_id": ctx.guild.id,
                "target_id": user.id,
                "moderator_id": ctx.author.id,
                "reason": reason,
                "alert_id": alert_id
            }
            self.alertslogs.insert_one(record)
            embed = discord.Embed(title=f"Alert Created", description=f"<:Shello_Right:1164269631062691880> **Moderator:** {ctx.author.mention}\n<:Shello_Right:1164269631062691880> **Target:** {user.mention}\n<:Shello_Right:1164269631062691880> **Reason:** {reason}", color=discord.Color.light_embed())
            embed.set_footer(text=f"ID: {alert_id}")
            await channel.send(embed=embed, content=f"<:Approved:1163094275572121661> **{ctx.author.display_name}** has submitted a new alert.")
        except Exception as e:
            print(e)
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** something went wrong.")
        
        
    @alert.command(name=f"find", description=f"Find a specific alert")
    async def alertfind(self, ctx: commands.Context, alert_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** you need to set up the design module. ")
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        designer_channel = self.client.get_channel(designer_log_channel_id)
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if staff_role not in ctx.author.roles:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** you can't use this command.")
        
        query = self.alertslogs.find_one({"guild_id": ctx.guild.id, "alert_id": alert_id})
        if not query:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** I can't find that alert.")
        
        moderator_id = query.get("moderator_id")
        reason = query.get("reason")
        target_id = query.get("target_id")
        embed = discord.Embed(title=f"Alert {alert_id}", description=f"**Target Information**\n<:Shello_Right:1164269631062691880> **Target:** <@!{target_id}>\n<:Shello_Right:1164269631062691880> **Target ID:** {target_id}\n\n**Alert Information**\n<:Shello_Right:1164269631062691880> **Moderator:** <@!{moderator_id}>\n<:Shello_Right:1164269631062691880> **Reason:** {reason}", color=discord.Color.light_embed(), timestamp=discord.utils.utcnow())
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        embed.set_footer(text=f"Alert ID: {alert_id}")
        return await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** here is the requested alert.", embed=embed)
    
    @alert.command(name=f"revoke")
    async def revokealert(self, ctx: commands.Context, alert_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** you need to set up the design module. ")
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        designer_channel = self.client.get_channel(designer_log_channel_id)
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if staff_role not in ctx.author.roles:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** you can't use this command.")
        
        query = self.alertslogs.find_one({"guild_id": ctx.guild.id, "alert_id": alert_id})
        if not query:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** I can't find that alert.")
        
        moderator_id = query.get("moderator_id")
        reason = query.get("reason")
        target_id = query.get("target_id")
        embed = discord.Embed(title=f"Alert {alert_id} Deleted", description=f"**Target Information**\n<:Shello_Right:1164269631062691880> **Target:** <@!{target_id}>\n<:Shello_Right:1164269631062691880> **Target ID:** {target_id}\n\n**Alert Information**\n<:Shello_Right:1164269631062691880> **Moderator:** <@!{moderator_id}>\n<:Shello_Right:1164269631062691880> **Revoked By:** <@!{ctx.author.id}>\n<:Shello_Right:1164269631062691880> **Reason:** {reason}", color=discord.Color.light_embed(), timestamp=discord.utils.utcnow())
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        embed.set_footer(text=f"Succesfully deleted Alert {alert_id}")
        
        self.alertslogs.delete_one(query)
        alerts_config = self.alertsconfig.find_one({"guild_id": guild_id})
        if not alerts_config:
            return
                  

        channel_id = alerts_config.get("alert_channel")    
        channel = ctx.guild.get_channel(channel_id)
        await channel.send(embed=embed, content=f"**{ctx.author.display_name},** has just revoked this alert.")    
        return await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** I have succesfully revoked that alert.")
        
            
        

    
        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(AlertsCog(client))