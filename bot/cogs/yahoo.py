import os
import config
import logging
import urllib3
import yahoo_api
from discord.ext import commands
from yahoo_oauth import OAuth2

logger = config.get_logger(__name__)

oauth_logger = logging.getLogger('yahoo_oauth')
oauth_logger.disabled = True

class Yahoo(commands.Cog):

    error_message = "I'm having trouble getting that right now, please try again later"

    def __init__(self, bot, KEY, SECRET):
        self.bot = bot
        self.http = urllib3.PoolManager()
        self.KEY = KEY
        self.SECRET = SECRET
        self.yahoo_api = self.refresh_oauth()
        self.generate_draft_results()

    async def cog_before_invoke(self, ctx):
        self.yahoo_api = self.refresh_oauth()
        return

    def refresh_oauth(self):
        oauth = yahoo_api.Yahoo(OAuth2(self.KEY, self.SECRET, store_file=False, **config.get_yahoo_oauth()), 
            os.environ['YAHOO_LEAGUE_ID'], os.environ['YAHOO_LEAGUE_TYPE'])
        return oauth

    def generate_draft_results(self):
        # Since dynos restart every 24 hours with Heroku,
        # regenerate the draft results file when the yahoo 
        # cog is added to bot (on bot init/restart)
        logger.info('generate draft results')
        self.yahoo_api.get_draft_results()

    @commands.command('standings')
    async def standings(self, ctx):
        logger.info('standings called')
        embed = self.yahoo_api.get_standings()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('history')
    async def history(self, ctx, *, content:int):
        logger.info('history called')
        msg, embed = self.yahoo_api.get_history(content)
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('matchups')
    async def matchups(self, ctx):
        logger.info('matchups called')
        embed = self.yahoo_api.get_matchups()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('roster')
    async def roster(self, ctx, *, content:str):
        logger.info('roster called')
        msg, embed = self.yahoo_api.get_roster(content)
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('player_details')
    async def player_details(self, ctx,  *, content:str):
        logger.info('player_details called')
        msg, embed = self.yahoo_api.get_player_details(content)
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('keeper')
    async def keeper(self, ctx,  *, content:str):
        logger.info('keeper called')
        msg = self.yahoo_api.get_keeper_value(content)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('playoffs')
    async def playoffs(self, ctx):
        logger.info('playoffs called')
        msg = self.yahoo_api.get_playoffs_details()
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('trade_deadline')
    async def trade_deadline(self, ctx):
        logger.info('trade_deadline called')
        msg = self.yahoo_api.get_trade_deadline()
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('waiver')
    async def waiver(self, ctx, *, content:str):
        logger.info('waiver called')
        msg = self.yahoo_api.get_waiver_priority(content)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('faab')
    async def faab(self, ctx, *, content:str):
        logger.info('faab called')
        msg = self.yahoo_api.get_faab_balance(content)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('manager')
    async def manager(self, ctx, *, content:str):
        logger.info('manager called')
        msg = self.yahoo_api.get_manager(content)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)
