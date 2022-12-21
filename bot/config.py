import os
import logging
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['settings.toml', '.secrets.toml'],
    environments=True
)

# We cannot loop through Dynaconf settings and dynamically set
# environment b/c of the default Dynaconf vars. If we are running
# from HEROKU, use env vars in the App > Settings > Config Vars section.
# If not, set environment variables from our secrets and settings files
if not os.environ.get('HEROKU_DEPLOYMENT'):
    os.environ['LOG_LEVEL'] = settings.LOG_LEVEL
    os.environ['DISCORD_GUILD'] = settings.DISCORD_GUILD
    os.environ['DISCORD_TOKEN'] = settings.DISCORD_TOKEN
    os.environ['YAHOO_LEAGUE_ID'] = settings.YAHOO_LEAGUE_ID
    os.environ['YAHOO_LEAGUE_TYPE'] = settings.YAHOO_LEAGUE_TYPE
    os.environ['YAHOO_KEY'] = settings.YAHOO_KEY
    os.environ['YAHOO_SECRET'] = settings.YAHOO_SECRET
    os.environ['OAUTH_ACCESS_TOKEN'] = settings.OAUTH_ACCESS_TOKEN
    os.environ['OAUTH_GUID'] = settings.OAUTH_GUID
    os.environ['OAUTH_REFRESH_TOKEN'] = settings.OAUTH_REFRESH_TOKEN
    os.environ['OAUTH_TOKEN_TIME'] = settings.OAUTH_TOKEN_TIME
    os.environ['OAUTH_TOKEN_TYPE'] = settings.OAUTH_TOKEN_TYPE

# Yahoo OAuth needs to be passed in as json
def get_yahoo_oauth():
    yahoo_oauth = {
        "access_token": os.environ['OAUTH_ACCESS_TOKEN'],
        "guid": os.environ['OAUTH_GUID'],
        "refresh_token": os.environ['OAUTH_REFRESH_TOKEN'],
        "token_time": float(os.environ['OAUTH_TOKEN_TIME']),
        "token_type": os.environ['OAUTH_TOKEN_TYPE']
    }
    return yahoo_oauth

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
