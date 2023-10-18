from discord import app_commands
from discord import Color
from discord.ext import commands
import discord.ext
from roblox import Client
from discord import app_commands
from discord import Color
import discord
from discord.ext import commands
import discord.ext
from datetime import timedelta
from pymongo import MongoClient
from Cogs.Commands.Config.view import SelectView
from Cogs.emojis import approved_emoji, denied_emoji

roclient = Client()

roclient.set_token("") # set the roblox token



    
    

            


        

    
class Config(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cluster = MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        
    @commands.hybrid_group(name="config", description=f"Config based commands")
    async def config(self, ctx):
        pass
    
    @config.command(name="start")
    async def start(self, ctx: commands.Context):
        if ctx.author.guild_permissions.manage_guild:
            message = await ctx.sen(f"{approved_emoji} **{ctx.author.display_name},** you are now setting up Shello!")
            TheView = SelectView(ctx=ctx, message=message)
            await message.edit(view=TheView)
            
        else:
            return await ctx.send(f"{denied_emoji} **{ctx.author.display_name},** you do not have the required permissions to do this.")

            

        
            
        
    

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Config(client))