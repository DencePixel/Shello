import pymongo
import os
from dotenv import load_dotenv
from Util.Yaml import Load_yaml
import datetime

load_dotenv()


class BaseGuild:
    """
    Base class for a guild Object. 
    """
    def __init__(self):
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = pymongo.MongoClient(self.mongo_uri)
        

        

        
    async def fetch_design_config(self, guild_id):
        """
        Function for getting design config for a guild

        Returns either the values or False
        """
        try:
            connection = pymongo.MongoClient(self.mongo_uri)
            db = connection[self.config["collections"]["design"]["database"]]
            design_config = db[self.config["collections"]["design"]["config_collection"]]

            guild_id = int(guild_id)

            existing_record = design_config.find_one({"guild_id": guild_id})

            if existing_record:
                return existing_record
            else:
                return False

        except Exception as e:
            print(f"Error in fetch_design_config: {e}")
            return None, None

        
    async def fetch_payment_links(self, guild_id):
        
        """
        Function for getting payment links for a guild
        
        Returns either the values or a placeholder
        """

        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        existing_record = self.payment_config.find_one({"guild_id": guild_id})

        if existing_record:
            links = existing_record.get("links", {})
            return [f"{name}" for name, link in links.items()]
        else:
            return None
    
    
    async def update_design_logs(self, guild, order_id, designer_id, customer_id, price, product):
        """
        Function to update design logs for the guild
        
        Returns a boolean dependant on if it suceeded or not
        """
        self.design = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_records = self.design[self.config["collections"]["design"]["log_collection"]]
        try:
            record = {
                "guild_id": guild,
                "order_id": order_id,
                "designer_id": designer_id,
                "customer_id": customer_id,
                "price": price,
                "product": product,
                "timestamp": datetime.datetime.utcnow()
            }
            result = self.design_records.insert_one(record)
            return result.inserted_id 
        except Exception as e:
            print(f"Error inserting design record: {e}")
            return None
        
    async def get_feedback_channel(self, guild_id):
        """
        Function for getting the feedback channel for a guild

        Returns either the channel ID or None if not found
        """

        try:
            connection = pymongo.MongoClient(self.mongo_uri)
            db = connection[self.config["collections"]["design"]["database"]]
            feedback_collection = db[self.config["collections"]["design"]["feedback_config"]]

            guild_id = int(guild_id)

            existing_record = feedback_collection.find_one({"guild_id": guild_id})

            if existing_record:
                return existing_record.get("feedback_channel")
            else:
                return None

        except Exception as e:
            print(f"Error fetching feedback channel: {e}")
            return None
        
        
    async def get_suggestion_channel(self, guild_id):
        """
        Function for getting the suggestion channel for a guild

        Returns either the channel ID or None if not found
        """

        try:
            connection = pymongo.MongoClient(self.mongo_uri)
            db = connection[self.config["collections"]["suggestion"]["database"]]
            suggestion_config = db[self.config["collections"]["suggestion"]["config"]]

            guild_id = int(guild_id)

            existing_record = suggestion_config.find_one({"guild_id": guild_id})

            if existing_record:
                return existing_record.get("suggestion_channel")
            else:
                return None

        except Exception as e:
            print(f"Error fetching feedback channel: {e}")
            return None
    
    async def store_active_design(self, guild, channel, customer, designer, product, order_id, price):
        """
        Function for storing active designs
        """
        try:
            record = {
                "guild": guild,
                "order_id": order_id,
                "designer_id": designer,
                "customer_id": customer,
                "price": price,
                "product": product,
                "channel": channel,
                "timestamp": datetime.datetime.utcnow()
            }
            connection = pymongo.MongoClient(self.mongo_uri)
            db = connection[self.config["collections"]["design"]["database"]]
            active_designs_collection = db[self.config["collections"]["design"]["active_designs_collection"]]
            result = active_designs_collection.insert_one(record)
            return order_id 
        except Exception as e:
            print(f"Error inserting active design record: {e}")
            return None
        
    async def fetch_active_design(self, order_id):
        try:
            active_designs_collection = self.cluster[self.config["collections"]["design"]["database"]][self.config["collections"]["design"]["active_designs_collection"]]

            order_id_str = str(order_id)
            result = active_designs_collection.find_one({"order_id": order_id_str})
            return result
        except Exception as e:
            print("Error fetching active design:", e) 
            return None
        
        
    async def fetch_guild_currency(self, guild):
        try:
            currency_config = self.cluster[self.config["collections"]["Customization"]["database"]][self.config["collections"]["Customization"]["config_collection"]]

            result = currency_config.find_one({"guild_id": guild})
            if result is None:
                return "Robux"
            
            if result is not None:
                return result.get("custom_currency")
        
        except Exception as e:
            print("Error fetching active design:", e) 
            return None


    async def fetch_design(self, order_id):
        try:
            log_designs_collection = self.cluster[self.config["collections"]["design"]["database"]][self.config["collections"]["design"]["log_collection"]]
            return log_designs_collection.find_one({"order_id": order_id})
        except Exception as e:
            return None
        
        
    async def cancel_active_design(self, order_id):
        """
        Function for canceling an active design by order_id
        """
        try:
            connection = pymongo.MongoClient(self.mongo_uri)
            db = connection[self.config["collections"]["design"]["database"]]
            active_designs_collection = db[self.config["collections"]["design"]["active_designs_collection"]]

            order_id_str = str(order_id)
            query = {"order_id": order_id_str}

            result = active_designs_collection.delete_one(query)

            connection.close()

            return True

        except Exception as e:
            print(f"Error canceling active design: {e}")
            return False
        