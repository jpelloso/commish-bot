import os
import config
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo
from discord.ext import commands

logger = config.get_logger(__name__)

bot = commands.Bot(command_prefix='$', description='')
bot.remove_command('help')

@bot.event
async def on_ready():
    bot.add_cog(Meta(bot))
    bot.add_cog(Misc(bot))
    bot.add_cog(Yahoo(bot, os.environ['YAHOO_KEY'], os.environ['YAHOO_SECRET']))
    logger.info('Bot is ready')

@bot.event
async def on_guild_join(guild):
    logger.info('Joined {}'.format(guild.name))

bot.run(os.environ['DISCORD_TOKEN'], bot=True, reconnect=True)
