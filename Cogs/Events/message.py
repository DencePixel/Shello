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


class AutoResponder(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]

    async def fetch_channel(self, guild, channel_id):
        try:
            return await guild.fetch_channel(channel_id)
        except discord.HTTPException:
            return None

    async def on_message(self, message):
        if message.author.bot:
            return  

        guild_id = str(message.guild.id)

        cluster = pymongo.MongoClient(self.mongo_uri)
        db = cluster[self.config["collections"]["autoresponder"]["database"]]
        autoresponder_config = db[self.config["collections"]["autoresponder"]["collection"]]

        existing_record = autoresponder_config.find_one({"guild_id": guild_id})
        if existing_record:
            responses = existing_record.get("responses", [])

            for response in responses:
                trigger = response["trigger"].lower()
                content = message.content.lower()

                if trigger in content:
                    channel_id = response["channel_id"]
                    role_id = response["role_id"]

                    if channel_id == 0:
                        channel = message.channel
                    else:
                        guild = message.guild
                        channel = await self.fetch_channel(guild, channel_id)
                        if channel is None:
                            channel = message.channel

                    if role_id == 0 or discord.utils.get(message.author.roles, id=role_id):
                        await channel.send(response["response"])
        

        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(AutoResponder(client))
