import discord
from motor.motor_asyncio import AsyncIOMotorClient
from Util.Yaml import Load_yaml




class LeavesChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx):
        self.ctx = ctx
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]

        super().__init__(placeholder="Select a LOA channel", max_values=1, min_values=1, row=2)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
        
        
        await interaction.response.defer()
        
        
        guild_id = interaction.guild.id
        
        existing_record = await self.leaves_config.find_one({"guild_id": guild_id})
        
        leave_channel = int(self.values[0].id)


        if existing_record:
            
            await self.leaves_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"loa_channel": leave_channel}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "loa_channel": leave_channel
            }
            await self.leaves_config.insert_one(new_record)        
  

class LeavesRole(discord.ui.RoleSelect):
    def __init__(self, ctx, message):
        self.ctx = ctx
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]

        super().__init__(placeholder="Select a active leaves role", max_values=1, min_values=1, row=1)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
        
        
        await interaction.response.defer()
        
        
        guild_id = interaction.guild.id
        
        existing_record = await self.leaves_config.find_one({"guild_id": guild_id})
        
        leaves_role = int(self.values[0].id)

        if existing_record:
            
            await self.leaves_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"leave_role": leaves_role}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "leave_role": leaves_role
            }
            await self.leaves_config.insert_one(new_record)   
            

        
            

class LeavesModuleSelection(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(LeavesRole(ctx=self.ctx, message=self.message))
        self.add_item(LeavesChannel(ctx=self.ctx))
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
        
    
        

        