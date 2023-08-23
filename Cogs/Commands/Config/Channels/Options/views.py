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
from Cogs.Commands.Config.Channels.DesignLog.views import DesignLogChannel



class ChannelModuleSelect(discord.ui.Select):
    def __init__(self, interaction):
        self.interaction = interaction
        options = [
            discord.SelectOption(label=f"Design Logging", value="Design-Logs"),
            discord.SelectOption(label=f"Reviews", value="Reviews")
        ]
        super().__init__(placeholder='Select what module to configure.', options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.interaction.author.id != interaction.user.id:
            await interaction.response.send_message(f"<:Failed:1143843095994179675> This is not your dropdown!", ephemeral=True)
            return
        
        elif self.values[0] == "Design-Logs":
            embed = discord.Embed(title=f"Design Logs", description=f"Please select a channel for all completed designs to be logged in.", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            await interaction.response.send_message(f"Please select a **Design Logging Channel**.", embed=embed)
            design_logging_Dropdown = DesignLogChannel(self.interaction, interaction)
            design_logging_view = discord.ui.View()
            design_logging_view.add_item(design_logging_Dropdown)
            await interaction.edit_original_response(view=design_logging_view)
            
        
        
            
        