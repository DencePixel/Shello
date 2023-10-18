import sys
sys.dont_write_bytecode = True
import discord
from discord import ui
from pymongo import MongoClient
from utils import replace_variable_welcome
import discord.ext
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from pytz import timezone
from Cogs.Utils.paginator import Simple
from datetime import datetime

import discord

from jishaku import Jishaku


class SHELLO(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or("t$"), intents=intents)

        self.cogslist = ["Cogs.Commands.setup",
                         "Cogs.Events.error",
                         "Cogs.Events.Join",
                         "Cogs.Master.Servers",
                         "Cogs.Commands.Priority.design",
                         "Cogs.Commands.Utils.routes"]
    async def load_jishaku(self):
        await self.wait_until_ready()
        await self.load_extension('jishaku')

    async def on_ready(self):

        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        await self.tree.sync()

        for ext in self.cogslist:
            await self.load_extension(ext)
            print(f"Cog {ext} loaded")
            
        await self.load_jishaku()

    
    async def on_connect(self):
        activity2 = discord.Activity(type=discord.ActivityType.watching, name=f"Near Release!")
        print("Connected to Discord Gateway!")
        await self.change_presence(activity=activity2)

    async def on_disconnect(self):
        print("Disconnected from Discord Gateway!")



client = SHELLO()
client.setup_hook()

import discord

correct_password = [3, 7, 6]
current_entry = []

class PasswordView(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.password_entered = False 

        for i in range(1, 10):
            button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label=str(i),
                custom_id=f"button_{i}"
            )
            button.callback = self.button_callback
            self.add_item(button)

        check_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Check",
            custom_id="button_check"
        )
        check_button.callback = self.check_callback
        self.add_item(check_button)

        reset_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Reset",
            custom_id="button_reset"
        )
        reset_button.callback = self.reset_callback
        self.add_item(reset_button)

        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancel",
            custom_id="button_cancel",
            disabled=False  
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)

    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        custom_id = interaction.data["custom_id"]
        number = int(custom_id.split("_")[1])
        current_entry.append(number)

    async def check_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.password_entered:
            return
        
        if current_entry == correct_password:
            self.password_entered = True 
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id != "button_reset" and item.custom_id != "button_cancel":
                    item.disabled = True
            current_entry.clear()
            await self.message.edit(content="Password Correct!", view=self)
        else:
            await self.message.edit(content="Password Incorrect")
            current_entry.clear()

    async def reset_callback(self, interaction: discord.Interaction):
        current_entry.clear()
        await interaction.response.defer()
        self.password_entered = False 
        updated_view = PasswordView(message=self.message)
        await self.message.edit(view=updated_view)

    async def cancel_callback(self, interaction: discord.Interaction):
        current_entry.clear()
        await interaction.response.defer()
        await self.message.edit(content="Finished.", view=None, embed=None)

@client.command()
async def j(ctx):
    message = await ctx.send(f"Password Entry:")
    view = PasswordView(message=message)
    await message.edit(view=view, content=None)



            
client.run("MTA2ODI2MTc0NTg2NjU3NTk4Mg.GR-yiu.mAbiydsvZP80r-f7uX06cyEp7e4LBHe9kut0KE")

