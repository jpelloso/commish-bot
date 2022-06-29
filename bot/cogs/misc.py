import logging
from discord.ext import commands

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Misc(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command('praise')
    async def praise(self, ctx, *args):
        logger.info('praise called')
        content = 'Wow, I think JP is doing a great job as commissioner! Keep up the good work boss!'
        await ctx.send(content=content)
