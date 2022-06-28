import logging
import os
import re
import discord
import objectpath

from yahoo_fantasy_api import league, game, team, yhandler
from datetime import datetime
from cachetools import cached, TTLCache


logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)


# TODO: make league() -> get_league()
# then combine get_league() and get_past_league()
# to take in optional argument of season

dir_path = os.path.dirname(os.path.realpath(__file__))

class Yahoo:

    oauth = None

    def __init__(self, oauth, league_id, league_type):
        self.oauth = oauth
        self.league_id = league_id
        self.league_type = league_type

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_league(self, year=None):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, self.league_type)
        if year:
            league_id = gm.league_ids(int(year))[0]
        else:
            league_id = '{}.l.{}'.format(gm.game_id(), self.league_id)
        
        return gm.to_league(league_id)

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def league(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, self.league_type)
        return gm.to_league('{}.l.{}'.format(gm.game_id(), self.league_id))
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_past_league(self, year):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, self.league_type)
        league_id = gm.league_ids(year)[0]
        return gm.to_league(league_id)

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_standings(self):
        title = 'Standings (W-L-T)'
        description = ''
        try:
            league = self.get_league()
            for idx, team in enumerate(league.standings()):
                outcomes = team['outcome_totals']
                wins = outcomes['wins']
                losses = outcomes['losses']
                ties = outcomes['ties']
                record = '({}-{}-{})'.format(wins, losses, ties)
                description += '**{}. {}** {}\n'.format(str(idx+1), team['name'], record)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            return embed
        except Exception as e:
            logger.info(e)
            return None
    
        # If Discord ever allows inline embeds on mobile, this format is much better
        #for idx, team in enumerate(self.league().standings()):
        #    outcomes = team['outcome_totals']
        #    record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
        #    standings_dict[str(idx+1) + '. ' + team['name']] = record
        #teams_string = ''
        #records_string = ''
        #for k,v in standings_dict.items():
        #    teams_string += k + '\n'
        #    records_string += v + '\n'
        #embed.add_field(name="Team", value=teams_string)
        #embed.add_field(name="Record", value=records_string)
        #return embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_history(self, past_season):
        content = None
        embed = None
        current_season = int(self.league().settings()['season'])
        name = self.league().settings()['name']
        emojis = ['first_place', 'second_place', 'third_place', 'four', 'five',
            'six', 'seven', 'eight', 'nine', 'keycap_ten', 'poop', 'skull']
        if int(past_season) < 2017:
            content = '{} started in 2017. There is no data before that year.'.format(name)
        elif int(past_season) >= current_season:
            content = '{} is currently in the {} season. There is no data past this year.'.format(name, str(current_season))
        else:
          try:
            league = self.get_past_league(past_season)
            title = '{} Season'.format(past_season)
            description = ''
            for idx, team in enumerate(league.standings()):
                team_key = team['team_key']
                manager = league.teams()[team_key]['managers'][0]['manager']['nickname']
                outcomes = team['outcome_totals']
                record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
                description += ':{}: {} ... {} ... {}\n'.format(emojis[idx], manager, team['name'], record)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
          except Exception as e:
            logger.info('Error while fetching history for the {} season'.format(past_season))
            logger.info(e)
        return content, embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_hall_of_fame(self):
        start = 2017
        end = int(self.league().settings()['season'])
        title = ':trophy:   Hall of Fame'
        description = ''
        thumbnail_url = 'https://c.tenor.com/cpKE-dqxY6gAAAAC/tom-brady-superbowl51.gif'
        try:
            for season in reversed(range(start, end)):
                league = self.get_past_league(season)
                team_key = league.standings()[0]['team_key']
                team_name = league.standings()[0]['name']
                manager = league.teams()[team_key]['managers'][0]['manager']['nickname']
                description += '**{}** - {}\n'.format(season, manager)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            embed.set_thumbnail(url=thumbnail_url)
            return embed
        except Exception as e:
            logger.info('Error while fetching hall of fame for {}'.format(self.league_id))
            logger.info(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_hall_of_shame(self):
        start = 2017
        end = int(self.league().settings()['season'])
        title = ':poop:   Hall of Shame'
        description = ''
        thumbnail_url = 'https://c.tenor.com/qv-F_rn4w1sAAAAC/football-fail.gif'
        # thumbnail_url = 'https://c.tenor.com/8y4-V8lINJsAAAAC/baker-mayfield-browns.gif'
        try:
            for season in reversed(range(start, end)):
                league = self.get_past_league(season)
                team_key = league.standings()[-1]['team_key']
                team_name = league.standings()[-1]['name']
                manager = league.teams()[team_key]['managers'][0]['manager']['nickname']
                description += '**{}** - {}\n'.format(season, manager)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            embed.set_thumbnail(url=thumbnail_url)
            return embed
        except Exception as e:
            logger.info('Error while fetching hall of shame for {}'.format(self.league_id))
            logger.info(e)
            return None


# first place
# last place

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_matchups(self):
        try:
            title = 'Matchups for Week {}'.format(str(self.league().current_week()))
            embed = discord.Embed(title=title, description='', color=0xeee657)
            matchups_json = objectpath.Tree(self.league().matchups())
            matchups = matchups_json.execute('$..scoreboard..matchups..matchup..teams')
            for matchup in matchups:
                team1 = matchup['0']['team']
                team1_name = team1[0][2]['name']
                team1_actual_points = team1[1]['team_points']['total']
                team1_projected_points = team1[1]['team_projected_points']['total']
                if 'win_probability' in team1[1]:
                    team1_win_probability = "{:.0%}".format(team1[1]['win_probability'])
                    team1_details = 'Score: {}\nWin Probability: {}\n'.format(team1_actual_points, team1_win_probability)
                else:
                    team1_details = 'Score: {}\n'.format(team1_actual_points)
                team2 = matchup['1']['team']
                team2_name = team2[0][2]['name']
                team2_actual_points = team2[1]['team_points']['total']
                team2_projected_points = team2[1]['team_projected_points']['total']
                if 'win_probability' in team2[1]:
                    team2_win_probability = "{:.0%}".format(team2[1]['win_probability'])
                    team2_details = 'Score: {}\nWin Probability: {}\n'.format(team2_actual_points, team2_win_probability)
                else:
                    team2_details = 'Score: {}\n'.format(team2_actual_points)
                divider = r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
                embed.add_field(name='{} (Proj. {})'.format(team1_name, team1_projected_points), value=team1_details, inline=False)
                embed.add_field(name='{} (Proj. {})'.format(team2_name, team1_projected_points), value=team2_details + divider, inline=False)
            return embed
        except Exception as e:
            logger.info('Error while fetching matchups for league: {}'.format(self.league_id))
            logger.info(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_roster(self, team_name):
        team = self.get_team(team_name)
        if team:
            title = "{} Roster".format(team_name)
            description = ''
            for idx, player in enumerate(team.roster(self.league().current_week())):
                description += '**{}** - {}'.format(player['selected_position'], player['name']) 
                if idx == 10:
                    description += r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            return embed
        else:
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team(self, team_name):
        try:
            for id, team in self.league().teams().items():
                if team['name'] == team_name:
                    return self.league().to_team(id)
        except Exception as e:
            logger.info("Error while fetching team: {} from league: {}".format(team_name, self.league_id))
            logger.info(e)
            return None
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_details(self, player_name):
        try:
            #player = self.league().player_details(player_name)[0]
            player = self.get_past_league(2021).player_details(player_name)[0]
            title = player['name']['full']
            player_id_list = [int(player['player_id'])]
            description = '#{} - {}'.format(player['uniform_number'], player['editorial_team_full_name'])
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            embed.add_field(name='Postion', value=player['primary_position'])
            if 'bye_weeks' in player:
                embed.add_field(name='Bye', value=player['bye_weeks']['week'])
            else:
                embed.add_field(name='Bye', value='NA')
            embed.add_field(name='Total Points', value=player['player_points']['total'])
            if 'status' in player:
                embed.add_field(name='Status', value=player['status'])
            else:
                embed.add_field(name='Status', value='Healthy')
            embed.add_field(name='% Rostered', value='{}%'.format(self.league().percent_owned(player_id_list)[0]['percent_owned']))
            embed.add_field(name='Keeper', value=player['is_keeper']['kept'])
            embed.add_field(name='Owner', value=self.get_player_owner(player['player_id']))
            embed.set_thumbnail(url=player['image_url'])
            return embed
        except Exception as e:
            logger.exception("Error while fetching player details for player: {} in league {}".format(player_name, self.league_id))
            return None
    
    # TODO: check if the player is valid first so we can determine if the player was not found or if the player exists but was not drafted
    # TODO: get season - 3 and check is_keeper status and increment for every time True to determine validity of keeper
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_keeper_value(self, keeper):
        try:
            #league = self.get_past_league(2021)
            league = self.league()
            draft_results = self.get_draft_results(league)
            pick = None
            round = None
            drafted = False
            content = None
            for result in draft_results:

                drafted_player = league.player_details(int(result['player_id']))[0]['name']['full']
                if drafted_player == keeper:
                    pick = int(result['pick'])
                    round = int(result['round'])
                    drafted = True
                    break

            if drafted:
                if round == 1 or round == 2:
                    content = '**{}** was drafted at **pick #{}** in **round {}**. He is not an eligible keeper.'.format(keeper, pick, round)
                else:
                    content = '**{}** was drafted at **pick #{}** in **round {}**. He would cost a pick in **_round {}_** to keep for next season.'.format(keeper, pick, round, round - 1)
            else:
                content = '{} was not drafted. He would cost a 7th or 8th round to keep for next season.'.format(keeper)

            return content

                    # result['round'] result['pick'] result['team_key']


        except Exception as e:
            logger.info("Error while fetching team from league: {}".format(self.league_id))
            logger.info(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_results(self, league):
        try:
            draft_results = league.draft_results()
            return draft_results
        except:
            # maybe we renewed the season and have drafted yet
            # so we have to get the draft results from the previous season
            season = int(league.settings()['season']) - 1
            league = self.get_past_league(season)
            draft_results = league.draft_results()
            return draft_results


    # TODO:
    #@cached(cache=TTLCache(maxsize=1024, ttl=600))
    #def is_valid_player(self, league):

    #@cached(cache=TTLCache(maxsize=1024, ttl=600))
    #def is_valid_team(self, league):


    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_owner(self, player_id):
        try:
            player_ownership = self.league().ownership([player_id])[str(player_id)]
            if 'owner_team_name' in player_ownership:
                return player_ownership['owner_team_name']
            else:
                ownership_map = {
                    "freeagents": "Free Agent",
                    "waivers":    "On Waviers"      
                }
                return ownership_map.get(player_ownership['ownership_type'], "")
        except Exception:
            logger.exception("Error while fetching ownership for player id: {} in league {}".format(player_id, self.league_id))
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_latest_trade(self):
        try:
            for key, values in self.league().teams().items():
                if 'is_owned_by_current_login' in values:
                    team = self.league().to_team(key)
                    accepted_trades = list(filter(lambda d: d['status'] == 'accepted', team.proposed_trades()))
                    if accepted_trades:
                        return accepted_trades[0]
            return
        except Exception:
            logger.exception("Error while fetching latest trade")