import config
import discord
import json
import os
import re
import requests
from cachetools import cached, TTLCache

logger = config.get_logger(__name__)

# https://docs.sleeper.com/

class Sleeper:

    def __init__(self):
        self.endpoint = 'https://api.sleeper.app'
        self.league_id = config.settings.sleeper_league_id
        self.previous_league_id = config.settings.previous_league_id
        self.player_id_map = 'player_id_map.json'

    @cached(cache=TTLCache(maxsize=1024, ttl=600))  
    def handler_error_code(self, code):
        if code == 400:
            return "Sorry, looks like the request was invalid. [400]"
        elif code == 404:
            return "Sorry, looks like the data is not available [404]"
        elif code == 429:
            return "Sorry, looks like you need to relax, Sleeper suggests slowing down the requests! [429]"
        elif code == 500:
            return "Sorry, the Sleeper server is having issues, please try again later [500]"
        elif code == 503:
            return "Sorry, the Sleeper server is temporarily offline for maintenance, please try again later [503]"
        else:
            return "Sorry, I'm having trouble getting that right now, please try again later"

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_regex_search_name(self, player):
        name = re.sub('[^A-Za-z0-9]+', '', player).lower()
        return name

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def is_valid_player(self, player):
        if os.path.exists(self.player_id_map):
            with open(self.player_id_map, 'r') as f:
                players = json.load(f)
            player = self.get_regex_search_name(player)
            result = any(player in d.values() for d in players.values())
            logger.debug('{} -> valid? -> {}'.format(player, result))
            return result
        else:
            logger.error('{} does not exist'.format(self.player_id_map))

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_season(self):
        endpoint = '{}/v1/league/{}'.format(self.endpoint, self.league_id)
        league = requests.get(endpoint, timeout=10)
        if league.status_code == 200:
            data = league.json()
            season = data['season']
            logger.debug(season)
            return season
        else:
            logger.error(self.handle_error_code(league.status_code))
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_status(self):
        endpoint = '{}/v1/league/{}'.format(self.endpoint, self.league_id)
        league = requests.get(endpoint, timeout=10)
        if league.status_code == 200:
            data = league.json()
            status = data['status'] # "pre_draft", "drafting", "in_season", "complete"
            logger.debug(status)
            return status
        else:
            logger.error(self.handle_error_code(league.status_code))
            return None 

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_settings(self):
        endpoint = '{}/v1/league/{}'.format(self.endpoint, self.league_id)
        settings = requests.get(endpoint, timeout=10)
        if settings.status_code == 200:
            logger.debug(settings.json())
            content = settings.json()
        else:
            content = self.handle_error_code(settings.status_code)
        return content
 
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_list(self):
        endpoint = '{}/v1/players/nfl'.format(self.endpoint)
        local_players = {}
        players = requests.get(endpoint, timeout=60)
        if players.status_code == 200:
            for key,values in players.json().items():
                name = '{} {}'.format(values['first_name'], values['last_name'])
                search = self.get_regex_search_name(name)
                local_players[key] = {}
                local_players[key]['name'] = name
                local_players[key]['search'] = search
            with open(self.player_id_map, 'w') as fp:
                json.dump(local_players, fp, indent=4)
                logger.info('created player id map json')
        else:
            logger.error(self.handler_error_code(players.status_code))

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_id(self):
        # if draft status for the current season is 'pre_draft' or 'drafting', get the previous season draft id for results
        if self.get_draft_status() == 'pre_draft' or self.get_draft_status() == 'drafting':
            league_id = self.previous_league_id
            season = int(self.get_season()) - 1
        else:
            league_id = self.league_id
            season = self.get_season()
        endpoint = '{}/v1/league/{}/drafts'.format(self.endpoint, league_id)
        drafts = requests.get(endpoint, timeout=10)
        if drafts.status_code == 200:
            for draft in drafts.json():
                logger.debug(draft['draft_id'])
                return draft['draft_id'], season
        else:
            logger.error(self.handler_error_code(drafts.status_code))

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_results(self):
        draft_id, season = self.get_draft_id()
        endpoint = '{}/v1/draft/{}/picks'.format(self.endpoint, draft_id)
        local_draft_results = {}
        draft_results_file = 'draft_results_{}.json'.format(season)
        # if the local file doesn't exist, request draft results and create it
        if not os.path.exists(draft_results_file):
            picks = requests.get(endpoint, timeout=10)
            if picks.status_code == 200:            
                for result in picks.json():
                    pick = result['pick_no']
                    round = result['round']
                    player = '{} {}'.format(result['metadata']['first_name'], result['metadata']['last_name'])
                    local_draft_results[player] = {}
                    local_draft_results[player]['pick'] = pick
                    local_draft_results[player]['round'] = round
                with open(draft_results_file, 'w') as fp:
                    json.dump(local_draft_results, fp, indent=4)
                    logger.info('created draft results json')
            else:
                logger.error(self.handler_error_code(picks.status_code))
        else:
            logger.info('draft results already exist, not recreating')
        # read the file and return the draft results json    
        with open(draft_results_file, 'r') as f:
            draft_results = json.load(f)
        return draft_results

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_keeper_value(self, keeper):
        pick = None
        round = None
        content = None
        draft_results = self.get_draft_results()
        validated = self.is_valid_player(keeper)
        if validated:
            for player,values in draft_results.items():
                keeper_lower = self.get_regex_search_name(keeper)
                player_lower = self.get_regex_search_name(player)
                if player_lower == keeper_lower:
                    pick = int(values['pick'])
                    round = int(values['round'])
                    drafted = True
                    break
                else:
                    drafted = False
            if drafted:
                if round == 1 or round == 2:
                    content = '**{}** was drafted at pick #{} in round {}. He is not an eligible keeper.'.format(player, pick, round)
                else:
                    content = '**{}** was drafted at pick #{} in round {}. He would cost a pick in **round {}** to keep for next season.'.format(player, pick, round, round - 1)
            else:
                content = '**{}** was not drafted. He would cost a pick in the **7th or 8th round** to keep for next season.'.format(keeper.title())
        else:
            content = "Sorry, I couldn't find a player with the name **{}**. Please check the player name and try again.".format(keeper.title())

        return content
