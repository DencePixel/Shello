import discord
from jsonschema import validate, exceptions
import sqlite3
import json
from Cogs.Commands.Config.Channels.DesignLog.utils import *

class DesignLogChannel(discord.ui.ChannelSelect):
    def __init__(self, firstinteraction, mainmessage):
        super().__init__(placeholder='Where would you like to log completed designs?', max_values=1, min_values=1)
        self.interaction = firstinteraction
        self.message = mainmessage

    async def callback(self, interaction: discord.Interaction):
        if self.interaction.author.id != interaction.user.id:
            await interaction.response.send_message(f"<:Failed:1143843095994179675> This is not your dropdown!", ephemeral=True)
            return

        channel_id = int(self.values[0].id)
        channel2 = interaction.guild.get_channel(channel_id)
        guild_id = interaction.guild.id
        
        conn = sqlite3.connect('Data/DesignLog/DesignLog.sql')
        cur = conn.cursor()
        embed = discord.Embed(description=f"Design Logging Channel:\n``>`` {channel2.mention}", color=discord.Color.dark_embed())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)


        try:
            validate_existing_guild(cur, guild_id)
        except exceptions.ValidationError as e:
            error_message = str(e)
            if error_message == "Design entry already exists for this guild.":
                update_existing_entry(cur, guild_id, channel_id)
                conn.commit()
                conn.close()
                await interaction.response.send_message(f"<:Approved:1143843098468827136> I have updated the current configuration!", embed=embed)
                return
            await interaction.response.send_message(f"<:Failed:1143843095994179675> Design validation failed: {e}", ephemeral=True)
            conn.close()
            return

        insert_or_replace_design_info(cur, guild_id, channel_id)
        conn.commit()
        conn.close()
        await interaction.response.send_message(embed=embed)
