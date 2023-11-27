import discord
from discord.ext import commands
import datetime

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='latency', description=f"Get the bot's latency")
    async def latency(self, ctx):
        start_time = datetime.datetime.now()
        message = await ctx.send(f"<a:Loading:1177637653382959184> **{ctx.author.display_name},** calculating latency")
        end_time = datetime.datetime.now()
        latency = (end_time - start_time).microseconds / 1000
        latency.__round__()

        await message.edit(content=f'<:Approved:1163094275572121661> **{ctx.author.display_name},** my ping is **{latency}ms**')

async def setup(bot):
    await bot.add_cog(PingCog(bot))
