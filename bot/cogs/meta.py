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
        embed.add_field(name='`$poll [prompt]`', value='Create a poll for the league to vote on', inline=False)
        await ctx.send(embed=embed)

    @commands.command('ping')
    async def ping(self, ctx):
        logger.info('ping called')
        # Included in the Discord.py library
        latency = self.bot.latency
        await ctx.send(latency)

    @commands.command('poll')
    async def poll(self, ctx, *, content:str):
        logger.info('poll called')
        dev_channel = 991893190221234176
        polls_channel = 1009118603322335272
        if ctx.channel.id == dev_channel or ctx.channel.id == polls_channel:
            author = re.sub('\#[0-9]+', '', str(ctx.message.author))
            title = '{} created a poll'.format(author)
            vote = 'Click the ✅ or ❌ reaction below to cast your vote!'
            embed = discord.Embed(title=title, description=content, color=0xeee657)
            embed.set_footer(text=vote)
            await ctx.message.delete()
            msg = await ctx.send(embed=embed)
            yes_emoji = '✅'
            no_emoji = '❌'
            await msg.add_reaction(yes_emoji)
            await msg.add_reaction(no_emoji)
        else:
            msg = 'Sorry, but you are only allowed to create polls in the <#1009118603322335272> channel.'
            await ctx.send(content=msg)
