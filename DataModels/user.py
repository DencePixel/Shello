import pymongo
import os
from dotenv import load_dotenv
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")


class BaseUser:
    """
    Base class for a user Object. 
    """
    def __init__(self):
        self.mongo_uri = mongo_uri

    async def fetch_roblox_account(self, user_id):
        """
        Retrieve the Roblox user ID associated with the provided Discord user ID.
        """
        
        self.cluster = pymongo.MongoClient(self.mongo_uri)
        self.db = self.cluster["Roblox"]
        self.roblox_accounts = self.db["accounts"]
        self.user_id = str(user_id) 

        roblox_account = self.roblox_accounts.find_one({"discord_user_id": self.user_id})

        if roblox_account:
            return roblox_account.get("roblox_user_id")
        else:
            return None

