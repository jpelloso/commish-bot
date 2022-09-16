import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Meta(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            logger.error('CommandNotFound: {}'.format(error))
            content = "Sorry, I don't understand that command. Type `$help` to see a list of valid commands."
            await ctx.send(content=content)

    @commands.command('help')
    async def help(self, ctx):
        logger.info('help called')
        title = 'CommishBot Help'
        description = 'A Yahoo Fantasy Sports Bot for Discord'
        embed = discord.Embed(title=title, description=description, color=0xeee657)
        embed.add_field(name='`$ping`', value='Return the latency of the bot', inline=False)
        embed.add_field(name='`$standings`', value='Return the standings of the current season', inline=False)
        embed.add_field(name='`$history [year]`', value='Return the standings from a specific season', inline=False)
        embed.add_field(name='`$hall_of_fame`', value='Return a list of champions from every year', inline=False)
        embed.add_field(name='`$hall_of_shame`', value='Return a list of losers from every year', inline=False)
        embed.add_field(name='`$matchups`', value='Return the matchups for the current gameweek', inline=False)
        embed.add_field(name='`$roster [team]`', value='Return the roster of a specific team', inline=False)
        embed.add_field(name='`$faab [team]`', value='Return the FAAB balance of a specific team', inline=False)
        embed.add_field(name='`$manager [team]`', value='Return the manager nickname of a specific team', inline=False)
        embed.add_field(name='`$waiver [team]`', value='Return the waiver position of a specific team', inline=False)
        embed.add_field(name='`$player_details [player]`', value='Return the details of a specific player', inline=False)
        embed.add_field(name='`$keeper [player]`', value='Return the round drafted of a specific player', inline=False)
        embed.add_field(name='`$trade_deadline`', value='Return the last possible day for trades to be processed', inline=False)
        embed.add_field(name='`$playoffs`', value='Return details about the playoffs for the current season', inline=False)
        embed.add_field(name='`$poll [prompt]`', value='Create a poll for the league to vote on', inline=False)
        await ctx.send(embed=embed)

    @commands.command('ping')
    async def ping(self, ctx):
        logger.info('ping called')
        # Included in the Discord.py library
        latency = self.bot.latency
        await ctx.send(latency)
