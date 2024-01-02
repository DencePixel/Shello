import asyncio
import datetime
import typing
import aiohttp
import discord
import pytz
import roblox.users
from discord import Embed, InteractionResponse, Webhook
from discord.ext import commands
from zuid import ZUID
import re
from Util.helpers import interaction_check_failure



class YesNoMenu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    async def common_button_action(self, interaction: discord.Interaction, value: bool):
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = value
        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await self.common_button_action(interaction, True)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction_check_failure(interaction.followup)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await self.common_button_action(interaction, False)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction_check_failure(interaction.followup)


class CustomDropdown(discord.ui.Select):
    def __init__(self, user_id, options: list, limit=1):
        self.user_id = user_id
        optionList = []

        for option in options:
            if isinstance(option, str):
                optionList.append(
                    discord.SelectOption(
                        label=option.replace("_", " ").title(), value=option
                    )
                )
            elif isinstance(option, discord.SelectOption):
                optionList.append(option)

        super().__init__(
            placeholder="Select an option",
            min_values=1,
            max_values=limit,
            options=optionList,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            await interaction.response.defer()
            if len(self.values) == 1:
                self.view.value = self.values[0]
            else:
                self.view.value = self.values
            self.view.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await interaction_check_failure(interaction.followup)