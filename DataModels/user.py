import pymongo
import os
import asyncio
import yaml
from dotenv import load_dotenv
from Util.Yaml import Load_yaml
load_dotenv()



class BaseUser:
    def __init__(self):
        self.config = None
        self.mongo_uri = None

    async def initialize(self):
        self.config = await Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]

    async def fetch_roblox_account(self, user_id):
        if self.config is None:
            await self.initialize()

        self.cluster = pymongo.MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config['collections']['Roblox']['database']]
        self.roblox_accounts = self.db[self.config['collections']['Roblox']['accounts_collection']]
        self.user_id = str(user_id)
        
        roblox_account = self.roblox_accounts.find_one({"discord_user_id": self.user_id})
        

        if roblox_account:
            return roblox_account.get("roblox_user_id")
        else:
            return None
