import discord
import motor.motor_asyncio
from Util.Yaml import Load_yaml


import datetime
import discord
from Cogs.emojis import approved_emoji, alert_emoji, denied_emoji, space_emoji, right_Emoji
from discord.ext import commands, tasks
from DataModels.guild import BaseGuild
from roblox import Client
from Util.helpers import convert_duration

Base_Guild = BaseGuild()


class ExtendLoaModal(discord.ui.Modal):
    def __init__(self, author,original_user, title='Edit the users loa Duration'):
        self.roblox_client = Client()
        self.author = author
        self.original_user = original_user
        
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]

        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]
        self.overall_leaves = self.leaves_db[self.config["collections"]["Leaves"]["overall"]]
        self.active_leaves = self.leaves_db[self.config["collections"]["Leaves"]["active"]]
        super().__init__(title=title)

        self.Message = discord.ui.TextInput(
            label='Edit Duration',
            style=discord.TextStyle.short,
            placeholder='E.g: 5D',
            required=True,
            max_length=500,
        )

        self.add_item(self.Message)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = interaction.guild_id
        try:
            new_end_duration = convert_duration(duration_str=self.Message.value)
        except ValueError:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** that duration is invalid.")

        active_loa = self.active_leaves.find_one({"guild_id": guild_id, "author_id": self.author.id})

        if active_loa:
            end_date = active_loa.get("end_date")
            new_end_timedelta = new_end_duration - end_date
            new_end = end_date + new_end_timedelta
            await self.active_leaves.update_one(
                {"guild_id": guild_id, "author_id": self.author.id},
                {"$set": {"end_date": new_end}}
            )
        else:
            return await interaction.followup.send(
                content=f"{denied_emoji} **{interaction.user.display_name},** I could not find that."
            )

        return await interaction.followup.send(
            content=f"<:Approved:1163094275572121661> **{interaction.user.display_name},** I have updated the LOA duration **{self.Message.value}**!")
