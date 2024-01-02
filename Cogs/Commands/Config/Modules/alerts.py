import discord
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from Util.Yaml import Load_yaml

class AlertsChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx):
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]  
        self.ctx = ctx
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["Alerts"]["database"]]
        self.alerts_config = self.db[self.config["collections"]["Alerts"]["config"]]

        super().__init__(placeholder="Select a alerts channel", max_values=1, min_values=1, row=1)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
        
        
        await interaction.response.defer()
        
        
        guild_id = interaction.guild.id
        
        existing_record = await self.alerts_config.find_one({"guild_id": guild_id})
        
        alert_channel = int(self.values[0].id)


        if existing_record:
            
            await self.alerts_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"alert_channel": alert_channel}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "alert_channel": alert_channel
            }
            await self.alerts_config.insert_one(new_record)        
  


            

        
            

class AlertsModuleSelection(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(AlertsChannel(ctx=self.ctx))
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
        
        
        

        