import os
import logging
from dynaconf import Dynaconf

settings = Dynaconf(settings_files=['settings.toml'], environments=True)

# We cannot loop through Dynaconf settings and dynamically set
# environment b/c of the default Dynaconf vars. If we are running
# from HEROKU, use env vars in the App > Settings > Config Vars section.
# If not, set environment variables from our secrets and settings files
if not os.environ.get('HEROKU_DEPLOYMENT'):
    os.environ['LOG_LEVEL'] = settings.LOG_LEVEL
    os.environ['DISCORD_GUILD'] = settings.DISCORD_GUILD
    os.environ['DISCORD_TOKEN'] = settings.DISCORD_TOKEN
    os.environ['SLEEPER_LEAGUE_ID'] = settings.SLEEPER_LEAGUE_ID
    os.environ['PREVIOUS_LEAGUE_ID'] = settings.PREVIOUS_LEAGUE_ID

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(os.environ['LOG_LEVEL'])
    if not logger.handlers:
        # prevent logging from propagating to root logger
        logger.propagate = 0
        ch = logging.StreamHandler()
        ch.setLevel(os.environ['LOG_LEVEL'])
        formatter = logging.Formatter('[%(asctime)s %(levelname)s] [%(name)s.%(funcName)s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
