import logging
import random
import discord
from discord.ext import commands
from cachetools import cached, TTLCache

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message.content.lower()
        if 'good bot' in msg:
            emojis = [':grin:', ':heart:', ':slight_smile:', ':smile:']
            replies = ['Anytime', 'Appreciate you', 'Thanks', 'You got it']
            emoji = random.choice(emojis)
            reply = random.choice(replies)
            await message.reply('{} {}'.format(reply, emoji), mention_author=False)
        elif 'bad bot' in msg:
            emojis = [':broken_heart:', ':cry:', ':disappointed:', ':sob:']
            replies = ['I am trying my hardest!', 'Pain', 'Sorry', 'Wah']
            emoji = random.choice(emojis)
            reply = random.choice(replies)
            await message.reply('{} {}'.format(reply, emoji), mention_author=False)
        elif 'fire pelloso' in msg:
            await message.reply("C'mon now, I think Commissioner Pelloso is doing a fine job, calm down.", mention_author=False)
        elif 'when is' in msg or 'when do' in msg or 'what is' in msg or 'what are' in msg:
            await message.reply("Hey looks like you're maybe asking a question! Have you checked out the <#988308336384557147> and <#988303200551596122> channels for your answer? If your answer cannot be found there, try typing `$help` to see if I can help you find what you need.")

    @commands.command('chirp')
    async def chirp(self, ctx, *, content:str):
        logger.info('chirp called')
        chirps = [
            "I took your mother out for a steak dinner. I didn't call her back the next day, but I did tell her she raised a horrible fantasy football player.",
            "I was going to create a website for his team, but he couldn't string 3 w's together.",
            "You're only in the league because we haven't found a replacement yet.",
            "Good to see that your fantasy success perfectly contrasts your lack of personal success.",
            "Your league fee is more valuable than you.",
            "The beating you're going to get is gonna bring back some childhood memories.",
            "I don't hate you because you're fat. You're fat because I hate you",
            "Scoreboard.",
            "I just looked at your roster and threwup in my mouth.",
            "Don't worry, I have directions. \
            https://www.google.com/maps/place/PJ's/@42.0548294,-72.1629024,17z/data=!4m5!3m4!1s0x89e697eb3bdb3bc9:0xd902df67e14be1f2!8m2!3d42.0548294!4d-72.1607137"
        ]
        chirp = random.choice(chirps)
        await ctx.send(content=chirp)

    @commands.command('praise')
    async def praise(self, ctx):
        logger.info('praise called')
        content = 'Wow, I think JP is doing a great job as commissioner! Keep up the good work boss!'
        await ctx.send(content=content)

    @commands.command('poll')
    async def poll(self, ctx, *, content:str):
        logger.info('poll called')
        if ctx.channel.id == 1009118603322335272:
            creator = ctx.message.author.mention
            title = '{} created a poll'.format(creator)
            embed = discord.Embed(title=title, description=content, color=0xeee657)
            msg = await ctx.send(embed=embed)
            yes_emoji = '\U00002705'
            no_emoji = '\U0001F6AB'
            await msg.add_reaction(yes_emoji)
            await msg.add_reaction(no_emoji)
        else:
            msg = 'Sorry, but you are only allowed to create polls in the <#1009118603322335272> channel.'
            await ctx.send(content=msg)
