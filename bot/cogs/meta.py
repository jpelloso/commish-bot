import config
import discord
from discord.ext import commands

logger = config.get_logger(__name__)

class Meta(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        logger.debug("Meta cog initialized")

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
        description = 'A Sleeper Fantasy Sports Bot for Discord'
        embed = discord.Embed(title=title, description=description, color=0xeee657)
        embed.add_field(name='`$ping`', value='Return the latency of the bot', inline=False)
        embed.add_field(name='`$settings`', value='Return the settings for the league', inline=False)
        embed.add_field(name='`$history`', value='Return the league history', inline=False)
        embed.add_field(name='`$keeper [player]`', value='Return the round drafted of a specific player', inline=False)
        embed.add_field(name='`$poll [prompt]`', value='Create a poll for the league to vote on', inline=False)
        embed.add_field(name='`$regenerate_player_list`', value='Regenerate player list used for player lookups', inline=False)
        await ctx.send(embed=embed)

    @commands.command('ping')
    async def ping(self, ctx):
        logger.info('ping called')
        # Included in the Discord.py library
        latency = self.bot.latency
        await ctx.send(latency)
