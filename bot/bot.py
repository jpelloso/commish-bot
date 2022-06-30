import os
import logging
from discord.ext import commands
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo
from config import settings
from datastore import GuildsDatastore

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(settings.log_level)

bot = commands.Bot(command_prefix='$', description='')
bot.remove_command('help')

@bot.event
async def on_ready():
    logger.info('Bot is ready')

@bot.event
async def on_guild_join(guild):
    logger.info('Joined {}'.format(guild.name))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        logger.error('CommandNotFound: {}'.format(error))
        content = "Sorry, I don't understand that command. Type `$help` to see a list of valid commands." 
        await ctx.send(content=content)

guilds = GuildsDatastore(settings.guilds_datastore)
bot.add_cog(Meta(bot))
bot.add_cog(Misc(bot))
bot.add_cog(Yahoo(bot, settings.yahoo_key, settings.yahoo_secret, guilds))
bot.run(settings.discord_token, bot=True, reconnect=True)
