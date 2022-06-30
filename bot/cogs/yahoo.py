import os
import logging
import urllib3
import discord
import yahoo_api
from discord.ext import commands
from yahoo_oauth import OAuth2

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)


# TODO: 
#   quotation mark consistency
#   string consistency
#   imports orders
#   error messages (PLayer not found etc.)
#   exceptions
# Smart-Ass Bot -> Array of replies, use random int to get reply
#  Directions to PJs

def oauth(func):
    async def setup(cog, ctx, *, content=None):
        league_details = cog.guilds.getGuildDetails(ctx.guild.id)
        cog.yahoo_api = yahoo_api.Yahoo(OAuth2(cog.KEY, cog.SECRET, **league_details), league_details["league_id"], league_details["league_type"])
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
        embed = self.yahoo_api.get_roster(content)
        if embed:
            await ctx.send(embed=embed)
        else:
            emsg = "Sorry, I couldn't find a team with name '_{}_'. This command is case-sensitive. Please make sure you have the team name spelled correctly and try again.".format(content)
            await ctx.send(emsg)
        
    @commands.command('player_details')
    @oauth
    async def player_details(self, ctx,  *, content:str):
        logger.info('player_details called')
        embed = self.yahoo_api.get_player_details(content)
        if embed:
            await ctx.send(embed=embed)
        else:
            emsg = "Sorry, I couldn't find a player with name '_{}_'. This command is case-sensitive. Please make sure you have the player name spelled correctly and try again.".format(content)
            await ctx.send(emsg)

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

    @commands.command('trade')
    @oauth
    async def trade(self, ctx):
        logger.info('trade called')
        latest_trade = self.yahoo_api.get_latest_trade()

        if latest_trade == None:
            await ctx.send("No trades up for approval at this time")
            return

        teams = self.yahoo_api.league().teams()

        trader = teams[latest_trade['trader_team_key']]
        tradee = teams[latest_trade['tradee_team_key']]
        managers = [trader['name'], tradee['name']]
        
        player_set0 = []
        player_set0_details = ""
        for player in latest_trade['trader_players']:
            player_set0.append(player['name'])
            api_details = self.yahoo_api.get_player_details(player['name'])["text"]+"\n"
            if api_details: 
                player_set0_details = player_set0_details + api_details
            else:
                await ctx.send(self.error_message)
                return

        player_set1 = []
        player_set1_details = ""
        for player in latest_trade['tradee_players']:
            player_set1.append(player['name'])
            api_details = self.yahoo_api.get_player_details(player['name'])["text"]+"\n"
            if api_details: 
                player_set1_details = player_set1_details + api_details
            else:
                await ctx.send(self.error_message)
                return

            confirm_trade_message = "{} sends {} to {} for {}".format(managers[0],', '.join(player_set0),managers[1],', '.join(player_set1))
            announcement = "There's collusion afoot!\n"
            embed = discord.Embed(title="The following trade is up for approval:", description=confirm_trade_message, color=0xeee657)
            embed.add_field(name="{} sends:".format(managers[0]), value=player_set0_details, inline=False)
            embed.add_field(name="to {} for:".format(managers[1]), value=player_set1_details, inline=False)
            embed.add_field(name="Voting", value=" Click :white_check_mark: for yes, :no_entry_sign: for no")
            msg = await ctx.send(content=announcement, embed=embed)    
            yes_emoji = '\U00002705'
            no_emoji = '\U0001F6AB'        
            await msg.add_reaction(yes_emoji)
            await msg.add_reaction(no_emoji)
