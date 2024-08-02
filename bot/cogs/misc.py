import re
import config
import random
import discord
from discord.ext import commands

logger = config.get_logger(__name__)

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        logger.debug("Misc cog initialized")

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
            logger.info('replying to bad bot')
            emojis = [':broken_heart:', ':cry:', ':disappointed:', ':sob:']
            replies = ['I am trying my hardest!', 'Pain', 'Sorry', 'Wah']
            emoji = random.choice(emojis)
            reply = random.choice(replies)
            await message.reply('{} {}'.format(reply, emoji), mention_author=False)
        elif self.bot.user.mentioned_in(message):
            logger.info('replying to a bot mention')
            quotes = [
              "Every day is an opportunity disguised as a challenge. – Tiki Barber",
              "Leadership is a matter of having people look at you and gain confidence. If you're in control, they're in control. – Tom Landry",
              "Football is like life. It requires perseverance, self-denial, hard work, sacrifice, dedication, and respect for authority. – Vince Lombardi",
              "Success isn't owned, it's leased. And rent is due every day. – J.J. Watt",
              "The man on top of the mountain didn\'t fall there. – Vince Lombardi",
              "The most valuable player is the one who makes the most players valuable. – Peyton Manning",
              "You can’t win together if you don’t work together. – Nick Saban",
              "To the young: work, work, work, and then work some more. – Ed Reed",
              "Good things come to those who work! – Greg Dortch",
              "The only place success comes before work is in the dictionary. – Vince Lombardi",
              "It's not the will to win that matters. It's the will to prepare to win that matters. – Paul \"Bear\" Bryant",
              "You cannot make progress with excuses. – Cam Newton",
              "The difference between a successful person and others is not a lack of strength, not a lack of knowledge, but rather in a lack of will. - Vince Lombardi",
              "Remember, once you set a goal, it's all about how hard you're willing to work, how much you're willing to sacrifice and how badly you truly want it. – J.J. Watt",
              "Embrace the new, no matter how uncomfortable, and make it work for you. – Alex Smith",
              "Football is a game of controlled anger. It is a game of retribution. It’s about will. – Brian Dawkins",
              "Nobody who ever gave his best regretted it. – George S. Halas",
              "No one ever drowned in sweat. – Lou Holtz",
              "Winners never quit and quitters never win. – Vince Lombardi",
              "It's not the size of the dog in the fight, but the size in the fight of the dog. – Archie Griffin",
              "When you've got something to prove, there's nothing greater than a challenge. – Terry Bradshaw",
              "There is only one way to succeed in anything…and that is to give it everything. – Vince Lombardi",
              "If what you did yesterday seems big, you haven't done anything today. – Lou Holtz",
              "Effort will never be questioned. – Jalen Hurts",
              "If you work hard and you play well, all those critics quiet themselves pretty quickly. – Peyton Manning",
              "If you do the bare minimum, expect bare minimum results. You want to be great, work to be great. – J.J. Watt",
              "Winners, I am convinced, imagine their dreams first. They want it with all their heart and expect it to come true. There is, I believe, no other way to live. – Joe Montana",
              "When you lose, talk little. When you win, talk less. – Tom Brady",
              "Ability is what you're capable of doing. Motivation determines what you do. Attitude determines how well you do it. – Lou Holtz",
              "Self-praise is for losers. Be a winner. Stand for something. Always have class, and be humble. – John Madden",
              "You can learn a line from a win and a book from defeat. – Paul Brown",
              "When you're good at something, you'll tell everyone. When you're great at something, they'll tell you. - Walter Payton",
              "Winning isn’t getting ahead of others. It’s getting ahead of yourself. – Roger Staubach",
              "Do you want to know what my favorite part of the game is? The opportunity to play. – Mike Singletary",
              "Stay hungry, remain humble, and get better today. – Pete Carroll",
              "Trust that you can get back up and not give in. Ever. – Patrick Willis",
              "It's not whether you get knocked down, it's whether you get back up. – Vince Lombardi",
              "When you don't give up, you cannot fail. – Adrian Peterson",
              "I may win and I may lose, but I will never be defeated. – Emmitt Smith",
              "Set your goals high, and don't stop till you get there. – Bo Jackson",
              "To do things you've never done before, you have to do things you've never done before. – Sean Payton",
              "When you're good at something, you'll tell everyone. When you're great at something, they'll tell you. - Walter Payton",
              "A champion is simply someone who did not give up when they wanted to. - Tom Landry",
              "When you don’t give up, you cannot fail. – Adrian Peterson",
              "Life is ten percent what happens to you and ninety percent how you respond to it. – Lou Holtz",
              "Maybe. Maybe not. Maybe fuck yourself. - Sergeant Dignam",
              "Well I like school... and I like football... and I’m gonna keep doin’ ’em both because they make me feel good. – Bobby Boucher",
              "Talent sets the floor, character sets the ceiling - Bill Belichick",
              "When you get wet, it usually means something good. - Bill Belichick"
            ]
            quote = random.choice(quotes)
            logger.debug('replying with quote: {}'.format(quote))
            await message.reply('>>> *{}*'.format(quote), mention_author=False)

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
