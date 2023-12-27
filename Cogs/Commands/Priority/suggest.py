from discord.ext import commands
import discord
from discord.ui import View, button
import random
from pymongo import MongoClient
from Util.Yaml import Load_yaml
from DataModels.guild import BaseGuild
from DataModels.user import BaseUser

Base_User = BaseUser()
Base_Guild = BaseGuild()


class SuggestionButtons(View):
    def __init__(self, client: commands.Bot):
        super().__init__(timeout=None)
        self.client = client
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.suggestions_db = self.cluster[self.config["collections"]["suggestion"]["database"]]
        self.suggestions_logs = self.suggestions_db[self.config["collections"]["suggestion"]["logs"]]

    async def update_embed(self, interaction: discord.Interaction):
        suggestion_data = self.suggestions_logs.find_one({"message_id": interaction.message.id})
        if not suggestion_data:
            return await interaction.followup.send(content=f"I can't find that suggestion.", ephemeral=True)
        if suggestion_data:
            embed = discord.Embed.from_dict(interaction.message.embeds[0].to_dict())
            embed.description = f"{suggestion_data['suggestion']}\n\n{len(suggestion_data['voters'])} Upvotes | {suggestion_data['downvotes']} Downvotes"
            await interaction.message.edit(embed=embed)

    async def handle_vote(self, interaction: discord.Interaction, vote_type):
        await interaction.response.defer()
        suggestion_data = self.suggestions_logs.find_one({"message_id": interaction.message.id})
        if not suggestion_data:
            return await interaction.followup.send(content=f"I can't find that suggestion.", ephemeral=True)
        if suggestion_data:
            user_id = interaction.user.id
            voters = suggestion_data.get("voters", [])
            user_vote = next((voter for voter in voters if voter["user_id"] == user_id), None)

            suggestion_data.setdefault("upvotes", 0)
            suggestion_data.setdefault("downvotes", 0)

            if user_vote:
                suggestion_data[vote_type + "s"] -= 1
                suggestion_data["voters"].remove(user_vote)
                await self.update_embed(interaction)
            else:
                suggestion_data[vote_type + "s"] += 1
                suggestion_data["voters"].append({"user_id": user_id, "vote_type": vote_type})
                await self.update_embed(interaction)
        else:
            await interaction.followup.send("Suggestion not found.", ephemeral=True)

    async def list_votes(self, interaction: discord.Interaction):
        await interaction.response.defer()
        suggestion_data = self.suggestions_logs.find_one({"message_id": interaction.message.id})
        if not suggestion_data:
            return await interaction.followup.send(content=f"I can't find that suggestion.", ephemeral=True)
        voters = suggestion_data.get("voters", [])
        vote_list = "\n".join([f"<@!{voter['user_id']}> - {voter['vote_type']}" for voter in voters])
        embed = discord.Embed(title=f"Voters", description=vote_list, color=discord.Color.dark_embed())
        await interaction.followup.send(embed=embed, ephemeral=True)

    @button(label='Upvote', style=discord.ButtonStyle.green, custom_id='persistent_view:upvote', emoji='⬆️')
    async def upvote(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_vote(interaction, "upvote")

    @button(label='Downvote', style=discord.ButtonStyle.red, custom_id='persistent_view:downvote', emoji='⬇️')
    async def downvote(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_vote(interaction, "downvote")

    @button(label='List Votes', style=discord.ButtonStyle.gray, custom_id='persistent_view:listvotes', emoji='📜')
    async def list_votes_button(self, interaction: discord.Interaction, button: discord.Button):
        await self.list_votes(interaction)


class SuggestionCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = Load_yaml()
        self.mongo_uri = self.config["mongodb"]["uri"]
        self.cluster = MongoClient(self.mongo_uri)
        self.suggestions_db = self.cluster[self.config["collections"]["suggestion"]["database"]]
        self.suggestions_logs = self.suggestions_db[self.config["collections"]["suggestion"]["logs"]]

    @commands.hybrid_group(name="suggestion", description=f"Suggestion based commands")
    async def suggestion(self, ctx):
        pass

    @suggestion.command(name=f"create", description=f"Create a suggestion")
    async def createsuggest(self, ctx: commands.Context, *, suggestion: str):
        message = await ctx.send(content=f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** processing your request.")
        embed = discord.Embed(
            title=f"Suggested by {ctx.author.display_name}", description=f"{suggestion}\n\n0 Upvotes | 0 Downvotes",
            color=discord.Color.light_embed())
        feedback_channel_id = await Base_Guild.get_suggestion_channel(guild_id=ctx.guild.id)
        if feedback_channel_id is None:
            return await message.edit(
                content=f"<:shell_denied:1160456828451295232> **{ctx.author.name},** the suggestion module has been incorrectly configured.")

        await message.edit(content=f"<:Approved:1163094275572121661> **{ctx.author.display_name},** successfully sent your suggestion!")

        feedback_channel = ctx.guild.get_channel(feedback_channel_id)
        suggestion_data = {
            "guild_id": ctx.guild.id, "message_id": None, "suggestion": suggestion, "upvotes": 0, "downvotes": 0,
            "voters": [], "poster": ctx.author.id
        }
        message2 = await feedback_channel.send(embed=embed,
                                              content=f"<:Approved:1163094275572121661> **{ctx.author.mention},** thank you for your suggestion!",
                                              view=SuggestionButtons(client=self.client))
        suggestion_data["message_id"] = message2.id
        self.suggestions_logs.insert_one(suggestion_data)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(SuggestionCog(client))