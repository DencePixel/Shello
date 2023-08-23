import discord
import random
from discord import Embed
from discord.ext import commands

class nocmd(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @commands.Cog.listener(name="on_command_error")
    async def commanderror(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(colour=discord.Colour(0x2f3136))
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            embed.add_field(name="Oops!", value="I cannot find the command you referenced, please try typing a different command! If you believe this is a mistake please contact us in our [support server](https://discord.gg/26pgMKVwpW)")
            await ctx.send(embed=embed)
            
    @commands.Cog.listener(name="on_application_command_error")
    async def appcommanderror(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(colour=discord.Colour(0x2f3136))
            embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="Oops!", value="I cannot find the command you referenced, please try typing a different command! If you believe this is a mistake please contact us in our [support server](https://discord.gg/26pgMKVwpW)")
            await interaction.response.send_message(embed=embed)
            
    @commands.Cog.listener(name="on_error")
    async def error(self, interaction: discord.Interaction, error):
        error_id = random.random(1, 1000)
        embed = discord.Embed(title=f"Oops!", description=f"Looks like an error has occured, I have notifed the developers and they will fix me shortly!\n Error ID: {error_id}", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        await interaction.response.send_message(embed=embed)
        developer_Embed = discord.Embed(description=f"```py\n{error}```")
        developer_Embed.set_footer(text=f"Error ID: {error_id}")
        channel = self.client.get_channel(1144021005141020692)
        await channel.send(content=error_id, embed=embed)
            
        

        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(nocmd(client))
