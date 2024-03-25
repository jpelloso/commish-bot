import config
import sleeper_api
from discord.ext import commands

logger = config.get_logger(__name__)

class Sleeper(commands.Cog):

    error_message = "I'm having trouble getting that right now, please try again later"

    def __init__(self, bot):
        self.bot = bot
        self.sleeper_api = sleeper_api.Sleeper()
        self.generate_player_list()
        self.generate_draft_results()
        logger.debug("Sleeper cog initialized")

    def generate_player_list(self):
        # Please use this call sparingly, as it is intended only to be used once per day 
        # at most to keep your player IDs updated. The average size of this query is 5MB. 
        logger.info('generate player list')
        self.sleeper_api.get_player_list()

    def generate_draft_results(self):
        logger.info('generate draft results')
        self.sleeper_api.get_draft_results()

    @commands.command('regenerate_player_list')
    async def regenerate_player_list(self, ctx):
        logger.info('regenerate_player_list called')
        self.sleeper_api.get_player_list()

    @commands.command('settings')
    async def settings(self, ctx):
        logger.info('settings called')
        msg, embed = self.sleeper_api.get_settings()
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('history')
    async def history(self, ctx):
        logger.info('history called')
        msg = self.sleeper_api.get_history()
        if msg:
            await ctx.send(content=msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('keeper')
    async def keeper(self, ctx, *, content:str):
        logger.info('keeper called')
        msg = self.sleeper_api.get_keeper_value(content)
        if msg:
            await ctx.send(content=msg)
        else:
            await ctx.send(self.error_message)

