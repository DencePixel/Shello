import sys
sys.dont_write_bytecode = True
import discord
from discord import ui
import discord.ext
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import os
import logging
from Util.remote import NetworkServer
import threading
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)


from jishaku import Jishaku

class SHELLO(commands.AutoShardedBot):
    def __init__(self):

        intents = discord.Intents().all()
        super().__init__(
            command_prefix=commands.when_mentioned_or("$$"),
            intents=intents,
            shard_count=shard_count  
        )

        self.cogslist = ["Cogs.Commands.setup",
                         "Cogs.Events.error",
                         "Cogs.Events.Join",
                         "Cogs.Commands.Priority.design",
                         "Util.routes",
                         "Cogs.Commands.Roblox.link"]
        
    async def is_owner(self, user: discord.User):
        if user.id in [
            856971748549197865, # Mark
            


        ]:
            return True

        return await super().is_owner(user)

    async def load_jishaku(self):
        await self.wait_until_ready()
        await self.load_extension('jishaku')

    async def setup_hook(self):
        pass

    async def on_ready(self):
        logging.info(f'Logged in as {self.user} (ID: {self.user.id})')


        for ext in self.cogslist:
            if ext != "Utils.routes":
                try:
                    await self.load_extension(ext)
                    logging.info(f"Cog {ext} acknowledged")
                except Exception as e:
                    logging.error(f"Error loading cog {ext}: {e}")
                        
            if ext == "Utils.routes":
                if os.getenv("ENVIORMENT").lower() == "production":
                    logging.info("IPC Cog loaded. Reason: Production ENV")
                    await self.load_extension(ext)
                if os.getenv("ENVIORMENT").lower() == "development":
                    logging.info("IPC Cog not loaded. Reason: Development ENV")


                        

        await self.load_jishaku()

    async def on_connect(self):
        activity2 = discord.Activity(type=discord.ActivityType.watching, name="Near Release!")
        logging.info("Connected to Discord Gateway!")
        await self.change_presence(activity=activity2)

    async def on_disconnect(self):
        logging.info("Disconnected from Discord Gateway")




async def run_function(token, network_server):
    client = SHELLO()
    
    @client.event
    async def on_command(ctx):
        if ctx.author.bot:
            return
    
        return
    
    await client.setup_hook()
    
    await asyncio.gather(
        client.start(token=TOKEN),
    )

if __name__ == "__main__":
    try:
        shard_count = int(os.getenv("SHARD_COUNT", 1))
    except ValueError:
        shard_count = 1
        logging.error(f"Incorrect value for shards. Automatically set to {shard_count}")

    if os.getenv("ENVIORMENT").lower() == "production" or os.getenv("ENVIORMENT").lower() == "development":
        TOKEN = os.getenv("PRODUCTION_BOT_TOKEN" if os.getenv("ENVIORMENT") == "production" else "DEVELOPMENT_BOT_TOKEN")
        
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(run_function(token=TOKEN))
        except KeyboardInterrupt:
            loop.run_until_complete(SHELLO.close())
            loop.close()
    else:
        logging.error("Invalid environment option. Please either use development or production.")