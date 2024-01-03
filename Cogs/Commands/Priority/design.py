from typing import Any
from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
from discord.interactions import Interaction
from motor.motor_asyncio import AsyncIOMotorClient
from DataModels.guild import BaseGuild
import os

from DataModels.user import BaseUser
from dotenv import load_dotenv
load_dotenv()
import random
from Cogs.emojis import approved_emoji, denied_emoji, alert_emoji
from Util.Yaml import Load_yaml


Base_User = BaseUser()
Base_Guild = BaseGuild()

class OrderPaidButton(discord.ui.Button):
    def __init__(self, author, message, order_id):
        super().__init__(style=discord.ButtonStyle.gray, label="Paid")
        self.message = message
        self.order_id = order_id
        
        self.author = author
    async def callback(self, interaction: discord.Interaction):
        from Cogs.Commands.Config.view import SelectView

        if self.author.id != interaction.user.id:
            return await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** this is not your view.", ephemeral=True)
        

        await interaction.response.defer()
        
        order = await Base_Guild.fetch_active_design(self.order_id)
        if not order:
            pass
        
        
        customer = order.get("customer_id")
        designer = order.get("designer_id")
        if interaction.user.id != designer:
            return await self.message.edit(content=f"{denied_emoji} **{interaction.user.mention},** only the designer can do this.", view=None, embed=None)
        price = order.get("price")
        product = order.get("product")
        
        embed = discord.Embed(title=f"Order Finished",color=discord.Color.light_embed() ,description=f"The following order has been marked as paid.\n\n**Order {self.order_id}**\n<:Shello_Right:1164269631062691880> **Customer:** <@!{customer}>\n<:Shello_Right:1164269631062691880> **Designer:** <@!{designer}>\n<:Shello_Right:1164269631062691880> **Product:** {product}\n<:Shello_Right:1164269631062691880> **Price:** {price}", timestamp=discord.utils.utcnow())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        
        self.disabled = True
            
        await self.message.edit(view=self.view, embed=embed, content=f"{approved_emoji} Marked as paid by **{interaction.user.display_name}.**")
        existing_record = await Base_Guild.fetch_design_config(interaction.guild.id)
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_channel = interaction.guild.get_channel(designer_log_channel_id)
        await designer_channel.send(embed=embed)
        cancel = await Base_Guild.cancel_active_design(order_id=self.order_id)
        if cancel is True:
            log = await Base_Guild.update_design_logs(guild=interaction.guild.id,order_id=self.order_id, designer_id=designer, customer_id=customer, price=price, product=product)
            await interaction.followup.send(f"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully finished the design.", ephemeral=True)      
            
            

        
        

