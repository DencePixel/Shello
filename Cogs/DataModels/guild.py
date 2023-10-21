import pymongo

class BaseGuild:
    def __init__(self):
        self.mongo_uri = "mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/"
        self.cluster = pymongo.MongoClient(self.mongo_uri)

        
    async def fetch_design_config(self, guild_id):
        """
        Function for getting design config for a guild
        
        Returns either the values or False
        """
        try:
            db = self.cluster["DesignSystem"]
            design_config = db["design config"]

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
        self.payment_db = self.cluster["PaymentLinkSystem"]
        self.payment_config = self.payment_db["Payment Config"]
        existing_record = self.payment_config.find_one({"guild_id": guild_id})

        if existing_record:
            links = existing_record.get("links", {})
            return [f"{name}" for name, link in links.items()]
        else:
            return ["No payment links exist"]
        
    async def guild_is_blacklisted(self, guild_id):
        """
        Function for checking if a guild is blacklisted
        
        Returns a boolean
        """
        self.Master = self.cluster["Master"]
        self.Blacklists = self.Master["Blacklists"]
        existing_record = self.Blacklists.find_one({"guild_id": guild_id})
        
        if existing_record:
            return True
        elif not existing_record:
            return False
        
        else:
            return False
        
        
        
