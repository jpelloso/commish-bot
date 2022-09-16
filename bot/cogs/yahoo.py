import os
import logging
import urllib3
import yahoo_api
from discord.ext import commands
from yahoo_oauth import OAuth2

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)

def oauth(func):
    async def setup(cog, ctx, *, content=None):
        league_details = cog.guilds.getGuildDetails(ctx.guild.id)
        cog.yahoo_api = yahoo_api.Yahoo(OAuth2(cog.KEY, cog.SECRET, **league_details), league_details['league_id'], league_details['league_type'])
        if content:
            await func(cog, ctx, content=content)
        else:
            await func(cog, ctx)
    return setup

class Yahoo(commands.Cog):

    error_message = "I'm having trouble getting that right now, please try again later"

    def __init__(self, bot, KEY, SECRET, guilds):
        self.bot = bot
        self.http = urllib3.PoolManager()
        self.KEY = KEY
        self.SECRET = SECRET
        self.guilds = guilds
        self.yahoo_api = None

    @commands.command('standings')
    @oauth
    async def standings(self, ctx):
        logger.info('standings called')
        embed = self.yahoo_api.get_standings()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('history')
    @oauth
    async def history(self, ctx, *, content:int):
        logger.info('history called')
        msg, embed = self.yahoo_api.get_history(content)
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('hall_of_fame')
    @oauth
    async def hall_of_fame(self, ctx):
        logger.info('hall_of_fame called')
        embed = self.yahoo_api.get_hall_of_fame()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('hall_of_shame')
    @oauth
    async def hall_of_shame(self, ctx):
        logger.info('hall_of_shame called')
        embed = self.yahoo_api.get_hall_of_shame()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('matchups')
    @oauth
    async def matchups(self, ctx):
        logger.info('matchups called')
        embed = self.yahoo_api.get_matchups()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('roster')
    @oauth
    async def roster(self, ctx, *, content:str):
        logger.info('roster called')
        msg, embed = self.yahoo_api.get_roster(content)
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('player_details')
    @oauth
    async def player_details(self, ctx,  *, content:str):
        logger.info('player_details called')
        msg, embed = self.yahoo_api.get_player_details(content)
        if msg or embed:
            await ctx.send(content=msg, embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command('keeper')
    @oauth
    async def keeper(self, ctx,  *, content:str):
        logger.info('keeper called')
        msg = self.yahoo_api.get_keeper_value(content)
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('playoffs')
    @oauth
    async def playoffs(self, ctx):
        logger.info('playoffs called')
        msg = self.yahoo_api.get_playoffs_details()
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('trade_deadline')
    @oauth
    async def trade_deadline(self, ctx):
        logger.info('trade_deadline called')
        msg = self.yahoo_api.get_trade_deadline()
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)

    @commands.command('waiver_priority')
    @oauth
    async def trade_deadline(self, ctx):
        logger.info('waiver called')
        msg = self.yahoo_api.get_waiver_priority()
        if msg:
            await ctx.send(msg)
        else:
            await ctx.send(self.error_message)