class ContributeModal(discord.ui.Modal):
    def __init__(self, question_name, title, question_placeholder,status, order_id):
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.status = status
        self.order_id = order_id
        super().__init__(title=title)
            
        self.Message = discord.ui.TextInput(
            label=question_name,
            style=discord.TextStyle.short,
            placeholder=question_placeholder,
            required=True,
            max_length=500,
        )
        
        self.add_item(self.Message)
        
    async def on_submit(self, interaction: discord.Interaction):
        data = await Base_Guild.fetch_active_design(self.order_id)
        if not data:
            return await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** I can't find that Order!", ephemeral=True)
        if self.status == "update":

                
            order_channel = interaction.guild.get_channel(data['channel'])
            designer = interaction.guild.get_member(data["designer_id"])
            customer = interaction.guild.get_member(data["customer_id"])
            message_Embed = discord.Embed(title=f"Design Contribution", description=f"{self.Message.value}", color=discord.Color.dark_embed())
            message_Embed.set_author(icon_url=interaction.user.display_avatar.url, name=interaction.user.display_name)
            message_Embed.set_footer(text=f"Design contributed to by {interaction.user.display_name}")
            await order_channel.send(embed=message_Embed, content=f"<:Approved:1163094275572121661> **{customer.mention}**, there is a new contribution to your design!")  
            try:
                await customer.send(embed=message_Embed, content=f"<:Approved:1163094275572121661> **{customer.display_name}**, there is a new contribution to your design!") 
            except Exception as e:
                return await interaction.response.send_message(f"<:Alert:1163094295314706552> **{interaction.user.display_name},** I couldn't message that user.", ephemeral=True) 
            await interaction.response.send_message(f"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully sent the customer your contribution.", ephemeral=True) 
            
        elif self.status == "cancel":
            await interaction.response.defer()
            data = await Base_Guild.fetch_active_design(self.order_id)
            designer = interaction.guild.get_member(data["designer_id"])
            customer = interaction.guild.get_member(data["customer_id"])
            price = data["price"]
            product = data["product"]
            cancel = await Base_Guild.cancel_active_design(order_id=self.order_id)
            if cancel is False:
                return await interaction.followup.send(embed=message_Embed, content=f"<:Denied:1163095002969276456> **{customer.mention}**, I can't cancel your Order!", ephemeral=True)
            
            await interaction.followup.send(f"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully cancelled design.", ephemeral=True)      
            order_channel = interaction.guild.get_channel(data['channel'])
            designer = interaction.guild.get_member(data["designer_id"])
            customer = interaction.guild.get_member(data["customer_id"])
            message_Embed = discord.Embed(title=f"Design Cancelled", description=f"{self.Message.value}", color=discord.Color.dark_embed())
            message_Embed.set_author(icon_url=interaction.user.display_avatar.url, name=interaction.user.display_name)
            message_Embed.set_footer(text=f"Design cancelled by {interaction.user.display_name}")
            await order_channel.send(embed=message_Embed, content=f"<:Denied:1163095002969276456> **{customer.mention}**, your design has been cancelled.")      
            try:
                await customer.send(embed=message_Embed, content=f"<:Denied:1163095002969276456> **{customer.display_name}**, your design has been cancelled.") 
            except Exception as e:
                return await interaction.followup.send(f"<:Alert:1163094295314706552> **{interaction.user.display_name},** I couldn't message that user.", ephemeral=True) 
            existing_record = await Base_Guild.fetch_design_config(interaction.guild.id)
            designer_log_channel_id = existing_record.get("designer_log_channel_id")
            designer_role_id = existing_record.get("designer_role_id")
            staff_Role_id = existing_record.get("staff_role_id")
            designer_channel = interaction.guild.get_channel(designer_log_channel_id)

        
            info_embed = discord.Embed(color=discord.Color.dark_embed(), title="Design Cancelled", description=f"<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Price:** {price}\n<:Shello_Right:1164269631062691880> **Product:** {product}")
            await designer_channel.send(embed=info_embed, content=f"<:Approved:1163094275572121661> cancelled by **{interaction.user.mention}**")

class DesignFinishedOptions(discord.ui.Select):
    def __init__(self, author, order_id, guild_id, **kwargs):
        self.author = author
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.order_id = order_id
        self.guild_id = guild_id
        super().__init__(placeholder='Please select a payment link.', min_values=1, max_values=1, **kwargs)

    @classmethod
    async def create(cls, author, order_id, guild_id, **kwargs):
        self = cls(author, order_id, guild_id, **kwargs)
        await self.fetch_payment_links()
        return self

    async def fetch_payment_links(self):
        payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        payment_config = payment_db[self.config["collections"]["payment"]["collection"]]
        existing_record = await payment_config.find_one({"guild_id": self.guild_id})

        if existing_record:
            links = existing_record.get("links", {})
            for name, link in links.items():
                self.add_option(label=name, value=link)
        else:
            self.add_option(label="No payment links available", value="https://shellobot.xyz")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_value = interaction.data['values'][0]
        data = await Base_Guild.fetch_active_design(self.order_id)
        order_channel = interaction.guild.get_channel(data['channel'])
        price = data["price"]
        product = data["product"]
        designer = interaction.guild.get_member(data["designer_id"])
        customer = interaction.guild.get_member(data["customer_id"])
        embed = discord.Embed(title=f"Order Finished", color=discord.Color.light_embed(), description=f"The following order has been marked as finished.\n\n**Order {self.order_id}**\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Product:** {product}\n<:Shello_Right:1164269631062691880> **Price:** {price}", timestamp=discord.utils.utcnow())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        message = await order_channel.send(embed=embed, content=f"<:Approved:1163094275572121661> **{customer.mention},** please pay for your design.")
        view = discord.ui.View(timeout=None)
        item = discord.ui.Button(style=discord.ButtonStyle.gray, label="Pay Here", url=selected_value)
        view.add_item(OrderPaidButton(message=message, order_id=self.order_id, author=self.author))
        view.add_item(item)
        await message.edit(view=view)
    
