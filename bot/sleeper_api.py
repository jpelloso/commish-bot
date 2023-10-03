
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
        with open(self.player_id_map, 'r') as f:
            players = json.load(f)
        player = self.get_regex_search_name(player)
        result = any(player in d.values() for d in players.values())
        return result

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_season(self):
        endpoint = '{}/v1/league/{}'.format(self.endpoint, self.league_id)
        league = requests.get(endpoint, timeout=10)
        if league.status_code == 200:
            data = league.json()
            season = data['season']
            return season
        else:
            logger.error(self.handle_error_code(league.status_code))
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_settings_bit_value(self, bit):
        if bit == 1:
            return "Yes"
        else:
            return "No"

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_settings(self):
        content = None
        embed = None
        endpoint = "{}/v1/league/{}".format(self.endpoint, self.league_id)
        title = ':gear:  League Settings'
        description = ''
        embed = discord.Embed(title=title, description=description, color=0xeee657)
        settings = requests.get(endpoint, timeout=10)
        if settings.status_code == 200:
            logger.info(settings.json())
            data = settings.json()
            embed.add_field(name='League ID', value=data['league_id'], inline=False)
            embed.add_field(name='Roster Positions', value=str(data['roster_positions'])[1:-1].replace("'",""), inline=False)
            embed.add_field(name='Injured Reserved Slots', value=data['settings']['reserve_slots'], inline=False)
            bench_lock = self.get_settings_bit_value(data['settings']['bench_lock'])
            embed.add_field(name='Bench Players Lock', value=bench_lock, inline=False)
            embed.add_field(name='Maximum Keepers', value=data['settings']['max_keepers'], inline=False)
            embed.add_field(name='Waiver Type', value='FAAB', inline=False)
            embed.add_field(name='Waiver Budget', value=data['settings']['waiver_budget'], inline=False)
            embed.add_field(name='Trade Deadline', value='Week {}'.format(data['settings']['trade_deadline']), inline=False)
            embed.add_field(name='Days to Review Trades', value='{} days'.format(data['settings']['trade_review_days']), inline=False)
            embed.add_field(name='Veto Votes Needed', value='{} votes'.format(data['settings']['veto_votes_needed']), inline=False)
            pick_trading = self.get_settings_bit_value(data['settings']['pick_trading'])
            embed.add_field(name='Trade Draft Picks', value=pick_trading, inline=False)
            embed.add_field(name='Playoffs Start Week', value='Week {}'.format(data['settings']['playoff_week_start']), inline=False)
            embed.add_field(name='Number of Playoff Teams', value='{} teams'.format(data['settings']['playoff_teams']), inline=False)
        else:
            content = self.handle_error_code(settings.status_code)
        return content, embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_history(self):
        content = 'Yahoo! league history has been imported into Sleeper, but is not accessible via the API. In the Sleeper app, navigate to **Settings > League history** to view all-time stats and history from previous seasons.'
        return content

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_list(self):
        endpoint = '{}/v1/players/nfl'.format(self.endpoint)
        local_players = {}
        player_id_map_file = 'player_id_map.json'
        if not os.path.exists(player_id_map_file):
            players = requests.get(endpoint, timeout=60)
            if players.status_code == 200:
                for key,values in players.json().items():
                    name = '{} {}'.format(values['first_name'], values['last_name'])
                    search = self.get_regex_search_name(name)
                    local_players[key] = {}
                    local_players[key]['name'] = name
                    local_players[key]['search'] = search
                with open(player_id_map_file, 'w') as fp:
                    json.dump(local_players, fp, indent=4)
                    logger.info('created player id map json')
            else:
                logger.error(self.handler_error_code(players.status_code))

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_id(self):
        endpoint = '{}/v1/league/{}/drafts'.format(self.endpoint, self.league_id)
        drafts = requests.get(endpoint, timeout=10)
        if drafts.status_code == 200:
            for draft in drafts.json():
                if draft['season'] == self.get_season():
                    return draft['draft_id']
        else:
            logger.error(self.handler_error_code(drafts.status_code))

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_results(self):
        draft_id = self.get_draft_id()
        endpoint = '{}/v1/draft/{}/picks'.format(self.endpoint, draft_id)
        local_draft_results = {}
        draft_results_file = 'draft_results_{}.json'.format(self.get_season())
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
