import os

import logging


from discord.ext import commands
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo
from datastore import GuildsDatastore
from config import settings

logger = logging.getLogger('commish_bot.py')
logger.setLevel(settings.loglevel)

bot = commands.Bot(command_prefix='$', description='')
bot.remove_command('help')

@bot.event
async def on_ready():
    logger.info('CommishBot is ready')

@bot.event
async def on_guild_join(guild):
    logger.info('Joined {}'.format(guild.name))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        logger.info('CommandNotFound: {}'.format(error))
        content = "Sorry, I don't understand that command. Type `$help` to see a list of valid commands." 
        await ctx.send(content=content)

bot.add_cog(Meta(bot))


guilds = GuildsDatastore(settings.guilds_datastore_loc)

bot.add_cog(Yahoo(bot, settings.yahoo_key, settings.yahoo_secret, guilds))
bot.add_cog(Misc(bot))

bot.run(settings.discord_token, bot=True, reconnect=True)
