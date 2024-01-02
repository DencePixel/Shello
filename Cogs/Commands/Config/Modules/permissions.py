from discord.ext import commands
from discord import Color
import discord
from Util.Yaml import Load_yaml
from Cogs.emojis import approved_emoji
from motor.motor_asyncio import AsyncIOMotorClient

class StaffTeamRole(discord.ui.RoleSelect):
    def __init__(self, ctx, staff_role):
        self.staff_role_id = staff_role
        self.ctx = ctx

        super().__init__(placeholder="Select a staff role", max_values=1, min_values=1, row=1)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        management_role_id = int(self.values[0].id)
        await interaction.response.defer()
        find = await self.design_config.find_one({"guild_id": interaction.guild.id})
        
        if not find:
            data = {"guild_id": interaction.guild.id,
                    "staff_role_id": management_role_id}
            return await self.design_config.insert_one(data)
            
        else:
            data = {"guild_id": interaction.guild.id,
                    "staff_role_id": management_role_id}
            return await self.design_config.update_many(find, data)

            



class ManagementRole(discord.ui.RoleSelect):
    def __init__(self):
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]

        super().__init__(placeholder="Select a management role", max_values=1, min_values=1, row=2)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        management_role_id = int(self.values[0].id)
        await interaction.response.defer()
        find = await self.design_config.find_one({"guild_id": interaction.guild.id})
        
        if not find:
            data = {"guild_id": interaction.guild.id,
                    "management_role_id": management_role_id}
            return await self.design_config.insert_one(data)
            
        else:
            data = {"guild_id": interaction.guild.id,
                    "management_role_id": management_role_id}
            return await self.design_config.update_many(find, data)

            



class PermissionsView(discord.ui.View):
    def __init__(self, ctx, message):
        super().__init__(timeout=None)
        self.config = None
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.message = message
        self.ctx = ctx
        self.staff_role_view = StaffTeamRole(ctx=self.ctx, staff_role=self.staff_role)
        self.management_role_view = ManagementRole(ctx=self.ctx, management_role=self.management_role)
        self.add_item(item=self.staff_role_view)
        self.add_item(item=self.management_role_view)
                
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton

            
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))