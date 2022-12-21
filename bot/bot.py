import os
import config
from discord.ext import commands
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo
from datastore import GuildsDatastore

logger = config.get_logger(__name__)

bot = commands.Bot(command_prefix='$', description='')
bot.remove_command('help')

@bot.event
async def on_ready():
    logger.info('Bot is ready')

@bot.event
async def on_guild_join(guild):
    logger.info('Joined {}'.format(guild.name))

# These environment variables get set in Heroku
# under App > Settings > Config Vars
if os.environ.get('HEROKU_DEPLOYMENT'):
    discord_token =  os.environ['DISCORD_TOKEN']
    yahoo_key = os.environ['YAHOO_KEY']
    yahoo_secret = os.environ['YAHOO_SECRET']
else:
    discord_token = config.settings.discord_token
    yahoo_key = config.settings.yahoo_key
    yahoo_secret = config.settings.yahoo_secret

guilds = GuildsDatastore(config.settings.guilds_datastore)
bot.add_cog(Meta(bot))
bot.add_cog(Misc(bot))
bot.add_cog(Yahoo(bot, yahoo_key, yahoo_secret, guilds))
bot.run(discord_token, bot=True, reconnect=True)