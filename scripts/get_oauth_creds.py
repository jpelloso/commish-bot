import toml
import logging
from yahoo_oauth import OAuth2
from dynaconf import Dynaconf

oauth_logger = logging.getLogger('yahoo_oauth')
oauth_logger.disabled = True

settings = Dynaconf(settings_files=['settings.toml', '.secrets.toml'], environments=True)
toml_secrets = 'config/example.secrets.toml'

print("Follow this url to login to Yahoo and provide the verifer code...")
oauth = OAuth2(consumer_key=settings.yahoo_key, consumer_secret=settings.yahoo_secret, browser_callback=False)

data = toml.load(toml_secrets)
data['default']['OAUTH_ACCESS_TOKEN'] = oauth.access_token
data['default']['OAUTH_GUID'] = oauth.guid
data['default']['OAUTH_REFRESH_TOKEN'] = oauth.refresh_token
data['default']['OAUTH_TOKEN_TIME'] = oauth.token_time
data['default']['OAUTH_TOKEN_TYPE'] = oauth.token_type

with open(toml_secrets, 'w') as f:
    toml.dump(data, f)
