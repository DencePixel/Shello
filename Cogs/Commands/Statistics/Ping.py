import discord
from discord.ext import commands
import datetime

class PingCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.hybrid_command(name='latency', description=f"Get the bot's latency")
    async def latency(self, ctx: commands.Context):
        message = await ctx.send(f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** calculating latency")

        await message.edit(content=f'<:Approved:1163094275572121661> **{ctx.author.display_name},** my ping is **{round(self.bot.latency * 1000)}ms**')

async def setup(bot):
    await bot.add_cog(PingCog(bot))
