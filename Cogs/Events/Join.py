import discord
from discord.ext import commands
import pymongo
from utils import replace_variable_welcome


class Join(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_client = pymongo.MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        self.db = self.mongo_client["Master"]
        self.servers_collection = self.db["Servers"]

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        existing_guild = self.servers_collection.find_one({"guild_id": guild.id})
        
        if existing_guild:
            channel = self.client.get_channel(1144042386381606962)
            embed = discord.Embed(description=f"``>`` {guild.name}\n``>`` {guild.id}", color=discord.Color(2829617))
            await channel.send(embed=embed)
            return
        else:
            await self.client.get_guild(int(guild.id)).leave()
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("Function called")
        guild_id = member.guild.id

        cluster = pymongo.MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        db = cluster["WelcomeSystem"]
        welcome_config = db["Welcome Config"]

        config = welcome_config.find_one({"guild_id": guild_id})
        if config is None:
            print("No welcome config found")
            return

        welcome_message = config.get("welcome_message")
        welcome_channel_id = config.get("welcome_channel_id")

        if not welcome_channel_id:
            print(f"Welcome channel ID is not set for guild {guild_id}")
            return

        print(f"Sending welcome message to channel {welcome_channel_id} in guild {guild_id}")

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
