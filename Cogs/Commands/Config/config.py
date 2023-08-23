import os
import discord
from discord.ext import commands
from discord import app_commands
import time
import traceback
import sqlite3
from random import randint
import random
import roblox
from roblox import Client
from Cogs.Commands.Config.Channels.Options.views import *
from Cogs.Commands.Config.options import *

import string
rclient = Client()

class Config(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.db_connection = None
        

    @commands.hybrid_group(invoke_without_command=True, name="setup")
    async def config(self, ctx):
        return
    
    
        
    
    @config.command(name=f"start")
    async def setup(
        self,
        ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            menu_dropdown = ModuleSelect(ctx)
            menu_dropdown_view = discord.ui.View()
            menu_dropdown_view.add_item(menu_dropdown)
            await ctx.send(view=menu_dropdown_view)
            
            
            

            
            
            
            
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Config(client))
