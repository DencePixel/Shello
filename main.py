import sys
sys.dont_write_bytecode = True
import discord
from discord import ui
from colorama import Back, Fore, Style
import time
import json
import platform
import requests
import importlib
import discord.ext
from discord.ext import commands
import traceback
from datetime import UTC
from urllib.parse import quote_plus
from discord import app_commands
from datetime import datetime, timedelta
from pytz import timezone
import os
from datetime import datetime
import datetime
import logging
import sqlite3
import discord
import glob
import string
import random
import asyncio
from jishaku import Jishaku
#


class BLERP(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or("$"), intents=intents)

        self.cogslist = ["Cogs.Commands.Config.config"]

    async def load_jishaku(self):
        await self.wait_until_ready()
        await self.load_extension('jishaku')

    async def setup_hook(self):
        self.loop.create_task(self.load_jishaku()) # Load Jishaku in the background


        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S GMT", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.YELLOW + self.user.name)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
        synced = await self.tree.sync()
        await self.tree.sync()
        print(prfx + " Slash CMD Synced " + Fore.YELLOW + str(len(synced)) + " Commands")
        print(prfx + " Bot is in " + Fore.YELLOW + str(len(self.guilds)) + " servers")

    
    async def on_connect(self):
        activity2 = discord.Activity(type=discord.ActivityType.watching, name=f"{str(len(self.guilds))} guilds")
        print("Connected to Discord Gateway!")
        await self.change_presence(activity=activity2)

    async def on_disconnect(self):
        print("Disconnected from Discord Gateway!")



client = BLERP()
client.setup_hook()

    

    


client.run("MTExMTkyNjY2MDc4NzM1MTU5Mw.GRH5Xp.uFLFe82ekJnmL2MUeQXKg7x6TUGfWTzF1brBqM")

