import discord
import pymongo
from pymongo import MongoClient

class WelcomeMessageCreation(discord.ui.Modal):

    def __init__(self, title='Create a welcome message.'):

        self.cluster = MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        self.db = self.cluster["WelcomeSystem"]
        self.welcome_config = self.db["Welcome Config"]

        super().__init__(title=title)
            
        self.Message = discord.ui.TextInput(
            label='Message',
            style=discord.TextStyle.short,
            placeholder='The welcome message with variables like !member.mention!',
            required=True,
            max_length=500,
        )
        
        self.add_item(self.Message)

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer()
        guild_id = interaction.guild_id
        welcome_message = self.Message.value

        # Replace placeholders with actual values
        member = interaction.user  # Assuming you want to mention the user who interacted
        existing_record = self.welcome_config.find_one({"guild_id": guild_id})

        if existing_record:
            
            self.welcome_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"welcome_message": welcome_message}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "welcome_message": welcome_message
            }
            self.welcome_config.insert_one(new_record)

class DesignLogChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, design_channel):
        self.designer_log_channel = design_channel
        self.ctx= ctx

        super().__init__(placeholder="Select a design log channel", max_values=1, min_values=1, row=2)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
                
        self.designer_log_channel = int(self.values[0].id)
        await interaction.response.defer()