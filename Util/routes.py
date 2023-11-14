import json

import discord
from discord.ext import commands, ipc
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server

import pymongo

class Routes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if not hasattr(self.bot, "ipc") or getattr(self.bot, "ipc") == None:
            self.bot.ipc = ipc.Server(self.bot, host="0.0.0.0", secret_key="SuperSecretKey", standard_port=5000, multicast_port=5001)

    async def cog_load(self) -> None:
        await self.bot.ipc.start()

    async def cog_unload(self) -> None:
        await self.bot.ipc.stop()
        self.bot.ipc = None       

    @Server.route()
    async def get_minimal_info(self, data: ClientPayload):
        """returns info about a user"""
        user = self.bot.get_user(int(data.user_id))
        if not user:
            return None

        return user._to_minimal_user_json()
    
    @Server.route()
    async def get_bot_guilds(self, data: ClientPayload):
        """returns a list of guild ids for the bots guilds"""
        guilds = [str(guild.id) for guild in self.bot.guilds]
        return json.dumps(guilds)
    
    @Server.route()
    async def get_shared_guilds(self, data: ClientPayload):
        """returns a list of all guilds where a user is a admin"""
        user = self.bot.get_user(int(data.user_id))
        if not user:
            return None
        
        shared = []
        for guild in self.bot.guilds:
            member = guild.get_member(user.id)
            if member and member.guild_permissions.administrator:
                shared.append(str(guild.id))

        return json.dumps(shared)

    @Server.route()
    async def get_guild(self, data: ClientPayload):
        """returns info about a guild"""
        guild = self.bot.get_guild(int(data.guild_id))
        if not guild:
            return None
        return json.dumps({"name": guild.name, "icon_url": guild.icon.url if guild.icon else None, "id": guild.id, "channel_count": len(guild.channels), "member_count": guild.member_count})

    @Server.route()
    async def check_if_admin(self, data: ClientPayload):
        """checks if a user is still admin in a guild"""
        guild = self.bot.get_guild(int(data.guild_id))
        admin = False
        if guild:
            member = guild.get_member(int(data.user_id))
            if member and member.guild_permissions.administrator:
                admin = True

        return json.dumps({"admin": admin})



async def setup(bot: commands.Bot):
    await bot.add_cog(Routes(bot=bot))