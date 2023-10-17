from discord.ui import Modal
from pymongo import MongoClient
import discord



        

class PaymentLinksDeletionView(discord.ui.View):
    def __init__(self, guild_id, message, user):
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton
        super().__init__()
        self.guild_id = guild_id
        self.ctx = user
        self.message = message
        self.add_item(PaymentLinkDeletion(guild_id=self.guild_id))
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))


        
class PaymentLinksCreationView(discord.ui.View):
    def __init__(self, message, user):
        from Cogs.Commands.Config.Modules.view import GlobalFinishedButton

        super().__init__()
        self.message = message
        self.ctx = user
        self.add_item(GlobalFinishedButton(message=self.message, ctx=self.ctx))

    @discord.ui.button(label="Add A Link", style=discord.ButtonStyle.green, row=1)
    async def AddALink(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        
        
        await interaction.response.send_modal(PaymentLinkCreation())

class PaymentLinksActionSelect(discord.ui.View):
    def __init__(self, message, user):
        super().__init__()
        self.message = message
        self.ctx = user

    @discord.ui.button(label="Add A Link", style=discord.ButtonStyle.green)
    async def AddALink(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.ctx.author.id:
            return
        
        embed = discord.Embed(title=f"Link Configuration", description=f"Please click the button below to add a link.")
        view = PaymentLinksCreationView(message=self.message, user=self.ctx)
        await interaction.response.defer()
        await self.message.edit(view=view, embed=embed, content=None)

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

        cluster = MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        db = cluster["PaymentLinkSystem"]
        design_config = db["Payment Config"]

        existing_record = design_config.find_one({"guild_id": guild_id})

        if existing_record:
            links = existing_record.get("links", {})

            title = self.Title.value
            link = self.Link.value

            links[title] = link

            design_config.update_one({"guild_id": guild_id}, {"$set": {"links": links}})

        else:
            title = self.Title.value
            link = self.Link.value
            payment_link = {
                "guild_id": guild_id,
                "links": {title: link}
            }
            design_config.insert_one(payment_link)

            
            
class PaymentLinkDeletion(discord.ui.Select):
    def __init__(self, guild_id):
        super().__init__(placeholder='Select a payment link to delete', min_values=1, max_values=1, row=1)
        self.guild_id = guild_id
        self.cluster = MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        self.db = self.cluster["PaymentLinkSystem"]
        self.design_config = self.db["Payment Config"]
        
        existing_record = self.design_config.find_one({"guild_id": guild_id})
        links = existing_record.get("links", {}) if existing_record else {}
        
        if not links:
            self.add_option(label='No link available', value='no_link')
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

        cluster = MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        db = cluster["PaymentLinkSystem"]
        design_config = db["Payment Config"]

        existing_record = design_config.find_one({"guild_id": self.guild_id})
        links = existing_record.get("links", {}) if existing_record else {}

        if selected_value in links.values():
            selected_key = next(key for key, value in links.items() if value == selected_value)
            del links[selected_key]

            design_config.update_one({"guild_id": self.guild_id}, {"$set": {"links": links}})

            await interaction.response.send_message(f"Payment link '{selected_key}' has been deleted from MongoDB.", ephemeral=True)
        else:
            await interaction.response.send_message("The selected payment link does not exist.", ephemeral=True)