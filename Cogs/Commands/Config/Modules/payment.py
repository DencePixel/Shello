from discord.ui import Modal
from motor.motor_asyncio import AsyncIOMotorClient
import discord
from Util.Yaml import Load_yaml



        

class PaymentLinksDeletionView(discord.ui.View):
    def __init__(self, guild_id, message, user):
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        super().__init__()
        self.guild_id = guild_id
        self.ctx = user
        self.message = message
        self.add_item(PaymentLinkDeletion(guild_id=self.guild_id))
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))


        


class PaymentLinksActionSelect(discord.ui.View):
    def __init__(self, message, user):
        super().__init__()
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        self.message = message
        self.ctx = user
        
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))


    @discord.ui.button(label="Add A Link", style=discord.ButtonStyle.green)
    async def AddALink(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        
        await interaction.response.send_modal(PaymentLinkCreation(title=f"Create a payment link"))

    @discord.ui.button(label="Delete A Link", style=discord.ButtonStyle.red)
    async def DeleteALink(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        
        embed = discord.Embed(title=f"Link Configuration", description=f"Please select a link below to delete.")
        
        view = PaymentLinksDeletionView(guild_id=interaction.guild.id, message=self.message, user=self.ctx)
        await self.message.edit(view=view, embed=None)
        await interaction.response.defer()


class PaymentLinkCreation(Modal):
    def __init__(self, title='Create a payment link.'):
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        super().__init__(title=title)

            
        self.Title = discord.ui.TextInput(
            label='Title',
            style=discord.TextStyle.short,
            placeholder='The title of the payment link.',
            required=True,
            max_length=100,
        )
        self.Link = discord.ui.TextInput(
            label=f"Link",
            style=discord.TextStyle.short,
            placeholder='The link that is used for the payment link.',
            required=True,
            max_length=300
        )
        self.add_item(self.Title)
        self.add_item(self.Link)


    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


        
        guild_id = interaction.guild_id

        cluster = AsyncIOMotorClient(self.mongo_uri)
        db = cluster[self.config["collections"]["payment"]["database"]]
        design_config = db[self.config["collections"]["payment"]["collection"]]

        existing_record = await design_config.find_one({"guild_id": guild_id})

        if existing_record:
            links = existing_record.get("links", {})

            title = self.Title.value
            link = self.Link.value

            links[title] = link

            await design_config.update_one({"guild_id": guild_id}, {"$set": {"links": links}})

        else:
            title = self.Title.value
            link = self.Link.value
            payment_link = {
                "guild_id": guild_id,
                "links": {title: link}
            }
            await design_config.insert_one(payment_link)

            
            
class PaymentLinkDeletion(discord.ui.Select):
    async def __init__(self, guild_id):
        super().__init__(placeholder='Select a payment link to delete', min_values=1, max_values=1, row=1)
        self.guild_id = guild_id

        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
  
        self.cluster = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.db[self.config["collections"]["payment"]["collection"]]

        
        existing_record = await self.payment_config.find_one({"guild_id": guild_id})
        links = existing_record.get("links", {}) if existing_record else {}
        
        if not links:
            self.add_option(label='No link available', value='https://shellobot.xyz')
        else:
            for i, (title, link) in enumerate(links.items()):
                if i >= 25:
                    break
                self.add_option(label=title, value=link)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        if selected_value == 'no_link':
            await interaction.response.send_message("There are no payment links available to delete.", ephemeral=True)
            return



        existing_record = await self.payment_config.find_one({"guild_id": self.guild_id})
        links = existing_record.get("links", {}) if existing_record else {}

        if selected_value in links.values():
            selected_key = next(key for key, value in links.items() if value == selected_value)
            del links[selected_key]

            await self.payment_config.update_one({"guild_id": self.guild_id}, {"$set": {"links": links}})

            await interaction.response.send_message(f"Payment link '{selected_key}' has been deleted from MongoDB.", ephemeral=True)
        else:
            await interaction.response.send_message("The selected payment link does not exist.", ephemeral=True)