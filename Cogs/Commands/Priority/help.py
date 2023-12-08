from typing import Any
from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
from discord.app_commands import Choice
from pymongo import MongoClient
from DataModels.guild import BaseGuild
import os
from DataModels.user import BaseUser
from dotenv import load_dotenv
load_dotenv()
import random
from Util.Yaml import Load_yaml

Base_User = BaseUser()
Base_Guild = BaseGuild()

class HelpCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(name="help", description="Get help on a certain module")
    @app_commands.describe(module='The module you need help with')
    @app_commands.choices(module=[
        Choice(name='Designs', value='designs'),
        Choice(name='Payment', value='payment'),
        Choice(name='Refunds', value='refunds'),
        Choice(name=f"Activity", value=f"quota"),
    ])
    async def help(self, ctx: commands.Context, module: str):
        if module.lower() == "designs":
            embed = discord.Embed(
                title="Design Module",
                description="The Design Module allows designers to manage design-related activities.\n"
                            "Here are some available commands:",
                color=discord.Color.light_embed()
            )
            
            embed.add_field(
                name="Start",
                value="Start the process of creating a design.\n"
                      "Usage: `/design start @customer <price> <product>`",
                inline=False
            )

            embed.add_field(
                name="Contribute",
                value="Give the customer an update on an active order.\n"
                      "Usage: `/design contribute <order_id>`",
                inline=False
            )
            
            embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)

            return await ctx.send(embed=embed)
            
        elif module.lower() == "payment":
            embed = discord.Embed(
                title="Payment Module",
                description="The Payment module allows designers to assign a payment link to any active design's they may have.\n"
                            "Here is how to use the module:",
                color=discord.Color.light_embed()
            )
            
            embed.add_field(
                name="Setting Up",
                value="To use designs you will need to setup a payment link within the config.\n"
                      "Usage: `/config start > Payment > Add a Link`",
                inline=False
            )

            embed.add_field(
                name="Utilizing the Module",
                value="To use the Module, you need to create a design then mark it as finished. You can then select one of your payment links to be sent to the customer which is how you will recieve your profits.\n"
                      "Usage: `/design contribute <order_id> > Order Finish > Select a payment link`",
                inline=False
            )
            
            embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)

            return await ctx.send(embed=embed)
        
        elif module.lower() == "refunds":
            embed = discord.Embed(
                title="Refunds Module",
                description="The Refunds Module allows users to post a refund request for any designs that were previously logged.\n"
                            "Here is how to use the module:",
                color=discord.Color.light_embed()
            )
            
            embed.add_field(
                name="Request a Refund",
                value="Request a refund for a design you received.\n"
                      "Usage: `/refund request <order_id> <reason>`",
                inline=False
            )

            embed.add_field(
                name="Check Refund Status",
                value="Check the status of an active refund request.\n"
                      "Usage: `/refund status <order_id>`",
                inline=False
            )

            embed.add_field(
                name="Manage Refund",
                value="Manage a refund request.\n"
                      "Usage: `/refund admin <order_id>`",
                inline=False
            )
            
            embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)

            return await ctx.send(embed=embed)
        
        elif module.lower() == "activity":
            embed = discord.Embed(
                title="Activity Module",
                description="The Activity Module allows staff members to manage and monitor the activity of your designers.\n"
                            "Here is how to use the module:",
                color=discord.Color.light_embed()
            )
            
            
            embed.add_field(
                name="Setting Up",
                value="To use Activity you will need to setup the Activity Module within the config.\n"
                      "Usage: `/config start > Activity`",
                inline=False
            )

            embed.add_field(
                name="Leaderboard",
                value="View a weekly leaderboard showing who has and who hasn't passed their design quota.\n"
                      "Usage: `/activity leaderboard`",
                inline=False
            )

            embed.add_field(
                name="User Quota",
                value="Check if a specific user or yourself has passed the design quota.\n"
                      "Usage: `/activity user [@mention]`",
                inline=False
            )

            embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)

            return await ctx.send(embed=embed)
        
        
        else:
            await ctx.send(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** I can't find that module!")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(HelpCog(client))
