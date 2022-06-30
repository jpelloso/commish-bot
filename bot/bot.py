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

if os.environ['HEROKU_DEPLOYMENT']:
    discord_token =  os.environ['DISCORD_TOKEN']
    yahoo_key = os.environ['YAHOO_KEY']
    yahoo_secret = os.environ['YAHOO_SECRET']
else:
    discord_token = settings.discord_token
    yahoo_key = settings.yahoo_key
    yahoo_secret = settings.yahoo_secret

guilds = GuildsDatastore(settings.guilds_datastore)
bot.add_cog(Meta(bot))
bot.add_cog(Misc(bot))
bot.add_cog(Yahoo(bot, yahoo_key, yahoo_secret, guilds))
bot.run(discord_token, bot=True, reconnect=True)
