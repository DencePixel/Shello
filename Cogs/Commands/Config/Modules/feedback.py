from discord.ext import commands
from discord import Color
import discord
from Util.Yaml import Load_yaml
from motor.motor_asyncio import AsyncIOMotorClient

class FeedbackChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, guild, message):
        self.ctx = ctx
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.design_db = self.cluster[self.config["collections"]["design"]["database"]]
        self.feedback_collection = self.design_db[self.config["collections"]["design"]["feedback_config"]]
        self.guild_id = guild.id
        super().__init__(placeholder="Select a feedback channel", max_values=1, min_values=1, row=1)  

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)

        self.feedback_channel = int(self.values[0].id)
        
        existing_entry = await self.feedback_collection.find_one({"guild_id": self.guild_id})

        if existing_entry:
            await self.feedback_collection.update_one(
                {"guild_id": self.guild_id},
                {"$set": {"feedback_channel": self.feedback_channel}}
            )
        else:
            await self.feedback_collection.insert_one(
                {"guild_id": self.guild_id, "feedback_channel": self.feedback_channel}
            )

        await interaction.response.defer()

class FeedbackView(discord.ui.View):
    def __init__(self, ctx, message, guild):
        super().__init__(timeout=None)
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.add_item(GlobalFinishedButton(ctx=ctx, message=message))
        self.add_item(FeedbackChannel(guild=guild, ctx=ctx, message=message))
