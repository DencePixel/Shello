from discord.ui import Modal
import discord
from pymongo import MongoClient
from Util.Yaml import Load_yaml
from Cogs.emojis import denied_emoji

class AutoResponderChannel(discord.ui.ChannelSelect):
    def __init__(self, response):
        self.config = Load_yaml()
        
        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["autoresponder"]["database"]]
        self.autoresponder_config = self.db[self.config["collections"]["autoresponder"]["collection"]]


        super().__init__(placeholder="Select a alerts channel", max_values=1, min_values=1, row=1)
    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description=f"This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True, content=None)
        
        
        await interaction.response.defer()
           

class AutoresponderDeletionView(discord.ui.View):
    def __init__(self, guild_id, message, user):
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        super().__init__()
        self.guild_id = guild_id
        self.ctx = user
        self.message = message
        self.add_item(AutoresponderDeletion(guild_id=self.guild_id))
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))

class AutoresponderActionSelect(discord.ui.View):
    def __init__(self, message, user):
        super().__init__()
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.message = message
        self.ctx = user
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))

    @discord.ui.button(label="Add Response", style=discord.ButtonStyle.green)
    async def AddAutoresponder(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.ctx.author.id:
            return

        await interaction.response.send_modal(AutoresponderCreation(title="Create an autoresponder"))

    @discord.ui.button(label="Delete Response", style=discord.ButtonStyle.red)
    async def DeleteAutoresponder(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        await interaction.response.defer()

        embed = discord.Embed(title="Autoresponder Configuration", description="Please select an autoresponder below to delete.")

        view = AutoresponderDeletionView(guild_id=interaction.guild.id, message=self.message, user=self.ctx)
        await self.message.edit(view=view, embed=None)


class AutoresponderCreation(Modal):
    def __init__(self, title='Create an autoresponder.'):
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        super().__init__(title=title)

        self.Trigger = discord.ui.TextInput(
            label='Trigger',
            style=discord.TextStyle.short,
            placeholder='The trigger for the autoresponder.',
            required=True,
            max_length=100,
        )
        self.Response = discord.ui.TextInput(
            label="Response",
            style=discord.TextStyle.short,
            placeholder='The autoresponder response.',
            required=True,
            max_length=300
        )

        self.response_channel = discord.ui.TextInput(
            label=f"Response Channel ID",
            style=discord.TextStyle.short,
            placeholder=f"Leave this blank if you want it to respond in the current channel.",
            required=False,
            max_length=100
        )

        self.required_role = discord.ui.TextInput(
            label=f"Required Role ID",
            style=discord.TextStyle.short,
            placeholder=f"Leave this blank if anybody can use this command.",
            required=False,
            max_length=100
        )
        self.add_item(self.Trigger)
        self.add_item(self.Response)
        self.add_item(self.response_channel)
        self.add_item(self.required_role)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        trigger = self.Trigger.value
        response = self.Response.value
        response_channel = int(self.response_channel.value) if self.response_channel.value else 0
        required_role = int(self.required_role.value) if self.required_role.value else 0

        if response_channel != 0 and not isinstance(response_channel, int):
            return await interaction.followup.send(content=f"{denied_emoji} The **Response Channel** question has to be the channel ID.", ephemeral=True)

        if required_role != 0 and not isinstance(required_role, int):
            return await interaction.followup.send(content=f"{denied_emoji} The **Required Role** question has to be a role ID.", ephemeral=True)

        guild_id = interaction.guild_id

        cluster = MongoClient(self.mongo_uri)
        db = cluster[self.config["collections"]["autoresponder"]["database"]]
        autoresponder_config = db[self.config["collections"]["autoresponder"]["collection"]]

        existing_record = autoresponder_config.find_one({"guild_id": guild_id})

        if existing_record:
            responses = existing_record.get("responses", {})
            responses[trigger] = {
                "response": response,
                "channel_id": response_channel,
                "role_id": required_role
            }

            autoresponder_config.update_one({"guild_id": guild_id}, {"$set": {"responses": responses}})
        else:
            autoresponder = {
                "guild_id": guild_id,
                "responses": {
                    trigger: {
                        "response": response,
                        "channel_id": response_channel,
                        "role_id": required_role
                    }
                }
            }
            autoresponder_config.insert_one(autoresponder)

class AutoresponderDeletion(discord.ui.Select):
    def __init__(self, guild_id):
        super().__init__(placeholder='Select an autoresponder to delete', min_values=1, max_values=1, row=1)
        self.guild_id = guild_id

        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]

        self.cluster = MongoClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["autoresponder"]["database"]]
        self.autoresponder_config = self.db[self.config["collections"]["autoresponder"]["collection"]]

        existing_record = self.autoresponder_config.find_one({"guild_id": guild_id})
        responses = existing_record.get("responses", {}) if existing_record else {}

        if not responses:
            self.add_option(label='No autoresponder available', value='no_autoresponder')
        else:
            for i, trigger in enumerate(responses.keys()):
                if i >= 25:
                    break
                self.add_option(label=trigger, value=trigger)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        if selected_value == 'no_autoresponder':
            await interaction.response.send_message("There are no autoresponders available to delete.", ephemeral=True)
            return

        existing_record = self.autoresponder_config.find_one({"guild_id": self.guild_id})
        responses = existing_record.get("responses", {}) if existing_record else {}

        if selected_value in responses:
            del responses[selected_value]

            self.autoresponder_config.update_one({"guild_id": self.guild_id}, {"$set": {"responses": responses}})

            await interaction.response.send_message(f"Autoresponder with trigger '{selected_value}' has been deleted from MongoDB.", ephemeral=True)
        else:
            await interaction.response.send_message("The selected autoresponder does not exist.", ephemeral=True)