import config
import discord
from cogs.meta import Meta
from cogs.sleeper import Sleeper
from discord.ext import commands

logger = config.get_logger(__name__)

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all(), description='')
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.add_cog(Meta(bot))
    await bot.add_cog(Sleeper(bot))
    logger.info('Bot is ready')

@bot.event
async def on_guild_join(guild):
    logger.info('Joined {}'.format(guild.name))

bot.run(config.settings.discord_token, reconnect=True)
