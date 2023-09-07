
import config
import discord
import json
import requests
from cachetools import cached, TTLCache

logger = config.get_logger(__name__)

class Sleeper:

    def __init__(self):
        self.jon = "jon"
        self.league_id = 999735878371053568
        self.endpoint = "https://api.sleeper.app"
        #curl "https://api.sleeper.app/v1/league/<league_id>/transactions/<round>"
        # 400 	Bad Request -- Your request is invalid.
        # 404 	Not Found -- The specified kitten could not be found.
        # 429 	Too Many Requests -- You're requesting too many kittens! Slow down!
        # 500 	Internal Server Error -- We had a problem with our server. Try again later.
        # 503 	Service Unavailable -- We're temporarily offline for maintenance. Please try again later.
    
    def handler_error_code(code):
        print("error")

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_standings(self):
        endpoint = "https://api.sleeper.app/v1/league/999735878371053568"
        r = requests.get(endpoint, timeout=10)
        logger.info(r.status_code)
        logger.info(r.json())
