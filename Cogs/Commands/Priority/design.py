from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
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
    
class DesignCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_uri = None
        self.config = None  
        self.cluster = MongoClient(self.mongo_uri)
        
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.design_records = self.design_Db[self.config["collections"]["design"]["log_collection"]]

        





    @commands.hybrid_group(name="design", description=f"Design based commands")
    async def design(self, ctx):
        pass

    @design.command(name="log")
    async def designlog(self, ctx: commands.Context, price: int, customer: discord.Member, link,*, product: str):
        guild_id = ctx.guild.id
        existing_record = await self.fetch_design_config(guild_id)

        if not link:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you must specify a link.")

        if not existing_record:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. ")
        
        designer_role_id, designer_log_channel_id = await Base_Guild.fetch_design_config(ctx.guild.id)

        
        
        designer_channel = self.client.get_channel(designer_log_channel_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)
        
        if designer_channel is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. (no design channel)")
        
        if designer_role is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. (no designer role)" )
        
        if designer_role not in ctx.author.roles:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you are missing the required roles.")
        
        embed = discord.Embed(description=f"Greetings {customer.mention}! Your design has now been finished, please pay <:Roblox:1172789898898591764> **{price}** Robux by clicking this [link]({link}) and purchasing the item, once finished please let your designer know so that they can mark the design as finished!", color=discord.Color.dark_embed())
        await ctx.send(embed=embed, content=customer.mention)

        order_id = f"{ctx.author.id}{random.randint(1000,9999)}"
        log_Embed = discord.Embed(description=f"**Order Log**\n\n> **designer:** {ctx.author.mention}\n> **Product:** {product}\n> **Price:** {price}", color=discord.Color.dark_embed(), timestamp=discord.utils.utcnow())
        log_Embed.set_footer(text=f"Order ID: {order_id}")
        log_Embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        await designer_channel.send(embed=log_Embed)
        
        await Base_Guild.update_design_logs(order_id=order_id, customer_id=customer.id, designer_id=ctx.author.id, price=price, product=product)
        
                
        
        
        
    #@design.command(name=f"find", description=f"Find a design by a specific ID")
    #async def find(self, ctx: commands.Context)
        


            
        
        
        

        
        
        
        
        
        


    @designlog.autocomplete('link')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        guild_id = interaction.guild.id
        payment_links = await Base_Guild.fetch_payment_links(guild_id)

        choices = [
            app_commands.Choice(name=link, value=link) for link in payment_links if current.lower() in link.lower()
        ]
        
        if choices:
            return choices
        
        else:
            return "No Payment Links"
        
 
    

            

        
            
        
    

async def setup(client: commands.Bot) -> None:
    await client.add_cog(DesignCog(client))