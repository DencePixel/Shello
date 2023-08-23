import os
from typing import Any
import discord
from discord.ext import commands
import time
import traceback
import sqlite3
from random import randint
import random
from discord.interactions import Interaction
import roblox
from roblox import Client
import io
import string
from Cogs.Commands.Config.Channels.Options.views import ChannelModuleSelect


class gi(discord.ui.Select):
    def __init__(self, interaction):
        self.interaction = interaction
        options = [
            discord.SelectOption(label=f"Channels", value="Channels"),
            discord.SelectOption(label=f"Permissions", value="Permissions")
        ]
        super().__init__(placeholder='Select what module to configure.', options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.interaction.author.id != interaction.user.id:
            await interaction.response.send_message(f"<:Failed:1143843095994179675> This is not your dropdown!", ephemeral=True)
            return
        
        elif self.values[0] == "Channels":
            embed = discord.Embed(title=f"Channels", description=f"Please select a module.", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            await interaction.response.send_message(f"Please select a **module**.", embed=embed)
            channels_logging_dropdown = ChannelModuleSelect(self.interaction)
            channels_logging_view = discord.ui.View()
            channels_logging_view.add_item(channels_logging_dropdown)
            await interaction.edit_original_response(view=channels_logging_view)
            
        
        
            
        