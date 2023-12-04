import discord
import pymongo
from pymongo import MongoClient
from Util.Yaml import Load_yaml


import discord
from discord.ext import commands
from DataModels.guild import BaseGuild
from roblox import Client

Base_Guild = BaseGuild()




class StaffCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.roblox_client = Client()
        
        
    @commands.hybrid_group(name="staff", description=f"Staff based commands")
    async def staffgroup(self, ctx):
        pass
        
        
    @staffgroup.command(name="database", description="Get a list of members with the designer role")
    async def designer_list(self, ctx: commands.Context):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        existing_record = await Base_Guild.fetch_design_config(guild_id=ctx.guild.id)
        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** you need to set up the design module.")

        designer_role_id = existing_record.get("staff_role_id")
        designer_role = ctx.guild.get_role(designer_role_id)

        if not designer_role:
            return await message.edit(content=f"<:Denied:1163095002969276456> Staff role not found. Please check your configuration.")


        members_with_role = sorted(designer_role.members, key=lambda member: (-member.top_role.position, member.name))

        embed = discord.Embed(
            title=f"Staff Database for {ctx.guild.name}", color=discord.Color.light_embed(),
            description=f""
        )
        embed.set_footer(text=f"Staff Module")

        for member in members_with_role:
            embed.description += f"\n{member.mention}"

        await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** here is the staff list.",embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(StaffCog(client))