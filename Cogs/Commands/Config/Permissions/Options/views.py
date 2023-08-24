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
from Cogs.Commands.Config.Permissions.Design.views import *



class RoleModuleSelect(discord.ui.Select):
    def __init__(self, interaction):
        self.interaction = interaction
        options = [
            discord.SelectOption(label=f"Design Permissions", value="Design-roles"),
            discord.SelectOption(label=f"Review Permissions", value="Review-roles")
        ]
        super().__init__(placeholder='Select what module to configure.', options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.interaction.author.id != interaction.user.id:
            await interaction.response.send_message(f"<:Failed:1143843095994179675> This is not your dropdown!", ephemeral=True)
            return
        
        elif self.values[0] == "Design-roles":
            embed = discord.Embed(title=f"Design Logs", description=f"Please select the **Designer** role!", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            await interaction.response.send_message(f"Please select a **Designer role**.", embed=embed)
            role_logging_dropdown = DesignPermissionsRole(self.interaction, interaction)
            role_Logging_view = discord.ui.View()
            role_Logging_view.add_item(role_logging_dropdown)
            await interaction.edit_original_response(view=role_Logging_view)
            
        
        
            
        