from typing import Any
from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
from discord.interactions import Interaction
from pymongo import MongoClient
from DataModels.guild import BaseGuild
import os
from DataModels.user import BaseUser
import datetime
from dotenv import load_dotenv
load_dotenv()
import random
from Util.Yaml import Load_yaml

Base_User = BaseUser()
Base_Guild = BaseGuild()

class RefundModal(discord.ui.Modal):
    def __init__(self, question_name, title, question_placeholder, status, order_id):
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
             
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.design_records = self.design_Db[self.config["collections"]["design"]["log_collection"]]
        
        self.refund_records = self.design_Db[self.config["collections"]["design"]["refund_collection"]]
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
        data = await Base_Guild.fetch_design(self.order_id)
        if not data:
            return await interaction.response.send_message(
                f"<:shell_denied:1160456828451295232> **{interaction.user.display_name},** I can't find that Order!",
                ephemeral=True)
        if self.status == "update":
            refund_request = self.refund_records.find_one(
                {"guild_id": interaction.guild.id, "order_id": self.order_id})
            if not refund_request:
                return await interaction.response.send_message(
                    content=f"<:Denied:1163095002969276456> **{interaction.user.display_name},** I can't find that refund request.",
                    ephemeral=True)
                
                
                
            await interaction.response.send_message(F"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully updated the refund request.", ephemeral=True)
            self.refund_records.update_one(
                {"guild_id": interaction.guild.id, "order_id": self.order_id},
                {"$set": {"status": self.Message.value}}
            )

            message_Embed = discord.Embed(
                title=f"Refund Status", description=f"**New refund status:** ``{self.Message.value}``",
                color=discord.Color.dark_embed())
            message_Embed.set_author(icon_url=interaction.user.display_avatar.url,
                                     name=interaction.user.display_name)
            message_Embed.set_footer(
                text=f"Refund status updated by {interaction.user.display_name}")
            designer = interaction.guild.get_member(data["designer_id"])
            customer = interaction.guild.get_member(data["customer_id"])
            await customer.send(embed=message_Embed,
                                content=f"<:Approved:1163094275572121661> **{customer.display_name},** the status for your refund request has changed!")

        elif self.status == "decline":
            refund_request = self.refund_records.find_one(
                {"guild_id": interaction.guild.id, "order_id": self.order_id})
            if not refund_request:
                return await interaction.response.send_message(
                    content=f"<:Denied:1163095002969276456> **{interaction.user.display_name},** I can't find that refund request.",
                    ephemeral=True)

            self.refund_records.delete_one({"guild_id": interaction.guild.id, "order_id": self.order_id})
            
            await interaction.response.send_message(F"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully declined the refund request.", ephemeral=True)
            message_Embed = discord.Embed(
                title=f"Refund Status", description="**Refund request declined.**",
                color=discord.Color.dark_embed())
            message_Embed.set_author(icon_url=interaction.user.display_avatar.url,
                                     name=interaction.user.display_name)
            message_Embed.set_footer(
                text=f"Refund request canceled by {interaction.user.display_name}")
            customer = interaction.guild.get_member(data["customer_id"])
            await customer.send(embed=message_Embed,
                                content=f"<:Approved:1163094275572121661> **{customer.display_name},** your refund request has been declined.")

        elif self.status == "accept":
            refund_request = self.refund_records.find_one(
                {"guild_id": interaction.guild.id, "order_id": self.order_id})
            if not refund_request:
                return await interaction.response.send_message(
                    content=f"<:Denied:1163095002969276456> **{interaction.user.display_name},** I can't find that refund request.",
                    ephemeral=True)
                
            
            
            await interaction.response.send_message(F"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully accepted the refund request.", ephemeral=True)
                
                
            self.refund_records.delete_one({"guild_id": interaction.guild.id, "order_id": self.order_id})

            message_Embed = discord.Embed(
                title=f"Refund Status", description="**Refund request accepted.**\n",
                color=discord.Color.dark_embed())
            message_Embed.set_author(icon_url=interaction.user.display_avatar.url,
                                     name=interaction.user.display_name)
            message_Embed.set_footer(
                text=f"Refund request accepted by {interaction.user.display_name}")
            customer = interaction.guild.get_member(data["customer_id"])
            await customer.send(embed=message_Embed,
                                content=f"<:Approved:1163094275572121661> **{customer.display_name},** your refund request has been accepted.")
            existing_record = await Base_Guild.fetch_design_config(interaction.guild.id)
            designer_log_channel_id = existing_record.get("designer_log_channel_id")
            design_channel = interaction.guild.get_channel(designer_log_channel_id)
            await design_channel.send(embed=message_Embed)

