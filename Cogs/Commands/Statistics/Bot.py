import discord
from discord.ext import commands
import datetime

class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='info', description=f"Get the bot's info")
    async def info(self, ctx):
        return
        
async def setup(bot):
    await bot.add_cog(BotCog(bot))
