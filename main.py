import sys

sys.dont_write_bytecode = True
import io
import sqlite3
import json
from jsonschema import validate, exceptions
import roblox
import asyncio
import discord
import discord.ext
from typing import Literal, Optional
from discord import app_commands
import datetime
import discord.ext
from discord.ext import commands

import os



class BLERP(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or("$"), intents=intents)

        self.cogslist = ["Cogs.Commands.Config.config"]
    async def load_jishaku(self):
        await self.wait_until_ready()
        await self.load_extension('jishaku')

    async def on_ready(self):

        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
        await self.tree.sync()

        for ext in self.cogslist:
            await self.load_extension(ext)
            
        await self.load_jishaku()

    
    async def on_connect(self):
        activity2 = discord.Activity(type=discord.ActivityType.watching, name=f"{str(len(self.guilds))} guilds")
        print("Connected to Discord Gateway!")
        await self.change_presence(activity=activity2)

    async def on_disconnect(self):
        print("Disconnected from Discord Gateway!")



client = BLERP()
client.setup_hook()

    

    
@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
client.run("MTExMTkyNjY2MDc4NzM1MTU5Mw.GRH5Xp.uFLFe82ekJnmL2MUeQXKg7x6TUGfWTzF1brBqM")

