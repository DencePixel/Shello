import pymongo
import os
from dotenv import load_dotenv
from Util.Yaml import Load_yaml
load_dotenv()


class BaseGuild:
    """
    Base class for a guild Object. 
    """
    def __init__(self):
        self.config = None
        self.mongo_uri = None
        
    async def initialize(self):
        """
        Initialize our yaml config
        """
        self.config = await Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        

        
    async def fetch_design_config(self, guild_id):
        """
        Function for getting design config for a guild
        
        Returns either the values or False
        """
        if self.config is None:
            await self.initialize()
        try:
            db = self.cluster[self.config["collections"]["design"]["database"]]
            design_config = db[self.config["collections"]["design"]["collection"]]

            guild_id = int(guild_id)

            existing_record = design_config.find_one({"guild_id": guild_id})

            if existing_record:
                designer_log_channel_id = existing_record.get("designer_log_channel_id")
                designer_role_id = existing_record.get("designer_role_id")
                return designer_role_id, designer_log_channel_id
            else:
                return False

        except Exception as e:
            return None, None
        
    async def fetch_payment_links(self, guild_id):
        
        """
        Function for getting payment links for a guild
        
        Returns either the values or a placeholder
        """
        if self.config is None:
            await self.initialize()
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        existing_record = self.payment_config.find_one({"guild_id": guild_id})

        if existing_record:
            links = existing_record.get("links", {})
            return [f"{name}" for name, link in links.items()]
        else:
            return ["No payment links exist"]
        
    async def update_design_logs(self, guild_id, data):
        """
        Function to update design logs for the guild
        
        Returns a boolean dependant on if it suceeded or not
        """
        pass
        
        
