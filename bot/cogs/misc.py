import re
import config
import random
import discord
from discord.ext import commands

logger = config.get_logger(__name__)

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message.content.lower()
        if 'good bot' in msg:
            logger.info('replying to good bot')
            emojis = [':grin:', ':heart:', ':slight_smile:', ':smile:']
            replies = ['Anytime', 'Appreciate you', 'Thanks', 'You got it']
            emoji = random.choice(emojis)
            reply = random.choice(replies)
            await message.reply('{} {}'.format(reply, emoji), mention_author=False)
        elif 'bad bot' in msg:
            logger.info('repling to bad bot')
            emojis = [':broken_heart:', ':cry:', ':disappointed:', ':sob:']
            replies = ['I am trying my hardest!', 'Pain', 'Sorry', 'Wah']
            emoji = random.choice(emojis)
            reply = random.choice(replies)
            await message.reply('{} {}'.format(reply, emoji), mention_author=False)
        elif 'fire pelloso' in msg:
            logger.info('repling to fire pelloso')
            await message.reply("C'mon now, I think Commissioner Pelloso is doing a fine job, calm down.", mention_author=False)
        elif 'pjs' in msg or 'pj\'s' in msg:
            logger.info('replying to PJs')
            await message.reply("Did somebody say PJ's!? Don't worry, I have directions. \
                https://www.google.com/maps/place/PJ's/@42.0548294,-72.1629024,17z/data=!4m5!3m4!1s0x89e697eb3bdb3bc9:0xd902df67e14be1f2!8m2!3d42.0548294!4d-72.1607137")

    @commands.command('poll')
    async def poll(self, ctx, *, content:str):
        logger.info('poll called')
        dev_channel = 991893190221234176
        polls_channel = 1009118603322335272
        if ctx.channel.id == dev_channel or ctx.channel.id == polls_channel:
            author = re.sub('\#[0-9]+', '', str(ctx.message.author))
            title = '{} created a poll'.format(author)
            vote = 'Click the :white_check_mark: or :x: reaction below to cast your vote!'
            description = '{}\n\n{}'.format(content, vote)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            await ctx.message.delete()
            msg = await ctx.send(embed=embed)
            yes_emoji = '✅'
            no_emoji = '❌'
            await msg.add_reaction(yes_emoji)
            await msg.add_reaction(no_emoji)
        else:
            msg = 'Sorry, but you are only allowed to create polls in the <#1009118603322335272> channel.'
            await ctx.send(content=msg)
