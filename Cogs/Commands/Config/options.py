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
from Cogs.Commands.Config.Channels.Options.views import *
from Cogs.Commands.Config.Permissions.Options.views import *


class ModuleSelect(discord.ui.Select):
    def __init__(self, interaction):
        self.interaction = interaction
        options = [
            discord.SelectOption(label=f"Channels", value="channels"),
            discord.SelectOption(label=f"Role Permissions", value="roles")
        ]
        super().__init__(placeholder='Select what module to configure.', options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.interaction.author.id != interaction.user.id:
            await interaction.response.send_message(f"<:Failed:1143843095994179675> This is not your dropdown!", ephemeral=True)
            return
        
        elif self.values[0] == "channels":
            channel_dropdown = ChannelModuleSelect(self.interaction)
            channel_dropdown_view = discord.ui.View()
            channel_dropdown_view.add_item(channel_dropdown)
            embed = discord.Embed(description=f"Please select a channel to configure!", color=discord.Color.dark_embed())
            await interaction.response.send_message(embed=embed, view=channel_dropdown_view)
            
        elif self.values[0] == "roles":
            role_dropdown = RoleModuleSelect(self.interaction)
            role_dropdown_view = discord.ui.View()
            role_dropdown_view.add_item(role_dropdown)
            embed = discord.Embed(description=f"Please select a permission to configure!", color=discord.Color.dark_embed())
            await interaction.response.send_message(embed=embed, view=role_dropdown_view)