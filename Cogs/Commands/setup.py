from discord import app_commands
from discord import Color
from discord.ext import commands
import discord.ext
from roblox import Client
from discord import app_commands
from discord import Color
import discord
from discord.ext import commands
import motor.motor_asyncio
import discord.ext
from Util.Yaml import Load_yaml
from datetime import timedelta
from discord import app_commands
from discord.app_commands import Choice
from Cogs.Commands.Config.view import SelectView
from Cogs.emojis import approved_emoji, denied_emoji

roclient = Client()

roclient.set_token("")



    
    

            


        

    
class Config(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        
    @commands.hybrid_group(name="config", description=f"Config based commands")
    async def config(self, ctx):
        pass
    
    @config.command(name="start", description=f"Configure the current guild")
    async def start(self, ctx: commands.Context):
        if ctx.author.guild_permissions.manage_guild:
            message = await ctx.send(f"{approved_emoji} **{ctx.author.display_name},** you are now setting up Shello!")
            TheView = SelectView(ctx=ctx, message=message)
            await message.edit(view=TheView)
            
        else:
            return await ctx.send(f"{denied_emoji} **{ctx.author.display_name},** you do not have the required permissions to do this.")
        
    @config.command(name=f"remove", description=f"Remove the config for this guild")
    @app_commands.choices(module=[
        Choice(name='Designs', value='design'),
        Choice(name='Payment', value='payment'),
        Choice(name='Suggestions', value='suggestions'),
        Choice(name=f"Welcoming", value=f"welcome"),
        Choice(name=f"Leaves", value=f"leaves"),
    ])
    async def removeconfig(self, ctx: commands.Context, module: str):
        if ctx.guild.owner_id != ctx.author.id:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** only the guild owner can do this.")

        if module.lower() == "design":
            database = self.cluster[self.config["collections"]["design"]["database"]]
            collection = database[self.config["collections"]["design"]["config_collection"]]
        elif module.lower() == "suggestions":
            database = self.cluster[self.config["collections"]["suggestion"]["database"]]
            collection = database[self.config["collections"]["suggestion"]["config"]]
        elif module.lower() == "payment":
            database = self.cluster[self.config["collections"]["payment"]["database"]]
            collection = database[self.config["collections"]["payment"]["collection"]]
        elif module.lower() == "welcome":
            database = self.cluster[self.config["collections"]["welcome"]["database"]]
            collection = database[self.config["collections"]["welcome"]["collection"]]
            
        elif module.lower() == "quota":
            database = self.cluster[self.config["collections"]["Leaves"]["database"]]
            collection = database[self.config["collections"]["Leaves"]["config"]]
        else:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** invalid module specified.")

        config_data = await collection.find_one({"guild_id": ctx.guild.id})
        if config_data is None:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** there is no configuration for this guild in the specified module.")

        try:
            await collection.delete_one({"guild_id": ctx.guild.id})
            return await ctx.send(content=f"{approved_emoji} **{ctx.author.display_name},** I have successfully deleted the {module} config for this guild.")
        except:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** I was unable to delete the {module} config for this guild.")
            
            
            

            
            

        
            
        
    

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Config(client))