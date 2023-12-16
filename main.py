import sys
sys.dont_write_bytecode = True
import discord
from discord.ext import commands
import asyncio
from Util.Yaml import Load_yaml
import pymongo
import os
import logging
from dotenv import load_dotenv
from importlib import reload, import_module
from Cogs.Events.Join import StaffJoinedButton

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

class SHELLO(commands.AutoShardedBot):
    def __init__(self):
        code = os.getenv("ENVIORMENT")
        if code.lower() == "production":
            prefix = ">>"
        else:
            prefix = ">"
        intents = discord.Intents.default()
        intents.message_content = True
        intents.message_content = False
        intents.presences = False
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            shard_count=shard_count
        )
        self.help_command = None

        self.cogslist = [
            "Cogs.Commands.setup",
            "Cogs.Events.error",
            "Cogs.Events.Join",
            "Cogs.Commands.Priority.design",
            "Util.routes",
            "Cogs.Commands.Priority.roblox",
            "Cogs.Commands.Priority.activity",
            "Cogs.Commands.Priority.feedback",
            "Cogs.Commands.Statistics.Ping",
            "Cogs.Commands.Priority.refund",
            "Cogs.Commands.Owner.sync",
            "Cogs.Commands.Priority.help",
            "Cogs.Commands.Priority.staff",
            "Cogs.Commands.Priority.suggest",
            "Cogs.Commands.Priority.alerts"
            ]

        self.cogs_last_modified = {cog: self.get_last_modified(cog) for cog in self.cogslist}

    async def is_owner(self, user: discord.User):
        if user.id in [
            856971748549197865,  # Mark
            795743076520820776,  # Bugsy
            937122696003747930, # Moyai
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
            if ext != "Util.routes":
                await self.load_extension(ext)
                logging.info(f"Cog {ext} loaded")

            if ext == "Util.routes":
                if os.getenv("ENVIORMENT").lower() == "production":
                    logging.info("IPC Cog loaded. Reason: Production ENV")
                    await self.load_extension(ext)
                if os.getenv("ENVIORMENT").lower() == "development":
                    logging.info("IPC Cog not loaded. Reason: Development ENV")

        await self.load_jishaku()
    async def on_connect(self):
        activity2 = discord.Activity(type=discord.ActivityType.playing, name="/config start || V1")
        logging.info("Connected to Discord Gateway!")
        await self.change_presence(activity=activity2)

    async def on_disconnect(self):
        logging.info("Disconnected from Discord Gateway")

    async def change_prefix(self, ctx, new_prefix):
        config = Load_yaml()
        mongo_uri = self.config["mongodb"]["uri"]
        prefixes_collection = pymongo.MongoClient(self.mongo_uri)

        await prefixes_collection.update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"guild_id": ctx.guild.id, "prefix": new_prefix}},
            upsert=True
        )

        self.guild_prefixes[ctx.guild.id] = new_prefix

        await self.process_commands(ctx.message)

    def get_last_modified(self, cog):
        cog_file = f"{cog.replace('.', '/')}.py"
        return os.path.getmtime(cog_file)

    async def reload_cogs(client):
        while True:
            try:
                await asyncio.sleep(5) 

                for cog in client.cogslist:
                    try:
                        last_modified = client.get_last_modified(cog)
                        if last_modified != client.cogs_last_modified[cog]:
                            reload_module = f"{cog}"
                            reload(import_module(reload_module))
                            client.cogs_last_modified[cog] = last_modified
                            await client.reload_extension(cog)
                    except Exception as e:
                        logging.error(f"Error reloading cog {cog}: {e}")

            except asyncio.CancelledError:
                break

async def run_function(token):
    client = SHELLO()

    @client.event
    async def on_command(ctx):
        if ctx.author.bot:
            return

    @client.command()
    async def prefix(self, ctx, new_prefix: str):
        pass

    await client.setup_hook()

    await asyncio.gather(
        client.start(token=token),
        SHELLO.reload_cogs(client)
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
