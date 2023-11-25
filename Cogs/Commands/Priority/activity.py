from discord.ext import commands, tasks
import discord
from pymongo import MongoClient
from DataModels.guild import BaseGuild
from DataModels.user import BaseUser
from Util.Yaml import Load_yaml
import asyncio
import calendar
from datetime import datetime, timedelta, date

Base_User = BaseUser()
Base_Guild = BaseGuild()

class QuotaCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_uri = None
        self.config = None
        self.cluster = None
        self.payment_db = None
        self.payment_config = None
        self.design_Db = None
        self.design_config = None
        self.design_records = None
        self.activity_channel_id = None
        self.load_config()
        self.send_weekly_leaderboard.start()
        

    def load_config(self):
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.payment_db = self.cluster[self.config["collections"]["payment"]["database"]]
        self.payment_config = self.payment_db[self.config["collections"]["payment"]["collection"]]
        self.design_Db = self.cluster[self.config["collections"]["design"]["database"]]
        self.design_config = self.design_Db[self.config["collections"]["design"]["config_collection"]]
        self.design_records = self.design_Db[self.config["collections"]["design"]["log_collection"]]


    @tasks.loop(seconds=15)
    async def send_weekly_leaderboard(self):
        now = datetime.utcnow() + timedelta(hours=0)
        
        if now.weekday() == 7 and now.hour == 6 and now.minute == 30:
            try:
                await self.send_leaderboard()
            except Exception as e:
                print(f"Error in send_leaderboard: {e}")

            channel = self.client.get_channel(1165730359888052304)
            await channel.send(content="Sent weekly activity report")
        
    async def send_leaderboard(self):
        for guild in self.client.guilds:
            try:
                await self.send_leaderboard_for_guild(guild)
            except Exception as e:
                print(f"Error sending leaderboard for guild {guild.name}: {e}")

    async def send_leaderboard_for_guild(self, guild):
        existing_record = await Base_Guild.fetch_design_config(guild.id)
        if not existing_record:
            return

        staff_role_id = existing_record.get("staff_role_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_role = guild.get_role(staff_role_id)
        designer_role = guild.get_role(designer_role_id)

        if not staff_role or not designer_role:
            return

        weekly_quota = existing_record.get("weekly_quota")

        if not weekly_quota:
            return

        guild_design_records_cursor = self.design_records.find({"guild_id": guild.id, "accounted_for": {"$ne": True}})
        guild_design_records = list(guild_design_records_cursor)
        designers = [member for member in guild.members if designer_role in member.roles]



        leaderboard_embed = discord.Embed(
            title=f"{guild.name} Weekly Leaderboard", color=discord.Color.light_embed(), description=f"**Quota Information for {guild.name}**"
        )
        leaderboard_embed.set_footer(text=f"Activity Module")

        update_operations = []
        for designer in designers:
            user_quota = sum(1 for record in guild_design_records if record["designer_id"] == designer.id)
            designs_to_mark = [record["order_id"] for record in guild_design_records if record["designer_id"] == designer.id]

            if user_quota >= weekly_quota:
                leaderboard_embed.description += f"\n\n**User:** {designer.mention}\n**Passed:** ``True``"
                update_operations.extend([
                    self.design_records.update_one({"order_id": design_id, "accounted_for": {"$ne": True}}, {"$set": {"accounted_for": True}}) for design_id in designs_to_mark
                ])
            else:
                designs_needed = weekly_quota - user_quota
                leaderboard_embed.description += f"\n\n**User:** {designer.mention}\n**Passed:** ``False``\n**Designs Left:** ``{designs_needed}``"

        if update_operations:
            try:
                result = await self.design_records.bulk_write(update_operations)
            except Exception as bulk_write_error:
                print(f"Error during bulk write: {bulk_write_error}")

        activity_channel_id = existing_record.get("activity_channel")
        activity_channel = self.client.get_channel(activity_channel_id)
        
        if activity_channel:
            await activity_channel.send(embed=leaderboard_embed)


    @commands.hybrid_group(name="activity", description=f"Activity based commands")
    async def quota(self, ctx):
        pass
    
    @quota.command(name="leaderboard", description="See who has and who hasn't passed their quota")
    async def leaderboard(self, ctx: commands.Context):
        guild = ctx.guild
        existing_record = await Base_Guild.fetch_design_config(guild.id)
        if not existing_record:
            return

        staff_role_id = existing_record.get("staff_role_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_role = guild.get_role(staff_role_id)
        designer_role = guild.get_role(designer_role_id)

        if not staff_role or not designer_role:
            return

        weekly_quota = existing_record.get("weekly_quota")

        if not weekly_quota:
            return

        guild_design_records_cursor = self.design_records.find({"guild_id": guild.id, "accounted_for": {"$ne": True}})
        guild_design_records = list(guild_design_records_cursor)
        designers = [member for member in guild.members if designer_role in member.roles]



        leaderboard_embed = discord.Embed(
            title=f"{guild.name} Leaderboard", color=discord.Color.light_embed(), description=f"**Quota Information for {guild.name}**"
        )
        leaderboard_embed.set_footer(text=f"Activity Module")

        for designer in designers:
            user_quota = sum(1 for record in guild_design_records if record["designer_id"] == designer.id)

            if user_quota >= weekly_quota:
                leaderboard_embed.description += f"\n\n**User:** {designer.mention}\n**Passed:** ``True``"
            else:
                designs_needed = weekly_quota - user_quota
                leaderboard_embed.description += f"\n\n**User:** {designer.mention}\n**Passed:** ``False``\n**Designs Left:** ``{designs_needed}``"

        await ctx.send(embed=leaderboard_embed)
        
    @quota.command(name=f"user", description=f"See if you have passed the quota")
    async def user(self, ctx: commands.Context, user: discord.Member=None):
        if user is None:
            user = ctx.author
        existing_record = await Base_Guild.fetch_design_config(ctx.guild.id)
        if not existing_record:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the design module.")

        staff_role_id = existing_record.get("staff_role_id")
        designer_role_id = existing_record.get("designer_role_id")
        staff_role = ctx.guild.get_role(staff_role_id)
        designer_role = self.client.get_guild(ctx.guild.id).get_role(designer_role_id)

        if staff_role not in ctx.author.roles:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you can't use this command.")

        weekly_quota = existing_record.get("weekly_quota")

        if not weekly_quota:
            return await ctx.send(f"<:shell_denied:1160456828451295232> **{ctx.author.name},** you need to set up the quota module.")

        guild_design_records_cursor = self.design_records.find({"guild_id": ctx.guild.id, "accounted_for": {"$ne": True}})
        guild_design_records = list(guild_design_records_cursor)
        
        quota_embed = discord.Embed(
            title=f"Quota Information for {user.display_name}", color=discord.Color.light_embed()
        )
        quota_embed.set_footer(text=f"Activity Module")
        quota_embed.set_author(icon_url=user.display_avatar.url, name=user.display_name)

        user_quota = sum(1 for record in guild_design_records if record["designer_id"] == user.id)

        if user_quota >= weekly_quota:
            quota_embed.description = f"\n\n**User:** {user.mention}\n**Passed:** ``True``"
        else:
            designs_needed = weekly_quota - user_quota
            quota_embed.description = f"\n\n**User:** {user.mention}\n**Passed:** ``False``\n**Designs Left:** ``{designs_needed}``"


        await ctx.send(embed=quota_embed)
        print("User command executed successfully.")
        
    @commands.command(name="manual_leaderboard", hidden=True)
    async def test_leaderboard(self, ctx: commands.Context):
        print("Executing test leaderboard command...")
        await self.send_leaderboard()
        await ctx.send("Test leaderboard sent.")
        print("Test leaderboard command executed successfully.")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(QuotaCog(client=client))

