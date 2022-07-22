import os
import re
import time
import logging
import discord
import objectpath
from config import settings
from yahoo_fantasy_api import game
from cachetools import cached, TTLCache

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(settings.log_level)

    # TODO:
    #   error messages
    #   exceptions (logging.error)

class Yahoo:

    oauth = None

    def __init__(self, oauth, league_id, league_type):
        self.oauth = oauth
        self.league_id = league_id
        self.league_type = league_type
        self.embed_divider = r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'

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
    def get_league_season(self, league):
        return int(league.settings()['season'])
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_league_name(self, league):
        return league.settings()['name']

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team_manager(self, league, team_key):
        return league.teams()[team_key]['managers'][0]['manager']['nickname']

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def is_valid_player(self, league, player_name):
        player = league.player_details(player_name)
        if player:
            return True
        else:
            return False

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def is_integer(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_standings(self):
        try:
            league = self.get_league()
            title = 'Standings'
            description = ''
            for index, team in enumerate(league.standings()):
                outcomes = team['outcome_totals']
                record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
                description += '{}. {} ({})\n'.format(str(index+1), team['name'], record)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            return embed
        except Exception as e:
            logger.error(e)
            return None
    
        # If Discord ever allows inline embeds on mobile, this format is much better
        # for idx, team in enumerate(league.standings()):
        #    standings[str(index+1) + '. ' + team['name']] = record
        # for k,v in standings_dict.items():
        #    teams += k + '\n'
        #    records += v + '\n'
        # embed.add_field(name="Team", value=teams_string)
        # embed.add_field(name="Record", value=records_string)

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_history(self, past_season):
        try:
            content = None
            embed = None
            if self.is_integer(past_season):
                league = self.get_league()
                league_name = self.get_league_name(league)
                current_season = self.get_league_season(league)
                past_season = int(past_season)
                emojis = ['first_place', 'second_place', 'third_place', 'four', 'five',
                    'six', 'seven', 'eight', 'nine', 'keycap_ten', 'poop', 'skull']
                if past_season < 2017:
                    content = '{} started in 2017. There is no league data before that year.'.format(league_name)
                elif past_season >= current_season:
                    content = '{} is currently in the {} season. There is no league data past this year.'.format(league_name, str(current_season))
                else:
                    league = self.get_league(past_season)
                    title = '{} Season'.format(past_season)
                    description = ''
                    for index, team in enumerate(league.standings()):
                        team_key = team['team_key']
                        manager = self.get_team_manager(league, team_key)
                        outcomes = team['outcome_totals']
                        record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
                        description += ':{}: {} - {} ({})\n'.format(emojis[index], team['name'], manager, record)
                    embed = discord.Embed(title=title, description=description, color=0xeee657)
            else:
                content = 'The `$history` command only accepts a single year as an arugment. Please try again.'
        except Exception as e:
            logger.error(e)    
        return content, embed
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_overall_history(self, title, thumbnail_url, index):
        try:
            league = self.get_league()
            start = 2017
            end = self.get_league_season(league)
            description = ''
            for season in reversed(range(start, end)):
                league = self.get_league(season)
                team_key = league.standings()[index]['team_key']
                team_name = league.standings()[index]['name']
                manager = self.get_team_manager(league, team_key)
                description += '**{}** - {} - {}\n'.format(season, team_name, manager)
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            embed.set_thumbnail(url=thumbnail_url)
            return embed
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_hall_of_fame(self):
        title = ':trophy:   Hall of Fame'
        thumbnail_url = 'https://c.tenor.com/cpKE-dqxY6gAAAAC/tom-brady-superbowl51.gif'
        index = 0   # first place in league.standings()
        embed = self.get_overall_history(title, thumbnail_url, index)
        return embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_hall_of_shame(self):
        title = ':poop:   Hall of Shame'
        thumbnail_url = 'https://c.tenor.com/qv-F_rn4w1sAAAAC/football-fail.gif'
        index = -1   # last place in league.standings()
        embed = self.get_overall_history(title, thumbnail_url, index)
        return embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_matchups(self):
        try:
            league = self.get_league()
            title = 'Matchups for Week {}'.format(str(league.current_week()))
            embed = discord.Embed(title=title, description='', color=0xeee657)
            matchups_json = objectpath.Tree(league.matchups())
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
                embed.add_field(name='{} (Proj. {})'.format(team1_name, team1_projected_points), value=team1_details, inline=False)
                embed.add_field(name='{} (Proj. {})'.format(team2_name, team2_projected_points), value=team2_details + self.embed_divider, inline=False)
            return embed
        except Exception as e:
            logger.error(e)
            return None

    # TODO: check team name and if not valid return a list of team names/managers
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_roster(self, team_name):
        league = self.get_league()
        team = self.get_team(league, team_name)
        if team:
            title = "{} - Roster".format(team_name)
            description = ''
            for player in team.roster(league.current_week()):
                description += '**{}** - {}'.format(player['selected_position'], player['name']) 
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            return embed
        else:
            return None

    # league.teams().items()
    # team['name'], team['managers'][0]['manager']['nickname']

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team(self, league, team_name):
        try:
            for id, team in league.teams().items():
                if team['name'] == team_name:
                    return league.to_team(id)
        except Exception as e:
            logger.error(e)
            return None
    
    # TODO: check player name and if not valid return invalid player
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_details(self, player_name):
        try:
            league = self.get_league()
            player = league.player_details(player_name)[0]
            title = player['name']['full']
            player_id_list = [int(player['player_id'])]
            description = '#{} - {}'.format(player['uniform_number'], player['editorial_team_full_name'])
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            embed.add_field(name='Postion', value=player['primary_position'])
            if 'bye_weeks' in player:
                embed.add_field(name='Bye Week', value=player['bye_weeks']['week'])
            else:
                embed.add_field(name='Bye Week', value='NA')
            embed.add_field(name='Total Points', value=player['player_points']['total'])
            embed.add_field(name='% Rostered', value='{}%'.format(league.percent_owned(player_id_list)[0]['percent_owned']))
            if 'status' in player:
                embed.add_field(name='Status', value=player['status'])
            else:
                embed.add_field(name='Status', value='Healthy')
            embed.add_field(name='Keeper', value=player['is_keeper']['kept'])
            embed.add_field(name='Owner', value=self.get_player_owner(player['player_id']))
            embed.set_thumbnail(url=player['image_url'])
            return embed
        except Exception as e:
            logger.error(e)
            return None
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_owner(self, player_id):
        try:
            league = self.get_league()
            player_ownership = league.ownership([player_id])[str(player_id)]
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


    # TODO: check if player is valid before going through draft results
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_keeper_value(self, keeper):
        try:
            league = self.get_league()
            draft_results = self.get_draft_results(league)
            pick = None
            round = None
            drafted = False
            content = None
        except Exception as e:
            logger.error(e)
            return None
        
        # Widen the scope of the try catch so we try/catch the player details
        # Draft results contain a player/player id that is no longer valid in 
        # Yahoo! sports and causes an exception. If we encounter a case like that
        # pass and continue on looking at the draft results.
        for result in draft_results:
            time.sleep(0.5)
            try:
                drafted_player = league.player_details(int(result['player_id']))[0]['name']['full']
                keeper = re.sub('[^A-Za-z0-9]+', '', keeper).lower()
                drafted_player = re.sub('[^A-Za-z0-9]+', '', drafted_player).lower()
                if drafted_player == keeper:
                    pick = int(result['pick'])
                    round = int(result['round'])
                    drafted = True
                    break
            except:
                pass

        if drafted:
            if round == 1 or round == 2:
                content = '**{}** was drafted at pick #{} in round {}. He is not an eligible keeper.'.format(keeper, pick, round)
            else:
                content = '**{}** was drafted at pick #{} in round {}. He would cost a pick in **round {}** to keep for next season.'.format(keeper, pick, round, round - 1)
        else:
            if self.is_valid_player(league, keeper):
                content = '{} was not drafted. He would cost a 7th or 8th round to keep for next season.'.format(keeper)
            else:
                content = 'Sorry, I couldn\'t find a player with name *{}*. Please check the player name and try again.'.format(keeper)

        return content

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_results(self, league):
        try:
            draft_results = league.draft_results()
            return draft_results
        except:
            # maybe we renewed the season and have drafted yet
            # so we have to get the draft results from the previous season
            season = int(league.settings()['season']) - 1
            league = self.get_league(season)
            draft_results = league.draft_results()
            return draft_results

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_trade_deadline(self):
        try:
            league = self.get_league()
            season = self.get_league_season(league)
            trade_deadline = league.settings()['trade_end_date']
            content = 'The trade deadline for the {} season is **{}**.'.format(season, trade_deadline)
            return content
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_playoffs_details(self):
        try:
            league = self.get_league()
            season = self.get_league_season(league)
            playoff_start_week = league.settings()['playoff_start_week']
            playoff_end_week = league.settings()['end_week']
            playoff_end_date = league.settings()['end_date']
            num_playoff_teams = league.settings()['num_playoff_teams']
            content = 'The playoffs for the {} season are **weeks {}-{}** with {} teams fighting for the chance to be named champion.'.format(season, playoff_start_week, playoff_end_week, num_playoff_teams)
            return content
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_latest_trade(self):
        try:
            league = self.get_league()
            for key, values in league.teams().items():
                if 'is_owned_by_current_login' in values:
                    team = league.to_team(key)
                    accepted_trades = list(filter(lambda d: d['status'] == 'accepted', team.proposed_trades()))
                    if accepted_trades:
                        return accepted_trades[0]
            return
        except Exception:
            logger.exception("Error while fetching latest trade")
