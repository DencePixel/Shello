import os
import discord
from discord.ext import commands
from discord import app_commands
import string
from roblox import Client
rclient = Client()

import pymongo

rclient = Client()

class Servers(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_client = pymongo.MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        self.db = self.mongo_client["Master"]
        self.servers_collection = self.db["Servers"]

    @commands.group(invoke_without_command=True, name="server")
    async def server(self, ctx):
        return

    @server.command(name="add")
    async def add(self, ctx: commands.Context, server_id: int):
        shello_guild = self.client.get_guild(1158057497274368102)
        user = shello_guild.get_member(ctx.author.id)
        if user:
            shello_role = shello_guild.get_role(1158067036065366078)
            if shello_role:
                if shello_role in ctx.author.roles:
                    await ctx.message.delete()
                    embed = discord.Embed(title="Congratulations!", description="Thank you for using shello, at any time if the bot is removed please just add it back!", color=discord.Color.green())
                    log_embed = discord.Embed(description=f"``Server: `` {server_id}", color=discord.Color.dark_embed())
                    log_embed.set_author(name="Shello", icon_url=ctx.author.display_avatar.url)
                    channel = shello_guild.get_channel(1158103780445917304)

                    self.servers_collection.insert_one({"guild_id": server_id})
                    await ctx.send(embed=embed)
                    await channel.send(embed=log_embed)

    @server.command(name="lookup")
    async def lookup(self, ctx: commands.Context, server_id: int):
        shello_guild = self.client.get_guild(1158057497274368102)
        user = shello_guild.get_member(ctx.author.id)
        if user:
            shello_role = shello_guild.get_role(1158067036065366078)
            if shello_role:
                if shello_role in user.roles:
                    existing_server = self.servers_collection.find_one({"guild_id": server_id})

                    if existing_server:
                        embed = discord.Embed(color=discord.Color.dark_embed(), description=f"``{server_id}`` has purchased premium before!", timestamp=discord.utils.utcnow())
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(color=discord.Color.dark_embed(), description=f"``{server_id}`` has not purchased premium before!", timestamp=discord.utils.utcnow())
                        await ctx.send(embed=embed)

    @server.command(name="remove")
    async def remove(self, ctx: commands.Context, server_id: int):
        shello_guild = self.client.get_guild(1143842566555582516)
        user = shello_guild.get_member(ctx.author.id)
        if user:
            shello_role = shello_guild.get_role(1144027935792177202)
            if shello_role:
                if shello_role in ctx.author.roles:
                    existing_server = self.servers_collection.find_one({"guild_id": server_id})

                    if existing_server:
                        self.servers_collection.delete_one({"guild_id": server_id})
                        await self.client.get_guild(int(server_id)).leave()
                        embed = discord.Embed(color=discord.Color.dark_embed(), description=f"``{server_id}`` has been removed from the database and I have left.", timestamp=discord.utils.utcnow())
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(color=discord.Color.dark_embed(), description=f"``{server_id}`` was not found in the database.", timestamp=discord.utils.utcnow())
                        await ctx.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Servers(client))
