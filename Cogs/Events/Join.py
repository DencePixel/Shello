import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import os
import aiohttp
import pymongo
from Utils.functions import replace_variable_welcome



class Join(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with aiohttp.ClientSession() as session:
            embed = discord.Embed(description=f"``>`` {guild.name}\n``>`` {guild.id}\n``>`` {guild.owner.mention}", color=discord.Color(2829617))
            webhook = discord.Webhook.from_url(os.getenv("BOT_JOINS_WEBHOOK"), session=session)
            webhook.send(embed=embed)
        


    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id

        cluster = pymongo.MongoClient(os.getenv("MONGO_URI"))
        db = cluster[os.geten("WELCOME_DB")]
        welcome_config = db[os.getenv("WELCOME_COLLECTION")]

        config = welcome_config.find_one({"guild_id": guild_id})
        if config is None:
            return

        welcome_message = config.get("welcome_message")
        welcome_channel_id = config.get("welcome_channel_id")

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

        
        

        

        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Join(client))