class DesignContributionOptions(discord.ui.Select):
    def __init__(self, author, order_id):
        self.author = author
        self.order_id = order_id

        options = [
            discord.SelectOption(label='Update Order', description='Alert the customer of any progress you may have made.', emoji='<:order_updated:1177327822721794058>', value="update"),
            discord.SelectOption(label='Cancel Order', description='Alert the customer that you are cancelling the order.', emoji='<:order_cancel:1177328205410091138>', value="cancel"),
            discord.SelectOption(label='Finish Order', description='Alert the customer you are ready to accept payment.', emoji='<:order_finished:1177327826656034837>', value="finish"),
        ]

        super().__init__(placeholder='Please select an option.', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.author.id != interaction.user.id:
            return await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** this is not your view.", ephemeral=True)
        
        data = await Base_Guild.fetch_active_design(self.order_id)
        order_channel = interaction.guild.get_channel(data['channel'])
        designer = interaction.guild.get_member(data["designer_id"])
        if not order_channel:
            return await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** I can't find the order channel.", ephemeral=True)
        if interaction.user.id != designer.id:
            return await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** only the designer can use this view.", ephemeral=True)
        
        if self.values[0] == "update":
            await interaction.response.send_modal(ContributeModal(question_name=f"Message", question_placeholder=f"Message", status="update", title=f"Update Order", order_id=self.order_id))
            
        elif self.values[0] == "cancel":
            await interaction.response.send_modal(ContributeModal(question_name=f"Reason", question_placeholder=f"Reason", status="cancel", title=f"Cancel Order", order_id=self.order_id))
            
        elif self.values[0] == "finish":
            view = discord.ui.View()
            design_finished_options = await DesignFinishedOptions.create(author=self.author, order_id=self.order_id, guild_id=interaction.guild.id)
            view.add_item(design_finished_options)
            await interaction.response.send_message(view=view, ephemeral=True, content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** please choose a payment link!")
            
            
            
            

        
        



    
class DesignCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_uri = None
        self.config = None  
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.design_records = self.design_Db[self.config["collections"]["design"]["log_collection"]]

        





    @commands.hybrid_group(name="order", description=f"Design based commands")
    async def design(self, ctx):
        pass
    
    
    @design.command(name="start", description="Start the process of creating a design")
    @commands.guild_only()
    async def startdesign(self, ctx: commands.Context, customer: discord.Member, price: int, *, product: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** you need to set up the design module. ")
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        designer_channel = self.client.get_channel(designer_log_channel_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if designer_channel is None or designer_role is None or designer_role not in ctx.author.roles:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** you can't use this command.")

        order_id = f"{random.randint(1000, 9999)}"
        currency = await Base_Guild.fetch_guild_currency(guild=ctx.guild.id)
        await Base_Guild.store_active_design(order_id=order_id, guild=ctx.guild.id, channel=ctx.channel.id, customer=customer.id, price=price, designer=ctx.author.id, product=product)

        embed = discord.Embed(title="Order Started", description=f"Greetings {customer.mention}! The designer {ctx.author.mention} has started your **{product}**, you will receive updates on your products within this channel and your DM's.", color=discord.Color.light_embed())
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        embed.set_footer(text=os.getenv("SERVER_NAME"))

        info_embed = discord.Embed(color=discord.Color.dark_embed(), title="New Design", description=f"**Order {order_id}**\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Designer:** {ctx.author.mention}\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Price:** {price} {currency}\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Product:** {product}")
        info_embed.set_footer(text=f"Order ID: {order_id}")

        await ctx.send(embed=embed) 
        try:
            await ctx.channel.send(embed=info_embed)
        except discord.Forbidden:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** I cannot send messages to the current channel!")
        try:
            await designer_channel.send(embed=info_embed)
        except discord.Forbidden:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** I can't send messages in the designs channel.")
        try:
            await customer.send(embed=info_embed, content=f"<:Approved:1163094275572121661> **{customer.display_name},** your design has now been started!")
                
        except discord.Forbidden:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** I was unable to DM the customer")
        
    @design.command(name=f"manage", description=f"Give the customer an update on an active order")
    @commands.guild_only()
    async def contribute(self, ctx: commands.Context, order_id: int):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** you need to set up the design module. ")

        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = ctx.guild.get_role(designer_role_id)

        if designer_log_channel_id is None or designer_role_id is None or  staff_Role_id is None:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** The design module is not properly set up.")
        

        if staff_role not in ctx.author.roles and designer_role not in ctx.author.roles:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** You can't use this.")
        
        active_design = await Base_Guild.fetch_active_design(order_id=order_id)

        if not active_design:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** there is no active order for this ID.")
        designer = ctx.guild.get_member(active_design["designer_id"])
        customer = ctx.guild.get_member(active_design["customer_id"])
        price = active_design["price"]
        product = active_design["product"]
        currency = await Base_Guild.fetch_guild_currency(guild=ctx.guild.id)
        
        info_embed = discord.Embed(color=discord.Color.dark_embed(), title="Order Contribution", description=f"<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Price:** {price} {currency}\n<:Shello_Right:1164269631062691880> **Product:** {product}")
        view = discord.ui.View()
        view.add_item(DesignContributionOptions(order_id=order_id, author=ctx.author))
        await ctx.send(embed=info_embed, view=view)

    @design.command(name=f"find", description=f"Find a specific order")
    @commands.guild_only()
    async def finddesign(self, ctx: commands.Context, order_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        order = await Base_Guild.fetch_design(order_id=order_id)        
        if not order:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.name},** there is no order for this ID.")
        designer = ctx.guild.get_member(order["designer_id"])
        customer = ctx.guild.get_member(order["customer_id"])
        price = order["price"]
        product = order["product"]
        
        if ctx.author.id != designer.id:
            if ctx.author.id != customer.id:
                return await message.edit(content=F"<:Denied:1163095002969276456> **{ctx.author.display_name},** only the designer or customer can use this.")
        
        embed = discord.Embed(color=discord.Color.light_embed(), title=f"Design {order_id}", description=f"<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Price:** {price}\n<:Shello_Right:1164269631062691880> **Product:** {product}")
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        embed.set_footer(text=f"Design {order_id}")
        await message.edit(embed=embed, content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** here is the requested design.")
        
        
    @design.command(name=f"log", description=f"Log a design without having to start the design")
    async def logdesign(self, ctx: commands.Context, customer: discord.Member, price: int, *, product: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.name},** you need to set up the design module. ")
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        designer_channel = self.client.get_channel(designer_log_channel_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if designer_channel is None or designer_role is None or designer_role not in ctx.author.roles:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.name},** you can't use this command.")

        order_id = f"{random.randint(1000, 9999)}"
        currency = await Base_Guild.fetch_guild_currency(guild=ctx.guild.id)
        await Base_Guild.update_design_logs(order_id=order_id, guild=ctx.guild.id, customer_id=customer.id, price=price, designer_id=ctx.author.id, product=product)

        info_embed = discord.Embed(color=discord.Color.dark_embed(), title="Logged Design", description=f"**Order {order_id}**\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Designer:** {ctx.author.mention}\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Price:** {price} {currency}\n<:Space:1182833159579115530><:Shello_Right:1164269631062691880> **Product:** {product}")
        info_embed.set_footer(text=f"Order ID: {order_id}")

        try:
            await designer_channel.send(embed=info_embed)
        except discord.Forbidden:
            return await ctx.send(content=f"{denied_emoji} **{ctx.author.display_name},** I can't send messages in the designs channel.")
        try:
            await customer.send(embed=info_embed, content=f"<:Approved:1163094275572121661> **{customer.display_name},** your design has now been logged!")
                
        except discord.Forbidden:
            return await ctx.send(f"{denied_emoji} **{ctx.author.name},** I was unable to DM the customer")
        
        
 
async def setup(client: commands.Bot) -> None:
    await client.add_cog(DesignCog(client))