import discord
import random
from discord.ext import commands
from discord.ui import Button


from Cogs.emojis import denied_emoji

class ErrorCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client


    @commands.Cog.listener(name="on_application_command_error")
    async def appcommanderror(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandNotFound):
            return await interaction.response.send_message(F"{denied_emoji} **{interaction.user.display_name},** this command does not exist.")
        
        
        error_id = random.randint(1, 1000)
        embed = discord.Embed(
            title=f"Oops!",
            description=f"Looks like an error has occurred. The developers have been notified, and they will fix me shortly!",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        developer_embed.set_footer(text=f"Error ID: {error_id}")

        developer_embed = discord.Embed(description=f"```py\n{error}```")
        button = Button(style=discord.ButtonStyle.link, label="Report Error", url="https://discord.gg/FFZzpZ9MMX")
        view = discord.ui.View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)
        developer_embed.set_footer(text=f"Error ID: {error_id}")
        channel = self.client.get_channel(1165730359888052304)
        await channel.send(content=error_id, embed=developer_embed)

    @commands.Cog.listener(name="on_error")
    async def error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandNotFound):
            return await interaction.response.send_message(F"{denied_emoji} **{interaction.user.display_name},** this command does not exist.")
        error_id = random.randint(1, 1000)
        embed = discord.Embed(
            title=f"Oops!",
            description=f"Looks like an error has occurred. The developers have been notified, and they will fix me shortly!\n",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=f"Error ID: {error_id}")

        developer_embed = discord.Embed(description=f"```py\n{error}```")
        button = Button(style=discord.ButtonStyle.link, label="Report Error", url="https://discord.gg/FFZzpZ9MMX")
        view = discord.ui.View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)
        developer_embed.set_footer(text=f"Error ID: {error_id}")
        channel = self.client.get_channel(1165730359888052304)
        await channel.send(content=error_id, embed=developer_embed)
        
        
    @commands.Cog.listener(name="on_command_error")
    async def cerror(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(F"{denied_emoji} **{ctx.author.display_name},** this command does not exist.")
        error_id = random.randint(1, 1000)
        embed = discord.Embed(
            title=f"Oops!",
            description=f"Looks like an error has occurred.",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=f"Error ID: {error_id}")

        developer_embed = discord.Embed(description=f"```py\n{error}```")
        button = Button(style=discord.ButtonStyle.link, label="Report Error", url="https://discord.gg/FFZzpZ9MMX")
        view = discord.ui.View()
        view.add_item(button)
        await ctx.send(embed=embed, view=view)
        developer_embed.set_footer(text=f"Error ID: {error_id}")
        channel = self.client.get_channel(1165730359888052304)
        await channel.send(content=error_id, embed=developer_embed)

    async def send_error_message(self, ctx_or_interaction, embed):
        button = Button(style=discord.ButtonStyle.link, label="Report Error", url="https://discord.gg/FFZzpZ9MMX")
        view = discord.ui.View()
        view.add_item(button)

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ErrorCog(client))