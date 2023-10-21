from discord import app_commands
from discord import Color
import discord
from discord.ext import commands
import discord.ext
from discord import app_commands
from discord import Color
import discord
from discord.ext import commands
import discord.ext
from pymongo import MongoClient
from Cogs.DataModels.guild import BaseGuild
from Cogs.DataModels.user import BaseUser

Base_User = BaseUser()
Base_Guild = BaseGuild()




    
    

            


        

    
class PaymentCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cluster = MongoClient("mongodb+srv://markapi:6U9wkY5D7Hat4OnG@shello.ecmhytn.mongodb.net/")
        self.payment_db = self.cluster["PaymentLinkSystem"]
        self.payment_config = self.payment_db["Payment Config"]
        self.design_Db = self.cluster["DesignSystem"]
        self.design_config = self.design_Db["design config"]



    @commands.hybrid_group(name="design", description=f"Design based commands")
    async def design(self, ctx):
        pass

    @design.command(name="log")
    async def designlog(self, ctx: commands.Context, price: int, customer: discord.Member, link,*, product: str):
        guild_id = ctx.guild.id
        existing_record = await self.fetch_design_config(guild_id)

        if not link:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you must specify a link.")

        if not existing_record:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. ")
        
        designer_role_id, designer_log_channel_id = await Base_Guild.fetch_design_config(ctx.guild.id)

        
        
        designer_channel = self.client.get_channel(designer_log_channel_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)
        
        if designer_channel is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. (no design channel)")
        
        if designer_role is None:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module. (no designer role)" )
        
        if designer_role not in ctx.author.roles:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you are missing the required roles.")

            
        
        log_Embed = discord.Embed(description=f"**Order Log**\n\n> **designer:** {ctx.author.mention}\n> **Product:** {product}\n> **Price:** {price}", color=discord.Color.dark_embed(), timestamp=discord.utils.utcnow())
        log_Embed.set_footer(text=f"Shello Systems")
        log_Embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)
        await designer_channel.send(embed=log_Embed)
        


            
        
        
        

        
        
        
        
        
        


    @designlog.autocomplete('link')
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        guild_id = interaction.guild.id
        payment_links = await Base_Guild.fetch_payment_links(guild_id)

        choices = [
            app_commands.Choice(name=link, value=link) for link in payment_links if current.lower() in link.lower()
        ]

        return choices
        
 
    

            

        
            
        
    

async def setup(client: commands.Bot) -> None:
    await client.add_cog(PaymentCog(client))