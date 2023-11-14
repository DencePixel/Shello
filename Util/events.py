import discord
import random
from discord import Embed
from discord.ext import commands
from Cogs.emojis import *
import aiohttp

class Events(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
    pass


            
        

        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Events(client))