class RefundAdminOptions(discord.ui.Select):
    def __init__(self, author, order_id):
        self.author = author
        self.order_id = order_id

        options = [
            discord.SelectOption(label='Update Status', description='Update the refund status.', value="update"),
            discord.SelectOption(label='Decline Refund', description='Decline the refund request.', value="decline"),
            discord.SelectOption(label='Accept Refund', description='Accept the refund request.', value="accept"),
        ]

        super().__init__(placeholder='Please select an option.', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.author.id != interaction.user.id:
            return await interaction.response.send_message(f"<:shell_denied:1160456828451295232> **{interaction.user.display_name},** this is not your view.", ephemeral=True)
        
        if self.values[0] == "update":
            await interaction.response.send_modal(RefundModal(status="update", question_name=f"Refund Status", question_placeholder=f"The new refund status", order_id=self.order_id, title=f"Update order status"))
            
        elif self.values[0] == "decline":
            await interaction.response.send_modal(RefundModal(status="decline", question_name=f"Reason", question_placeholder=f"Why would you like to decline the refund status", order_id=self.order_id, title=f"Cancel Request"))
            
        elif self.values[0] == "accept":
            await interaction.response.send_modal(RefundModal(status="accept", question_name=f"Reason", question_placeholder=f"Why would you like to accept the refund status", order_id=self.order_id, title=f"Accept Request"))

    
class RefundCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
             
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.design_records = self.design_Db[self.config["collections"]["design"]["log_collection"]]
        
        self.refund_records = self.design_Db[self.config["collections"]["design"]["refund_collection"]]

    @commands.hybrid_group(name="refund", description=f"Refund based commands")
    async def refundgroup(self, ctx):
        pass
        
        
    @refundgroup.command(name="request", description="Request a refund for a design you received")
    async def refund(self, ctx: commands.Context, order_id: int, *, reason: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        order = await Base_Guild.fetch_design(order_id)
        existing_record = await Base_Guild.fetch_design_config(ctx.guild.id)

        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** The design module is not properly set up.")

        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = ctx.guild.get_role(designer_role_id)

        if designer_log_channel_id is None or designer_role_id is None or staff_Role_id is None:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** The design module is not properly set up.")
        if not order:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** I can't find that order.")

        designer = ctx.guild.get_member(order["designer_id"])
        customer = ctx.guild.get_member(order["customer_id"])
        if customer.id != ctx.author.id:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** You can only refund orders you made.")

        price = order["price"]
        product = order["product"]

        existing_refund = self.refund_records.find_one(
            {"guild_id": ctx.guild.id, "requester_id": ctx.author.id}
        )
        if existing_refund:
            return await message.edit(
                content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** You already have an active refund request. "
            )

        refund_data = {
            "guild_id": ctx.guild.id,
            "order_id": order_id,
            "requester_id": ctx.author.id,
            "status": "Being Processed",
            "timestamp": datetime.datetime.utcnow(),
        }
        self.refund_records.insert_one(refund_data)

        await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** you can review your refund request with ``/refund status``")

        embed = discord.Embed(
            title=f"Refund Request",
            description=f"**Refund Information**\n<:Shello_Right:1164269631062691880> **Order ID:** ``{order_id}``\n<:Shello_Right:1164269631062691880> **Requested By:** ``{ctx.author.mention}``\n<:Shello_Right:1164269631062691880> **Refund Reason:** ``{reason}``\n\n**Design Information:**\n<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Price:** ``{price}``\n<:Shello_Right:1164269631062691880> **Product:** ``{product}``",
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.color = discord.Color.light_embed()
        embed.set_footer(text=f"You can manage this request with /refund admin")
        await designer.send(embed=embed)
        designer_log_channel = ctx.guild.get_channel(designer_log_channel_id)
        await designer_log_channel.send(
            embed=embed, content=f"<:Alert:1163094295314706552> **{designer.mention},** there is a refund request for your design."
        )
        
        
    @refundgroup.command(name="status", description="Check the status of an active refund request")
    async def refund_status(self, ctx: commands.Context, order_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** fetching information for that refund request.")
        refund_request = self.refund_records.find_one(
            {"guild_id": ctx.guild.id, "order_id": order_id}
        )

        existing_record = await Base_Guild.fetch_design_config(ctx.guild.id)

        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** The design module is not properly set up.")

        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_Role_id)

        if refund_request:
            status = refund_request["status"]
            requester_id = refund_request["requester_id"]
            requester = ctx.guild.get_member(requester_id)
            formatted_timestamp = discord.utils.format_dt(refund_request["timestamp"], style="R")

            embed = discord.Embed(
                title=f"Refund Request Status",
                description=f"**Refund Information**\n<:Shello_Right:1164269631062691880> **Order ID:** ``{order_id}``\n<:Shello_Right:1164269631062691880> **Status:** ``{status}``\n<:Shello_Right:1164269631062691880> **Timestamp:** {formatted_timestamp}\n\n**User Information:**\n<:Shello_Right:1164269631062691880> **Requester:** {requester.mention} (``{requester_id}``)",
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.color = discord.Color.light_embed()
            await message.edit(embed=embed, content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** here is the status of the refund request.")
        else:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** I can't find that refund request.")

    @refundgroup.command(name=f"admin", description=f"Manage a refund request")
    async def refundadmin(self, ctx: commands.Context, order_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** fetching the refund request.")
        refund_request = self.refund_records.find_one(
            {"guild_id": ctx.guild.id, "order_id": order_id}
        )

        existing_record = await Base_Guild.fetch_design_config(ctx.guild.id)

        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** The design module is not properly set up.")

        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = ctx.guild.get_role(designer_role_id)

        if refund_request:
            status = refund_request["status"]
            requester_id = refund_request["requester_id"]

            if staff_role not in ctx.author.roles and designer_role not in ctx.author.roles and requester_id != ctx.author.id:
                return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** You can't use this.")

            view = discord.ui.View()
            view.add_item(RefundAdminOptions(author=ctx.author, order_id=order_id))
            await message.edit(view=view, content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** here is the requested refund request.")
        else:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.display_name},** I can't find that refund request.")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(RefundCog(client))