from discord.ext import commands
from discord import Color
import discord
from Util.Yaml import Load_yaml
from pymongo import MongoClient

class DesignerRole(discord.ui.RoleSelect):
    def __init__(self, ctx, designer_role):
        self.designer_role_id = designer_role
        self.ctx = ctx

        super().__init__(placeholder="Select a designer role", max_values=1, min_values=1, row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        self.designer_role_id = int(self.values[0].id)
        print(self.designer_role_id)
        await interaction.response.defer()

class DesignLogChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, design_channel):
        self.designer_log_channel = design_channel
        self.ctx = ctx

        super().__init__(placeholder="Select a design log channel", max_values=1, min_values=1, row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)

        self.designer_log_channel = int(self.values[0].id)
        await interaction.response.defer()

from discord.ext import commands
from discord import Color
import discord
from Util.Yaml import Load_yaml
from pymongo import MongoClient

class DesignerRole(discord.ui.RoleSelect):
    def __init__(self, ctx, designer_role):
        self.designer_role_id = designer_role
        self.ctx = ctx

        super().__init__(placeholder="Select a designer role", max_values=1, min_values=1, row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        self.designer_role_id = int(self.values[0].id)
        print(self.designer_role_id)
        await interaction.response.defer()

class DesignLogChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, design_channel):
        self.designer_log_channel = design_channel
        self.ctx = ctx

        super().__init__(placeholder="Select a design log channel", max_values=1, min_values=1, row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)

        self.designer_log_channel = int(self.values[0].id)
        await interaction.response.defer()

class DesignView(discord.ui.View):
    def __init__(self, ctx, message):
        super().__init__(timeout=None)
        self.config = None
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.message = message
        self.ctx = ctx
        self.designer_role_id = None
        self.designer_log_channel = None
        self.designer_role_view = DesignerRole(ctx=self.ctx, designer_role=self.designer_role_id)
        self.design_log_channel_view = DesignLogChannel(ctx=ctx, design_channel=self.designer_log_channel)
        self.add_item(item=self.designer_role_view)
        self.add_item(item=self.design_log_channel_view)

        

    @discord.ui.button(label="Save Data", row=3)
    async def button_func(self, interaction: discord.Interaction, button: discord.Button):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        designer_role = self.designer_role_view.designer_role_id

        if designer_role:
            designer_role_text = f"<@&{designer_role}>"
        else:
            designer_role_text = "No designer role selected"
            designer_role = 0

        design_log_channel = self.design_log_channel_view.designer_log_channel

        if design_log_channel:
            log_channel_text = f"<#{design_log_channel}>"
        else:
            log_channel_text = "No Design Log Channel selected"
            design_log_channel = 0

        data = {
            "guild_id": interaction.guild.id,
            "designer_role_id": designer_role,
            "designer_log_channel_id": design_log_channel
        }

        filter = {"guild_id": interaction.guild.id}
        self.design_config.update_one(filter, {"$set": data}, upsert=True)

        confirmation_embed = discord.Embed(
            description=f"Data saved successfully!\n\n``>`` Designer Role: {designer_role_text}\n``>`` Design Log Channel: {log_channel_text}",
            color=discord.Color.green())
        
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        for child in self.children:
            self.remove_item(child)
            
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))
        return await self.message.edit(embed=confirmation_embed, view=self, content=None)

