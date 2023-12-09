import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import os
import aiohttp
import pymongo
from Util.functions import replace_variable_welcome

from Util.Yaml import Load_yaml
load_dotenv()




class Join(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        




    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with aiohttp.ClientSession() as session:
            embed = discord.Embed(description=f"``>`` {guild.name}\n``>`` {guild.id}\n``>`` {guild.owner.mention}", color=discord.Color(2829617))
            webhook = discord.Webhook.from_url(os.getenv("BOT_JOINS_WEBHOOK"), session=session)
            await webhook.send(embed=embed)
        


    
    @commands.Cog.listener()
    async def on_member_join(self, member):
            
        guild_id = member.guild.id
        

        cluster = pymongo.MongoClient(self.mongo_uri)
        db = cluster[self.config["collections"]["welcome"]["database"]]
        welcome_config = db[self.config["collections"]["welcome"]["collection"]]
        
        alertsdb = cluster[self.config["collections"]["Alerts"]["database"]]
        alertsconfig = alertsdb[self.config["collections"]["Alerts"]["config"]]
        alertslogs = alertsdb[self.config["collections"]["Alerts"]["logs"]]

        config = welcome_config.find_one({"guild_id": guild_id})
        if config is None:
            return

        welcome_message = config.get("welcome_message")
        welcome_channel_id = config.get("welcome_channel")

        if not welcome_channel_id:
            return
        
    


        replacements = {
            '!member.mention!': member.mention,
            '!member.name!': member.display_name,
            '!member.id!': str(member.id),
            '!member.discriminator!': str(member.discriminator),
            '!member.avatar_url!': member.display_avatar.url,
            '!member.desktop_status!': str(member.desktop_status),  
            '!member.mobile_status!': str(member.mobile_status),

            '!guild.name!': member.guild.name,
            '!guild.id!': str(member.guild.id),
            '!guild.member_count!': str(member.guild.member_count)
        }
        welcome_message = await replace_variable_welcome(welcome_message, replacements)
        welcome_channel = member.guild.get_channel(welcome_channel_id)
        if welcome_channel:
            await welcome_channel.send(welcome_message)
            role_id = config.get("join_role")
            if role_id:
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except:
                        pass
                    
        
        alerts_config = alertsconfig.find_one({"guild_id": guild_id})
        if not alerts_config:
            return
                  
        filter_criteria = {"target_id": member.id}

        count = alertslogs.count_documents(filter_criteria)
        if count > 1:
            embed = discord.Embed(title=f"Suspicious Account", description=f"**Account Information**\n<:Shello_Right:1164269631062691880> **User:** {member.mention}\n<:Shello_Right:1164269631062691880> **ID:** {member.id}\n\n**Reason**\n<:Shello_Right:1164269631062691880> **Reason:** ``User exceeds normal amount of alert.``\n<:Shello_Right:1164269631062691880> **Alerts Count:** ``{count}``", color=discord.Color.light_embed())
            embed.set_footer(text=f"Suspicious Account Flagged")
            embed.set_thumbnail(url=member.display_avatar.url)
            channel_id = alerts_config.get("alert_channel")
            channel = member.guild.get_channel(channel_id)
            try:
                await channel.send(embed=embed, content=f"<:Alert:1163094295314706552> I have flagged this account as suspicious.")
            except:
                return
            
                    

        
        

        

        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Join(client))
