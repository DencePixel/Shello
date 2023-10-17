import discord
import random
from discord import Embed
from discord.ext import commands
from Cogs.emojis import *

class nocmd(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @commands.Cog.listener(name="on_command_error")
    async def commanderror(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{denied_emoji} **{ctx.author.display_name},** I can't find the command you referenced!")

    @commands.Cog.listener(name="on_application_command_error")
    async def appcommanderror(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandNotFound):
            await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** I can't find the command you referenced!")
            
    @commands.Cog.listener(name="on_error")
    async def error(self, interaction: discord.Interaction, error):
        error_id = random.random(1, 1000)
        embed = discord.Embed(title=f"Oops!", description=f"Looks like an error has occured, I have notifed the developers and they will fix me shortly!\n Error ID: {error_id}", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        await interaction.response.send_message(embed=embed)
        developer_Embed = discord.Embed(description=f"```py\n{error}```")
        developer_Embed.set_footer(text=f"Error ID: {error_id}")
        channel = self.client.get_channel(1163097406666199100)
        await channel.send(content=error_id, embed=embed)
            
        

        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(nocmd(client))
