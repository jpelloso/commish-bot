import re
import config
import discord
from discord.ext import commands

logger = config.get_logger(__name__)

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        logger.debug("Misc cog initialized")

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