class LeaveAdminOptions(discord.ui.Select):
    def __init__(self, author, original_user):
        self.author = author
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]

        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]
        self.overall_leaves = self.leaves_db[self.config["collections"]["Leaves"]["overall"]]
        self.active_leaves = self.leaves_db[self.config["collections"]["Leaves"]["active"]]
        self.original_author = original_user
        options = [
            discord.SelectOption(label='Extend LOA', description='Extend the duration of a LOA.', emoji='<:order_updated:1177327822721794058>', value="extend"),
            discord.SelectOption(label='End LOA Early', description='End a LOA early.', emoji='<:order_cancel:1177328205410091138>', value="end")
        ]

        super().__init__(placeholder='Please select an option.', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.original_author.id != interaction.user.id:
            return await interaction.response.send_message(f"{denied_emoji} **{interaction.user.display_name},** this is not your view.", ephemeral=True)
        existing_record = await self.leaves_config.find_one({"guild_id": interaction.guild.id})
        if not existing_record:
            return await interaction.response.send_message(content=f"{denied_emoji} **{interaction.user.display_name},** you need to setup the LOA module.", ephemeral=True)

        channel = existing_record.get("loa_channel")
        
        if self.values[0] == "extend":
            return await interaction.response.send_modal(ExtendLoaModal(author=self.author))
        
        
        if self.values[0] == "end":
            find = await self.active_leaves.find_one({"guild_id": interaction.guild.id, "author_id": self.author.id})     
            if not find:
                return await interaction.response.send_message(content=f"{denied_emoji} **{interaction.user.display_name},** I could not find that users LOA.", ephemeral=True)
            
            user_id = find.get("author_id")
            delete = await self.active_leaves.delete_one(filter=find)
            user = interaction.guild.get_member(user_id)
            if user:
                user_embed = discord.Embed(title=f"Loa Ended Early", description=f"{interaction.user.mention} has ended your LOA early at **{interaction.guild.name}**.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
                user_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
                await user.send(embed=user_embed)
            log_embed = discord.Embed(title=f"Loa Ended Early", description=f"{interaction.user.mention} has ended {user.mention}'s LOA early.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            await interaction.guild.get_channel(channel).send(embed=log_embed)
            
            if delete.deleted_count == 1:
                return await interaction.response.send_message(content=f"{approved_emoji} **{interaction.user.display_name},** I have ended their LOA early.")

            
            
            
            


class LeaveRequestButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label='Approve', style=discord.ButtonStyle.green, custom_id='persistent_view:accept')
    async def acceptloa(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.roblox_client = Client()
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)

        
        
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]
        self.overall_leaves = self.leaves_db[self.config["collections"]["Leaves"]["overall"]]
        self.active_leaves = self.leaves_db[self.config["collections"]["Leaves"]["active"]]

        await interaction.response.defer()
        design_config = await Base_Guild.fetch_design_config(guild_id=interaction.guild.id)
        if not design_config:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** you need to setup the design module.", ephemeral=True)
        designer_role_id = design_config.get("designer_role_id")
        staff_Role_id = design_config.get("staff_role_id")
        staff_role = interaction.guild.get_role(staff_Role_id)
        designer_role = interaction.guild.get_role(designer_role_id)
        if staff_role not in interaction.user.roles:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** only staff members can use this.")
        loa_info = self.active_leaves.find_one({"guild_id": interaction.guild.id, "message_id": interaction.message.id})
        if not loa_info:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** I can't find that LOA.")
        message_id = loa_info.get("message_id")
        requester_id = loa_info.get("author_id")
        existing_record = await self.leaves_config.find_one({"guild_id": interaction.guild.id})
        if not existing_record:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** you need to setup the LOA module.", ephemeral=True)
        channel_id = existing_record.get("loa_channel")
        role_id = existing_record.get("leave_role")
        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                author = interaction.guild.get_member(requester_id)
                if role not in author.roles:
                    author.add_roles(role)
        channel = interaction.guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        if not message:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** I can't find the message associated to the LOA.")
        requester_id = loa_info.get("author_id")
        reason = loa_info.get("reason")
        start_date = loa_info.get("start_date")
        end_date = loa_info.get("end_date")
        timestamp_finish = discord.utils.format_dt(end_date, style="R")
        timestamp_start = discord.utils.format_dt(start_date, style="R")
        overall_loas = int(await self.overall_leaves.count_documents({"guild_id": interaction.guild.id, "author_id": requester_id}))
        embed = discord.Embed(title=f"Accepted LOA", description=f"**Requester Information:**\n{space_emoji}{right_Emoji}**User:** <@!{requester_id}>\n{space_emoji}{right_Emoji}**User ID:** {requester_id}\n{space_emoji}{right_Emoji}**User Leaves:** {overall_loas}\n\n**Loa Information:**\n{space_emoji}{right_Emoji} **Start Date:** {timestamp_start}\n{space_emoji}{right_Emoji} **End Date:** {timestamp_finish}\n{space_emoji}{right_Emoji} **Reason:** {reason}\n{space_emoji}{right_Emoji} **Accepted By:** {interaction.user.mention}", color=discord.Color.green())
        find_query = {"guild_id": interaction.guild.id, "author_id": requester_id, "message_id": message_id, "reason": reason, "start_date": start_date, "end_date": end_date, "status": "pending"}
        update_query = { "$set": { "status": "active" } }
        await self.active_leaves.update_one(find_query, update_query)
        for child in self.children:
            child.disabled = True
        member = interaction.guild.get_member(requester_id)
        try:
            await member.send(embed=embed, content=f"{approved_emoji} **Accepted by @{interaction.user.display_name}.**")
        except Exception as e:
            print(f"Error occured in guild {interaction.guild.id}\n\n{e}")
            return await interaction.followup.send(content=f"{denied_emoji} Something went wrong when DMing the requester.")
        return await message.edit(content=f"{approved_emoji} **Accepted by @{interaction.user.display_name}.**", embed=embed, view=self)
    
    @discord.ui.button(label='Deny', style=discord.ButtonStyle.red, custom_id='persistent_view:decline')
    async def declineloa(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.roblox_client = Client()
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)

        
        
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]
        self.overall_leaves = self.leaves_db[self.config["collections"]["Leaves"]["overall"]]
        self.active_leaves = self.leaves_db[self.config["collections"]["Leaves"]["active"]]

        await interaction.response.defer()
        design_config = await Base_Guild.fetch_design_config(guild_id=interaction.guild.id)
        if not design_config:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** you need to setup the design module.", ephemeral=True)
        designer_role_id = design_config.get("designer_role_id")
        staff_Role_id = design_config.get("staff_role_id")
        staff_role = interaction.guild.get_role(staff_Role_id)
        designer_role = interaction.guild.get_role(designer_role_id)
        if staff_role not in interaction.user.roles:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** only staff members can use this.")
        loa_info = await self.active_leaves.find_one({"guild_id": interaction.guild.id, "message_id": interaction.message.id})
        if not loa_info:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** I can't find that LOA.")
        message_id = loa_info.get("message_id")
        existing_record = await self.leaves_config.find_one({"guild_id": interaction.guild.id})
        if not existing_record:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** you need to setup the LOA module.", ephemeral=True)
        channel_id = existing_record.get("loa_channel")
        channel = interaction.guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        if not message:
            return await interaction.followup.send(content=f"{denied_emoji} **{interaction.user.display_name},** I can't find the message associated to the LOA.")
        requester_id = loa_info.get("author_id")
        reason = loa_info.get("reason")
        start_date = loa_info.get("start_date")
        end_date = loa_info.get("end_date")
        timestamp_finish = discord.utils.format_dt(end_date, style="R")
        timestamp_start = discord.utils.format_dt(start_date, style="R")
        overall_loas = int(await self.overall_leaves.count_documents({"guild_id": interaction.guild.id, "author_id": requester_id}))
        embed = discord.Embed(title=f"Denied LOA", description=f"**Requester Information:**\n{space_emoji}{right_Emoji}**User:** <@!{requester_id}>\n{space_emoji}{right_Emoji}**User ID:** {requester_id}\n{space_emoji}{right_Emoji}**User Leaves:** {overall_loas}\n\n**Loa Information:**\n{space_emoji}{right_Emoji} **Start Date:** {timestamp_start}\n{space_emoji}{right_Emoji} **End Date:** {timestamp_finish}\n{space_emoji}{right_Emoji} **Reason:** {reason}\n{space_emoji}{right_Emoji} **Denied By:** {interaction.user.mention}", color=discord.Color.red())
        find_query = {"guild_id": interaction.guild.id, "author_id": requester_id, "message_id": message_id, "reason": reason, "start_date": start_date, "end_date": end_date, "status": "pending"}
        await self.active_leaves.delete_one(find_query)
        for child in self.children:
            child.disabled = True
        member = interaction.guild.get_member(requester_id)
        try:
            await member.send(embed=embed, content=f"{approved_emoji} **Declined by @{interaction.user.display_name}.**")
        except Exception as e:
            return await interaction.followup.send(content=f"{denied_emoji} Something went wrong when DMing the requester.")
        return await message.edit(content=f"{approved_emoji} **Declined by @{interaction.user.display_name}.**", embed=embed, view=self)
    

        
class LoaCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.client = bot
        self.roblox_client = Client()
        self.config = Load_yaml()  
        self.mongo_uri = self.config["mongodb"]["uri"]
        
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        
        self.leaves_db = self.cluster[self.config["collections"]["Leaves"]["database"]]
        self.leaves_config = self.leaves_db[self.config["collections"]["Leaves"]["config"]]
        self.overall_leaves = self.leaves_db[self.config["collections"]["Leaves"]["overall"]]
        self.active_leaves = self.leaves_db[self.config["collections"]["Leaves"]["active"]]
        
        self.check_expired_loas.start()
        
    @tasks.loop(seconds=10)
    async def check_expired_loas(self):
        current_time = datetime.datetime.utcnow()

        cursor = self.active_leaves.find({"end_date": {"$lte": current_time}, "status": "active"})
        expired_loas = await cursor.to_list(length=None)  
        for loa in expired_loas:
            guild_id = loa["guild_id"]
            author_id = loa["author_id"]
            message_id = loa["message_id"]
            reason = loa["reason"]
            config = await self.leaves_config.find_one({"guild_id": guild_id})
            if not config:
                continue

            main_guild = self.client.get_guild(guild_id)
            role_id = config.get("leave_role")
            if role_id:
                role = main_guild.get_role(role_id)
                if role:
                    user = main_guild.get_member(author_id)
                    if role in user.roles:
                        user.remove_roles(role)

            await self.active_leaves.delete_one({"guild_id": guild_id, "author_id": author_id, "message_id": message_id})
            await self.overall_leaves.insert_one({"guild_id": guild_id, "author_id": author_id, "reason": reason})

            guild = self.client.get_guild(guild_id)
            member = guild.get_member(author_id)

            if guild and member:
                entry = await self.leaves_config.find_one({"guild_id": guild_id})
                if not entry:
                    continue

                channel_id = entry.get("loa_channel")
                if not channel_id:
                    continue

                channel = guild.get_channel(channel_id)
                message = await channel.fetch_message(message_id)

                if message:
                    embed = discord.Embed(title=f"Expired Loa", description=f"{member.mention}'s LOA has expired.")
                    await message.edit(content=f"****", embed=None, view=None)

                    try:
                        embed = discord.Embed(title="Expired LOA", description=f"Your LOA at **{guild.name}** has expired.", color=discord.Color.red())
                        await member.send(embed=embed)
                        
                    except Exception as e:
                        print(f"Error occurred when DMing the requester: {e}")
        

        
    @commands.hybrid_group(name="leave", description=f"Loa based commands")
    async def loagroup(self, ctx):
        pass
        
        
    @loagroup.command(name="request", description="Manage your LOA")
    async def requestloa(self, ctx: commands.Context, duration: str, *, reason: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        active_leave = await self.active_leaves.find_one({"guild_id": ctx.guild.id, "author_id": ctx.author.id})
        if active_leave:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you currently have an active LOA")
        existing_record = await self.leaves_config.find_one({"guild_id": ctx.guild.id})
        if not existing_record:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup the LOA module.")
        
        design_config = await Base_Guild.fetch_design_config(guild_id=ctx.guild.id)
        if not design_config:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup the design module.")
        designer_role_id = design_config.get("designer_role_id")
        staff_Role_id = design_config.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_Role_id)
        designer_role = ctx.guild.get_role(designer_role_id)
        if staff_role not in ctx.author.roles:
            print("only staff")
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** only staff members can use this.")
        overall_loas = int(await self.overall_leaves.count_documents({"guild_id": ctx.guild.id, "author_id": ctx.author.id}))
        try:
            finish = convert_duration(duration)
        except:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you have provided an invalid duration.")
        timestamp_finish = discord.utils.format_dt(finish, style="R")
        timestamp_start = discord.utils.format_dt(datetime.datetime.utcnow(), style="R")
        embed = discord.Embed(title=f"Pending LOA", description=f"**Requester Information:**\n{space_emoji}{right_Emoji}**User:** {ctx.author.mention}\n{space_emoji}{right_Emoji}**User ID:** {ctx.author.id}\n{space_emoji}{right_Emoji}**User Leaves:** {overall_loas}\n\n**Loa Information:**\n{space_emoji}{right_Emoji} **Start Date:** {timestamp_start}\n{space_emoji}{right_Emoji} **End Date:** {timestamp_finish}\n{space_emoji}{right_Emoji} **Reason:** {reason}", color=discord.Color.orange())
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        channel = existing_record.get("loa_channel")
        if not channel:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup a LOA channel.")
        discord_channel = ctx.guild.get_channel(channel)
        message2 = await discord_channel.send(embed=embed, view=LeaveRequestButtons())
        await self.active_leaves.insert_one({"guild_id": ctx.guild.id, "author_id": ctx.author.id, "status": "pending", "start_date": datetime.datetime.utcnow(), "end_date": finish, "reason": reason, "message_id": message2.id})
        return await message.edit(content=f"{approved_emoji} **{ctx.author.display_name},** I have succesfully posted your LOA request.")
    
    @loagroup.command(name=f"manage", description=f"Manage someones LOA")
    @commands.guild_only()
    async def loaadmin(self, ctx: commands.Context, member: discord.Member):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        design_config = await Base_Guild.fetch_design_config(guild_id=ctx.guild.id)
        if not design_config:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup the design module.")
        staff_role_id = design_config.get("staff_role_id")
        if staff_role_id is None:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup the a staff role.")
        staff_role = ctx.guild.get_role(staff_role_id)
        if staff_role not in ctx.author.roles:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you can't use this.")
        loa_info = await self.active_leaves.find_one({"guild_id": ctx.guild.id, "author_id": member.id, "status": "active"})
        if not loa_info:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** this user does not have an active LOA.")
        requester_id = loa_info.get("author_id")
        reason = loa_info.get("reason")
        start_date = loa_info.get("start_date")
        end_date = loa_info.get("end_date")
        timestamp_finish = discord.utils.format_dt(end_date, style="R")
        timestamp_start = discord.utils.format_dt(start_date, style="R")
        overall_loas = int(await self.overall_leaves.count_documents({"guild_id": ctx.guild.id, "author_id": requester_id}))
        dropdown = LeaveAdminOptions(author=member, original_user= ctx.author)
        view = discord.ui.View()
        view.add_item(dropdown)
        embed = discord.Embed(title=f"Active LOA", description=f"**Requester Information:**\n{space_emoji}{right_Emoji}**User:** <@!{requester_id}>\n{space_emoji}{right_Emoji}**User ID:** {requester_id}\n{space_emoji}{right_Emoji}**User Leaves:** {overall_loas}\n\n**Loa Information:**\n{space_emoji}{right_Emoji} **Start Date:** {timestamp_start}\n{space_emoji}{right_Emoji} **End Date:** {timestamp_finish}\n{space_emoji}{right_Emoji} **Reason:** {reason}\n", color=discord.Color.light_embed())
        embed.set_thumbnail(url=member.display_avatar.url)
        await message.edit(content=f"{approved_emoji} **{ctx.author.display_name},** here is that LOA.", embed=embed, view=view)
        
    @loagroup.command(name=f"view", description=f"View a LOA for someone")
    @commands.guild_only()
    async def loaview(self, ctx: commands.Context, member: discord.Member):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        design_config = await Base_Guild.fetch_design_config(guild_id=ctx.guild.id)
        if not design_config:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup the design module.")
        staff_role_id = design_config.get("staff_role_id")
        if staff_role_id is None:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you need to setup the a staff role.")
        staff_role = ctx.guild.get_role(staff_role_id)
        if staff_role not in ctx.author.roles:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you can't use this.")
        loa_info = await self.active_leaves.find_one({"guild_id": ctx.guild.id, "author_id": member.id, "status": "active"})
        if not loa_info:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** this user does not have an active LOA.")
        requester_id = loa_info.get("author_id")
        reason = loa_info.get("reason")
        start_date = loa_info.get("start_date")
        end_date = loa_info.get("end_date")
        timestamp_finish = discord.utils.format_dt(end_date, style="R")
        timestamp_start = discord.utils.format_dt(start_date, style="R")
        overall_loas = int(self.overall_leaves.count_documents({"guild_id": ctx.guild.id, "author_id": requester_id}))
        embed = discord.Embed(title=f"Active LOA", description=f"**Requester Information:**\n{space_emoji}{right_Emoji}**User:** <@!{requester_id}>\n{space_emoji}{right_Emoji}**User ID:** {requester_id}\n{space_emoji}{right_Emoji}**User Leaves:** {overall_loas}\n\n**Loa Information:**\n{space_emoji}{right_Emoji} **Start Date:** {timestamp_start}\n{space_emoji}{right_Emoji} **End Date:** {timestamp_finish}\n{space_emoji}{right_Emoji} **Reason:** {reason}\n", color=discord.Color.light_embed())
        embed.set_thumbnail(url=member.display_avatar.url)
        await message.edit(content=f"{approved_emoji} **{ctx.author.display_name},** here is that LOA.", embed=embed)
        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(LoaCog(client))