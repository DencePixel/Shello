import discord
import pymongo
from pymongo import MongoClient
from Util.Yaml import Load_yaml




class InfractionsChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx):
        self.ctx = ctx
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = MongoClient(self.mongo_uri)
        self.infractions_db = self.cluster[self.config["collections"]["Infractions"]["database"]]
        self.infractions_config = self.infractions_db[self.config["collections"]["Infractions"]["config"]]

        super().__init__(placeholder="Select a Infractions channel", max_values=1, min_values=1, row=2)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
        
        
        await interaction.response.defer()
        
        
        guild_id = interaction.guild.id
        
        existing_record = self.leaves_config.find_one({"guild_id": guild_id})
        
        infraction_channel = int(self.values[0].id)


        if existing_record:
            
            self.infractions_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"infraction_channel": infraction_channel}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "infraction_channel": infraction_channel
            }
            self.infractions_config.insert_one(new_record)        
        