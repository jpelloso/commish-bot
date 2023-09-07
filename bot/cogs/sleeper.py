import config
import sleeper_api
from discord.ext import commands

logger = config.get_logger(__name__)

class Sleeper(commands.Cog):

    error_message = "I'm having trouble getting that right now, please try again later"

    def __init__(self, bot):
        self.bot = bot
        self.sleeper_api = sleeper_api.Sleeper()
        logger.debug("Sleeper cog initialized")

    @commands.command('standings')
    async def standings(self, ctx):
        logger.info('standings called')
        msg = self.sleeper_api.get_standings()
        if msg:
            await ctx.send(content=msg)
        else:
            await ctx.send(self.error_message)
