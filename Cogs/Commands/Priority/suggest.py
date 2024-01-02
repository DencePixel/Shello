from discord.ext import commands
import discord
from discord.ui import View, button
import random
import motor.motor_asyncio
from Util.Yaml import Load_yaml
from Cogs.emojis import approved_emoji, denied_emoji, right_Emoji, space_emoji
from DataModels.guild import BaseGuild
from DataModels.user import BaseUser
from Util.views import YesNoMenu, CustomDropdown

Base_User = BaseUser()
Base_Guild = BaseGuild()

class SuggestionCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        self.suggestions_db = self.cluster[self.config["collections"]["suggestion"]["database"]]
        self.suggestions_logs = self.suggestions_db[self.config["collections"]["suggestion"]["logs"]]

    @commands.hybrid_group(name="suggestion", description=f"Suggestion based commands")
    async def suggestion(self, ctx):
        pass

    @suggestion.command(name=f"create", description=f"Create a suggestion")
    async def createsuggest(self, ctx: commands.Context, *, suggestion: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** I am processing your request.")
        embed = discord.Embed(
            title=f"Suggested by {ctx.author.display_name}", description=f"{suggestion}",
            color=discord.Color.light_embed())
        feedback_channel_id = await Base_Guild.get_suggestion_channel(guild_id=ctx.guild.id)
        if feedback_channel_id is None:
            return await message.edit(
                content=f"{denied_emoji} **{ctx.author.name},** the suggestion module has been incorrectly configured.")

        await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** successfully sent your suggestion!")

        feedback_channel = ctx.guild.get_channel(feedback_channel_id)
        suggestion_data = {
            "guild_id": ctx.guild.id, "message_id": None, "suggestion": suggestion,  "poster": ctx.author.id}
        message2 = await feedback_channel.send(embed=embed,
                                              content=f"<:Approved:1163094275572121661> **{ctx.author.mention},** thank you for your suggestion!")
        await message2.add_reaction("<:Approved:1163094275572121661>")
        await message2.add_reaction("<:Denied:1163095002969276456>")
        suggestion_data["message_id"] = message2.id
        await self.suggestions_logs.insert_one(suggestion_data)
        
    @suggestion.command(name=f"find", description=f"Find a suggestion")
    async def findsuggest(self, ctx: commands.Context, message_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** I am processing your request.")
        record = await self.suggestions_logs.find_one({"message_id": message_id})
        if not record:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** I can't find that suggestion.")
        author_id = record.get("poster")
        author = self.client.get_user(author_id)
        if not author:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** the poster is not in my cache.")
        suggestion = record.get("suggestion")
        embed = discord.Embed(title=f"{author.display_name}'s suggestion", description=f"<:suggestion:1181708198521090189> **Suggestion Information:**\n{space_emoji}{right_Emoji} **Suggestion:** ``{suggestion}``\n{space_emoji}{right_Emoji} **Message ID:** ``{message_id}``\n\n<:Badge:1163094257238806638> **Poster Information:**\n{space_emoji}{right_Emoji} **Poster:** {author.mention}\n{space_emoji}{right_Emoji} **Poster ID:** ``{author.id}``", color=discord.Color.light_embed())
        embed.set_thumbnail(url=author.display_avatar.url)
        return await message.edit(content=f"{approved_emoji} **{ctx.author.display_name},** here is the requested suggestion.", embed=embed)
    
    @suggestion.command(name=f"revoke", description=f"Revoke a suggestion")
    async def revokmesuggest(self, ctx: commands.Context, message_id: int):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** please wait while your request is processed.")
        existing_record = await Base_Guild.fetch_design_config(guild_id=ctx.guild.id)
        if not existing_record:
            return await message.edit(content=f"<:Denied:1163095002969276456> **{ctx.author.name},** you need to set up the design module.")

        staff_role_id = existing_record.get("staff_role_id")
        staff_role = ctx.guild.get_role(staff_role_id)

        if not staff_role:
            return await message.edit(content=f"<:Denied:1163095002969276456> Staff role not found. Please check your configuration.")
        
        if staff_role not in ctx.author.roles:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you can't use this.")
        
        find = await self.suggestions_logs.find_one({"guild_id": ctx.guild.id, "message_id": message_id})
        if not find:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** I can't find that suggestion.")
        
        menu = YesNoMenu(ctx.author.id)
        await message.edit(content=f"{right_Emoji} **{ctx.author.display_name},** do you want to continue?")
        await menu.wait()
        if menu.value is None:
            return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** you didn't select a option.", view=None)
        choice = "yes" if menu.value else "no"
        if choice == "yes":
            deletion = await self.suggestions_logs.delete_one({"guild_id": ctx.guild.id, "message_id": message_id})
            if not deletion:
                return await message.edit(content=f"{denied_emoji} **{ctx.author.display_name},** something went wrong.")
            return await message.edit(
                content=f"{approved_emoji} **{ctx.author.display_name},** I have succesfully revoked that suggestion."
            )
        
        if choice == "no":
            return await message.edit(
                content=f"{approved_emoji} **{ctx.author.display_name},** I have canceled this operation."
            )
            
   


async def setup(client: commands.Bot) -> None:
    await client.add_cog(SuggestionCog(client))