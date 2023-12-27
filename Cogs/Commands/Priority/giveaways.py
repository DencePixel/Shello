from typing import Any
from discord.ext import commands, tasks
import discord.ext
from discord import app_commands
from discord import Color
import discord
from pymongo import MongoClient
from DataModels.guild import BaseGuild
import os

from DataModels.user import BaseUser
import datetime
import re
import time
from dotenv import load_dotenv
load_dotenv()
import random
from Cogs.emojis import approved_emoji, denied_emoji, alert_emoji
from Util.Yaml import Load_yaml


Base_User = BaseUser()
Base_Guild = BaseGuild()

class GiveawayEnter(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = MongoClient(self.mongo_uri)

        
        
        self.giveaways_db = self.cluster[self.config["collections"]["Giveaways"]["database"]]
        self.active_giveaways = self.giveaways_db[self.config["collections"]["Giveaways"]["active"]]

    @discord.ui.button(label="🎊", style=discord.ButtonStyle.green, custom_id=f"persistent_view:giveawayenter")
    async def giveaway(self, interaction: discord.Interaction, button: discord.Button):
        result = self.active_giveaways.find_one({"message_id": interaction.message.id})

        if not result:
            return await interaction.response.send_message(content=f"I could not find that giveaway in my database.", ephemeral=True)

        entrants = result.get("entrants", [])
        entries = result.get("entries", 0)

        if interaction.user.id in entrants:
            entrants.remove(interaction.user.id)
            entries -= 1
            response_message = f"You have been removed from the giveaway."
        else:
            entrants.append(interaction.user.id)
            entries += 1
            response_message = f"You have been entered into the giveaway."

        self.active_giveaways.update_one({"message_id": interaction.message.id}, {"$set": {"entrants": entrants, "entries": entries}})

        prize = result.get("prize")
        new_content = result.get("description")
        formatted_enddate = discord.utils.format_dt(result.get("end_date"), style="R")
        formatted_enddate_long = discord.utils.format_dt(result.get("end_date"), style=f"F")
        embed = discord.Embed(title=prize, description=f"{new_content}**Ends:** {formatted_enddate} ({formatted_enddate_long})\n**Hosted By:** <@!{result.get('host')}\n**Entries:** {entries}\n**Winners:** {result.get('winners')}", timestamp=discord.utils.utcnow(), color=discord.Color.dark_embed())
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(content=response_message, ephemeral=True)

class Giveaways(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.check_giveaway_status.start()
        
        self.client = client
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = MongoClient(self.mongo_uri)

        
        
        self.giveaways_db = self.cluster[self.config["collections"]["Giveaways"]["database"]]
        self.active_giveaways = self.giveaways_db[self.config["collections"]["Giveaways"]["active"]]
        
    def parse_duration(self, duration):
        match = re.match(r'(?:(\d+)D)?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?(?:(\d+)W)?', duration)
        if not match:
            raise commands.BadArgument(
                "Invalid duration format. Use a combination of D (days), H (hours), M (minutes), S (seconds), W (weeks). Example: `3D2H30M`"
            )

        days, hours, minutes, seconds, weeks = map(lambda x: int(x) if x else 0, match.groups(default='0'))

        total_duration = datetime.datetime.utcnow() + datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds, weeks=weeks
        )
        return total_duration
        
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.hybrid_group(invoke_without_command=False, name="giveaway")
    async def giveaway(self, ctx):
        return
    
    @giveaway.error
    async def claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(time.time() + error.retry_after)
            embed = discord.Embed(title='Command is on Cooldown',
                              description=f'This command is on cooldown. Please try again <t:{remaining_time}:R>',
                              color=0xFF0000)
            await ctx.send(embed=embed)
        else:
            raise error
    
    
    @tasks.loop(seconds=2)
    async def check_giveaway_status(self):
        now = datetime.datetime.now()

        
        
        for document in self.active_giveaways.find({"end_date": {"$lt": now}}):
            winners_count = document.get("winners", 1)
            entrants = document.get("entrants", [])
            prize = document.get("prize")
            new_content = document.get("description")
            entries = document.get("entries", 0)
            message_id = document.get("message_id")
            channel_id = document.get("channel")
            channel = self.client.get_channel(channel_id)
            formatted_enddate = discord.utils.format_dt(document.get("end_date"), style="R")
            formatted_enddate_long = discord.utils.format_dt(document.get("end_date"), style=f"F")
            winner_string = ""
        

            if len(entrants) > 0:
                chosen_winners = random.sample(entrants, min(winners_count, len(entrants)))
                for winner in chosen_winners:
                    winner_string += f" <@!{winner}>"
                
            
            embed = discord.Embed(title=prize, description=f"{new_content}**Ended:** {formatted_enddate} ({formatted_enddate_long})\n**Hosted By:** <@!{document.get('host')}>\n**Entries:** {entries}\n**Winners:** {winner_string}", timestamp=discord.utils.utcnow(), color=discord.Color.dark_embed())
            message = await channel.fetch_message(message_id)
            if not message:
                return await channel.send(content=f"{denied_emoji} **I can't find the giveaway message.**")
            await message.edit(embed=embed, view=None)
            await message.reply(content=f"👏 {winner_string}")
            
            
            self.active_giveaways.delete_one({"message_id": document["message_id"]})

    
    @giveaway.command(name=f"start")
    async def setup(
        self,
        ctx: commands.Context, 
        winners: int,
        duration: str,
        *,
        prize: str):

        try:
            
            end_datetime = self.parse_duration(duration)
        except:
            return await ctx.send(content=f"That duration is invalid.")
        
        formatted_enddate = discord.utils.format_dt(end_datetime, style='R')
        format_enddate_long = discord.utils.format_dt(end_datetime, style='F')

        new_content = " "
        embed = discord.Embed(title=prize, description=f"{new_content}**Ends:** {formatted_enddate} ({format_enddate_long})\n**Hosted By:** {ctx.author.mention}\n**Entries:** 0\n**Winners:** {winners}", timestamp=discord.utils.utcnow(), color=discord.Color.dark_embed())
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.display_name)       
        view = GiveawayEnter()
        message = await ctx.send(embed=embed, view=view)
        self.active_giveaways.insert_one({"guild_id": ctx.guild.id,"channel": ctx.channel.id,"message_id": message.id, "prize": prize, "host": ctx.author.id, "end_date": end_datetime, "winners": winners, "description": new_content, "entries": 0, "entrants":[] })
        
    @giveaway.command(name="end")
    async def end_giveaway(self, ctx: commands.Context, message_id: int):
        result = self.active_giveaways.find_one({"message_id": message_id})

        if not result:
            return await ctx.send(content=f"I could not find that giveaway in my database.")

        entrants = result.get("entrants", [])
        winners_count = result.get("winners", 1)
        prize = result.get("prize")
        new_content = result.get("description")
        entries = result.get("entries", 0)
        formatted_enddate = discord.utils.format_dt(result.get("end_date"), style="R")
        formatted_enddate_long = discord.utils.format_dt(result.get("end_date"), style=f"F")
        winner_string = ""

        if len(entrants) > 0:
            chosen_winners = random.sample(entrants, min(winners_count, len(entrants)))
            for winner in chosen_winners:
                winner_string += f" <@!{winner}>"

        embed = discord.Embed(
            title=prize,
            description=f"{new_content}**Ended:** {formatted_enddate} ({formatted_enddate_long})\n**Hosted By:** <@!{result.get('host')}>\n**Entries:** {entries}\n**Winners:** {winner_string}",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.dark_embed()
        )
        message = await ctx.fetch_message(message_id)
        if not message:
            return await ctx.send(content=f"{denied_emoji} **I can't find the giveaway message.**")
        await message.edit(embed=embed, view=None)
        await message.reply(content=f"👏 {winner_string}")
        self.active_giveaways.delete_one({"message_id": message_id})

    @giveaway.command(name="reroll")
    async def reroll_giveaway(self, ctx: commands.Context, message_id: int):
        result = self.active_giveaways.find_one({"message_id": message_id})

        if not result:
            return await ctx.send(content=f"I could not find that giveaway in my database.")

        entrants = result.get("entrants", [])
        winners_count = result.get("winners", 1)
        prize = result.get("prize")
        new_content = result.get("description")
        entries = result.get("entries", 0)
        formatted_enddate = discord.utils.format_dt(result.get("end_date"), style="R")
        formatted_enddate_long = discord.utils.format_dt(result.get("end_date"), style=f"F")
        winner_string = ""

        if len(entrants) > 0:
            chosen_winners = random.sample(entrants, min(winners_count, len(entrants)))
            for winner in chosen_winners:
                winner_string += f" <@!{winner}>"

        embed = discord.Embed(
            title=prize,
            description=f"{new_content}**Ended:** {formatted_enddate} ({formatted_enddate_long})\n**Hosted By:** <@!{result.get('host')}>\n**Entries:** {entries}\n**Winners:** {winner_string}",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.dark_embed()
        )
        message = await ctx.fetch_message(message_id)
        if not message:
            return await ctx.send(content=f"{denied_emoji} **I can't find the giveaway message.**")
        await message.edit(embed=embed)
        await message.reply(content=f"👏 {winner_string}")

    @giveaway.command(name="modify")
    async def modify_giveaway(
        self,
        ctx: commands.Context,
        message_id: int,
        new_duration: str = None,
        new_prize: str = None
    ):
        result = self.active_giveaways.find_one({"message_id": message_id})

        if not result:
            return await ctx.send(content=f"I could not find that giveaway in my database.")

        if new_duration:
            try:
                end_datetime = self.parse_duration(new_duration)
                formatted_enddate = discord.utils.format_dt(end_datetime, style='R')
                formatted_enddate_long = discord.utils.format_dt(end_datetime, style='F')
                result["end_date"] = end_datetime
            except:
                return await ctx.send(content=f"That duration is invalid.")
        
        if new_prize:
            result["prize"] = new_prize

        self.active_giveaways.update_one({"message_id": message_id}, {"$set": result})
        await ctx.send(content=f"Giveaway with message ID {message_id} has been modified.")
    
    
        

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Giveaways(client))
