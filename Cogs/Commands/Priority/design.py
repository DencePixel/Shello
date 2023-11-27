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
from dotenv import load_dotenv
load_dotenv()
import random
from Util.Yaml import Load_yaml


Base_User = BaseUser()
Base_Guild = BaseGuild()

class ContributeModal(discord.ui.Modal):
    def __init__(self, question_name, title, question_placeholder,status, order_id):
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
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
            return await interaction.response.send_message(f"<:shell_denied:1160456828451295232> **{interaction.user.display_name},** I can't find that Order!", ephemeral=True)
        if self.status == "update":

                
            order_channel = interaction.guild.get_channel(data['channel'])
            designer = interaction.guild.get_member(data["designer_id"])
            customer = interaction.guild.get_member(data["customer_id"])
            message_Embed = discord.Embed(title=f"Design Contribution", description=f"{self.Message.value}", color=discord.Color.dark_embed())
            message_Embed.set_author(icon_url=interaction.user.display_avatar.url, name=interaction.user.display_name)
            message_Embed.set_footer(text=f"Design contributed to by {interaction.user.display_name}")
            await order_channel.send(embed=message_Embed, content=f"<:Approved:1163094275572121661> **{customer.mention}**, there is a new contribution to your design!")      
            await customer.send(embed=message_Embed, content=f"<:Approved:1163094275572121661> **{customer.display_name}**, there is a new contribution to your design!") 
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
            await order_channel.send(embed=message_Embed, content=f"<:Denied:1163095002969276456> **{customer.mention}**, you're design has been cancelled.")      
            await customer.send(embed=message_Embed, content=f"<:Denied:1163095002969276456> **{customer.display_name}**, you're design has been cancelled.") 
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
        self.cluster = MongoClient(self.mongo_uri)
        self.order_id = order_id
        self.guild_id = guild_id
        super().__init__(placeholder='Please select a payment link.', min_values=1, max_values=1, **kwargs)

        self.fetch_payment_links()

    def fetch_payment_links(self):
        payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        payment_config = payment_db[self.config["collections"]["payment"]["collection"]]
        existing_record = payment_config.find_one({"guild_id": self.guild_id})

        if existing_record:
            links = existing_record.get("links", {})
            for name, link in links.items():
                self.add_option(label=name, value=link)
        else:
            self.add_option(label="No payment links available", value="no_links")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_value = interaction.data['values'][0]
        data = await Base_Guild.fetch_active_design(self.order_id)
        order_channel = interaction.guild.get_channel(data['channel'])
        price = data["price"]
        product = data["product"]
        designer = interaction.guild.get_member(data["designer_id"])
        customer = interaction.guild.get_member(data["customer_id"])
        embed = discord.Embed(description=f"Please pay **{data['price']}** Robux by clicking this [link]({selected_value}) and purchasing the item, once finished please let your designer know so that they can close this ticket!", color=discord.Color.light_embed())
        await order_channel.send(embed=embed, content=f"<:Approved:1163094275572121661> **{customer.mention},** you're design has been finished.")      
        await customer.send(embed=embed, content=f"<:Approved:1163094275572121661> **{customer.display_name},** you're design has been finished.")      
        existing_record = await Base_Guild.fetch_design_config(interaction.guild.id)
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        info_embed = discord.Embed(color=discord.Color.dark_embed(), title="Design Finished", description=f"<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Price:** {price}\n<:Shello_Right:1164269631062691880> **Product:** {product}")
        embed.set_author(icon_url=interaction.user.display_avatar.url, name=interaction.user.display_avatar)
        designer_channel = interaction.guild.get_channel(designer_log_channel_id)
        await designer_channel.send(embed=info_embed)
        cancel = await Base_Guild.cancel_active_design(order_id=self.order_id)
        if cancel is True:
            log = await Base_Guild.update_design_logs(guild=interaction.guild.id,order_id=self.order_id, designer_id=designer.id, customer_id=customer.id, price=price, product=product)
            await interaction.followup.send(f"<:Approved:1163094275572121661> **{interaction.user.display_name},** succesfully finished the design.", ephemeral=True)      
            

        
        
    
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
            return await interaction.response.send_message(f"<:shell_denied:1160456828451295232> **{interaction.user.display_name},** this is not your view.", ephemeral=True)
        
        data = await Base_Guild.fetch_active_design(self.order_id)
        order_channel = interaction.guild.get_channel(data['channel'])
        designer = interaction.guild.get_member(data["designer_id"])
        if not order_channel:
            return await interaction.response.send_message(f"<:shell_denied:1160456828451295232> **{interaction.user.display_name},** I can't find the order channel.", ephemeral=True)
        if interaction.user.id != designer.id:
            return await interaction.response.send_message(f"<:shell_denied:1160456828451295232> **{interaction.user.display_name},** only the designer can use this view.", ephemeral=True)
        
        if self.values[0] == "update":
            await interaction.response.send_modal(ContributeModal(question_name=f"Message", question_placeholder=f"Message", status="update", title=f"Update Order", order_id=self.order_id))
            
        elif self.values[0] == "cancel":
            await interaction.response.send_modal(ContributeModal(question_name=f"Reason", question_placeholder=f"Reason", status="cancel", title=f"Cancel Order", order_id=self.order_id))
            
        elif self.values[0] == "finish":
            view = discord.ui.View()
            view.add_item(DesignFinishedOptions(author=self.author, guild_id=interaction.guild.id, order_id=self.order_id))
            await interaction.response.send_message(view=view, ephemeral=True, content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** please choose a payment link!")
            
            
            
            
            

        
        



    
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
    
    
    @design.command(name="start", description="Start the process of creating a design")
    async def start(self, ctx: commands.Context, customer: discord.Member, price: int, *, product: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. ")
        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        designer_channel = self.client.get_channel(designer_log_channel_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if designer_channel is None or designer_role is None or designer_role not in ctx.author.roles:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you can't use this command.")

        try:
            order_id = f"{random.randint(1000, 9999)}"
            await Base_Guild.store_active_design(order_id=order_id, guild=ctx.guild.id, channel=ctx.channel.id, customer=customer.id, price=price, designer=ctx.author.id, product=product)

            embed = discord.Embed(title="Design Started", description=f"Greetings {customer.mention}! The designer {ctx.author.mention} has started your {product}, you will receive updates on your products within this channel and your DM's.", color=discord.Color.light_embed())
            embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
            embed.set_footer(text="Shello Systems")

            info_embed = discord.Embed(color=discord.Color.dark_embed(), title="New Design", description=f"<:Shello_Right:1164269631062691880> **Designer:** {ctx.author.mention}\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Price:** {price}\n<:Shello_Right:1164269631062691880> **Product:** {product}")
            info_embed.set_footer(text=f"Order ID: {order_id}")

            await ctx.send(embed=embed) 
            await ctx.send(embed=info_embed)
            await designer_channel.send(embed=info_embed)
            await customer.send(embed=info_embed, content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** your design has now been started!")
        except Exception as e:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** I was unable to send the messages. Please try again.")
        
    @design.command(name=f"contribute", description=f"Give the customer an update on an active order")
    async def contribute(self, ctx: commands.Context, order_id: int):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        guild_id = ctx.guild.id
        existing_record = await Base_Guild.fetch_design_config(guild_id)

        if not existing_record:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. ")

        designer_log_channel_id = existing_record.get("designer_log_channel_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_Role_id = existing_record.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = ctx.guild.get_role(designer_role_id)

        if designer_log_channel_id is None or designer_role_id is None or  staff_Role_id is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** The design module is not properly set up.")
        
        print(staff_role)
        print(designer_role)
        print(ctx.author.roles)
        if staff_role not in ctx.author.roles and designer_role not in ctx.author.roles:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** You can't use this.")
        
        active_design = await Base_Guild.fetch_active_design(order_id=order_id)
        print("Active Design:", active_design) 

        if not active_design:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** there is no active order for this ID.")
        designer = ctx.guild.get_member(active_design["designer_id"])
        customer = ctx.guild.get_member(active_design["customer_id"])
        price = active_design["price"]
        product = active_design["product"]
        
        info_embed = discord.Embed(color=discord.Color.dark_embed(), title="Design Contribution", description=f"<:Shello_Right:1164269631062691880> **Designer:** {designer.mention}\n<:Shello_Right:1164269631062691880> **Customer:** {customer.mention}\n<:Shello_Right:1164269631062691880> **Price:** {price}\n<:Shello_Right:1164269631062691880> **Product:** {product}")
        view = discord.ui.View()
        view.add_item(DesignContributionOptions(order_id=order_id, author=ctx.author))
        await ctx.send(embed=info_embed, view=view)
               
    @design.command(name=f"feedback", description=f"Provide feedback on a design you recieved")
    @discord.app_commands.choices(
        rating=[
            discord.app_commands.Choice(name="⭐", value="1"), 
            discord.app_commands.Choice(name="⭐⭐", value="2"),
            discord.app_commands.Choice(name="⭐⭐⭐", value="3"),
            discord.app_commands.Choice(name="⭐⭐⭐⭐", value="4"),
            discord.app_commands.Choice(name="⭐⭐⭐⭐⭐", value="5")
        ]
    )
    async def feedback(self, ctx: commands.Context, rating: str, *, product: str):
        embed = discord.Embed(title=f"{product} - Review", description=f"{ctx.author.mention} has rated their {product} a **{rating}** star!", color=discord.Color.gold())
        embed.set_footer(text=f"Shello Systems")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)       
        feedback_channel_id = await Base_Guild.get_feedback_channel(guild_id=ctx.guild.id)

        if feedback_channel_id is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** the feedback module has been incorrectly configured.")
        
        feedback_channel = ctx.guild.get_channel(feedback_channel_id)
        await feedback_channel.send(embed=embed)
        await ctx.send(f"<:Approved:1163094275572121661> **{ctx.author.display_name},** succesfully sent your feedback!")
        
 
async def setup(client: commands.Bot) -> None:
    await client.add_cog(DesignCog(client))