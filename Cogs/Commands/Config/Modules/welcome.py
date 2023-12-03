import discord
import pymongo
from pymongo import MongoClient
from Util.Yaml import Load_yaml

class WelcomeMessageCreation(discord.ui.Modal):
    
    

    def __init__(self, title='Create a welcome message.'):
        
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]  
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["welcome"]["database"]]
        self.welcome_config = self.db[self.config["collections"]["welcome"]["collection"]]
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

        member = interaction.user
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

class WelcomeLogChannel(discord.ui.ChannelSelect):
    def __init__(self, ctx, message):
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]  
        self.ctx = ctx
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["welcome"]["database"]]
        self.welcome_config = self.db[self.config["collections"]["welcome"]["collection"]]

        super().__init__(placeholder="Select a welcome channel", max_values=1, min_values=1, row=1)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
        
        
        await interaction.response.defer()
        
        
        guild_id = interaction.guild.id
        
        existing_record = self.welcome_config.find_one({"guild_id": guild_id})
        
        welcome_channel = int(self.values[0].id)

        if existing_record:
            
            self.welcome_config.update_one(
                {"guild_id": guild_id},
                {"$set": {"welcome_channel": welcome_channel}}
            )
        else:
            new_record = {
                "guild_id": guild_id,
                "welcome_channel": welcome_channel
            }
            self.welcome_config.insert_one(new_record)        


class WelcomeModuleSelection(discord.ui.Select):
    def __init__(self, message, ctx):
        self.message = message
        self.ctx = ctx
        options=[
            discord.SelectOption(label="Welcome Channel",description="What channel should welcome messages get sent to", value="Channel"),
            discord.SelectOption(label=f"Welcome Message", description=f"What is the welcome message", value=f"Message")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options, row=1)
    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "Message":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await interaction.response.send_modal(WelcomeMessageCreation())            

        if self.values[0] == "Channel":
            if interaction.user.id != self.ctx.author.id:
                return
            
            await interaction.response.defer()
            
            replacements = [
            '``!member.mention!``\n',
            '``!member.name!``\n',
            '``!member.id!``\n',
            '``!member.discriminator!``\n',
            '``!member.avatar_url!``\n',
            '``!member.desktop_status!``\n',  
            '``!member.mobile_status!``\n',

            '``!guild.name!``\n',
            '``!guild.id!``\n',
            '``!guild.member_count!``\n']
            
            view = discord.ui.View(timeout=None)
            view.add_item(WelcomeLogChannel(self.ctx, message=self.message))
            from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
            view.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
            embed = discord.Embed(title="Welcome Message Variables", description=f"".join(replacements))
            await self.message.edit(view=view, content=f"<:Approved:1163094275572121661> **{self.ctx.author.display_name},** you are now setting up the welcome channel.", embed=embed)

            

        
            

class WelcomeModuleSelectionView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, message):
        self.ctx= ctx
        self.message = message
        super().__init__(timeout=timeout)
        self.add_item(WelcomeModuleSelection(ctx=self.ctx, message=self.message))
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.add_item(GlobalFinishedButton(ctx=self.ctx, message=self.message))
        
        
        

        
