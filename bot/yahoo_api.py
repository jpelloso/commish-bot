import os
import re
import json
import config
import discord
import objectpath
from yahoo_fantasy_api import game
from cachetools import cached, TTLCache

logger = config.get_logger(__name__)

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
    def is_valid_player(self, league, player):
        player_list = league.player_details(player)
        if player_list:
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
        # team['name'], team['rank'], team['outcome_totals']
        # team['streak'], team['points_for'], team['points_against']
        try:
            league = self.get_league()
            title = 'Standings'
            description = '```\n'
            description += '{:5} {:25} {:8} {}\n'.format('Rank', 'Team', 'Record', 'PF / Streak')
            description += '-----------------------------------------------------\n'
            logger.debug(league.standings())
            for team in league.standings():
                outcomes = team['outcome_totals']
                streak_type = team['streak']['type']
                streak_value = team['streak']['value']
                if streak_type == 'loss':
                    streak = 'L{}'.format(streak_value)
                elif streak_type == 'win':
                    streak = 'W{}'.format(streak_value)
                else:
                    streak = 'T{}'.format(streak_value)
                record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
                description += '{:5} {:25} {:8} {:8} {}\n'.format(team['rank'], team['name'], record, team['points_for'], streak)
            description += '\n```'
            embed = discord.Embed(title=title, description=description, color=0xeee657)
            return embed
        except Exception as e:
            logger.error(e)
            return None

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
                    logger.debug(league.standings())
                    for index, team in enumerate(league.standings()):
                        team_key = team['team_key']
                        manager = self.get_team_manager(league, team_key)
                        outcomes = team['outcome_totals']
                        record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
                        description += ':{}: ` {:35} {:7} `\n'.format(emojis[index], team['name'] + ' (' + manager + ')', record)
                    embed = discord.Embed(title=title, description=description, color=0xeee657)
            else:
                content = 'The `$history` command only accepts a single year as an arugment. Please try again.'
        except Exception as e:
            logger.error(e)
        return content, embed

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

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_roster(self, team_name):
        try:
            content = None
            embed = None
            league = self.get_league()
            team_dict = self.get_team(league, team_name)
            if team_dict:
                team = league.to_team(team_dict['team_key'])
                title = '{} - Roster'.format(team_name)
                description = '```\n'
                logger.debug(team.roster(league.current_week()))
                for player in team.roster(league.current_week()):
                    if player['status']:
                        description += '{:8} {} ({})\n'.format(player['selected_position'], player['name'], player['status'])
                    else:
                        description += '{:8} {}\n'.format(player['selected_position'], player['name'])
                description += '```'
                embed = discord.Embed(title=title, description=description, url=team_dict['url'], color=0xeee657)
                embed.set_thumbnail(url=team_dict['team_logos'][0]['team_logo']['url'])
            else:
                content = "Sorry, I couldn't find a team with the name **{}**. Team names are case sensitive. Please check the team name and try again.".format(team_name)
        except Exception as e:
            logger.error(e)
        return content, embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team(self, league, team_name):
        try:
            for id, team in league.teams().items():
                if team['name'] == team_name:
                    return team
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_waiver_priority(self, team_name):
        try:
            league = self.get_league()
            team_dict = self.get_team(league, team_name)
            if team_dict:
                print(team_dict)
                logger.info(team_dict)
                waiver = team_dict['waiver_priority']
                content = "{} has a waiver priority of **{}**".format(team_name, str(waiver))
            else:
                content = "Sorry, I couldn't find a team with the name **{}**. Team names are case sensitive. Please check the team name and try again.".format(team_name)
            return content
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_faab_balance(self, team_name):
        try:
            league = self.get_league()
            team_dict = self.get_team(league, team_name)
            if team_dict:
                faab = team_dict['faab_balance']
                content = "{} has a FAAB balance of **${}**".format(team_name, str(faab))
            else:
                content = "Sorry, I couldn't find a team with the name **{}**. Team names are case sensitive. Please check the team name and try again.".format(team_name)
            return content
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_manager(self, team_name):
        try:
            league = self.get_league()
            team_dict = self.get_team(league, team_name)
            if team_dict:
                manager = team_dict['managers'][0]['manager']['nickname']
                content = "**{}** is the manager of {}".format(str(manager), team_name)
            else:
                content = "Sorry, I couldn't find a team with the name **{}**. Team names are case sensitive. Please check the team name and try again.".format(team_name)
            return content
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_details(self, player_name):
        try:
            content = None
            embed = None
            league = self.get_league()
            if self.is_valid_player(league, player_name):
                player = league.player_details(player_name)[0]
                logger.debug(player)
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
            else:
                content = "Sorry, I couldn't find a player with the name **{}**. Please check the player name and try again.".format(player_name)
        except Exception as e:
            logger.error(e)
        return content, embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_owner(self, player_id):
        try:
            league = self.get_league()
            player_ownership = league.ownership([player_id])[str(player_id)]
            if 'owner_team_name' in player_ownership:
                return player_ownership['owner_team_name']
            else:
                ownership_map = {
                    'freeagents': 'Free Agent',
                    'waivers':    'On Waviers'
                }
                return ownership_map.get(player_ownership['ownership_type'], "")
        except Exception:
            logger.exception('Error while fetching ownership for player id: {} in league {}'.format(player_id, self.league_id))
            return None

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
            num_playoff_teams = league.settings()['num_playoff_teams']
            league_end_date = league.settings()['end_date']
            content = 'The playoffs for the {} season are **weeks {}-{}** ending on **{}** with {} teams fighting for the chance to be named champion.'.format(
                season, playoff_start_week, playoff_end_week, league_end_date, num_playoff_teams)
            return content
        except Exception as e:
            logger.error(e)
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_keeper_value(self, keeper):
        try:
            league = self.get_league()
            draft_results, season = self.get_draft_results(league)
            pick = None
            round = None
            drafted = False
            content = None
        except Exception as e:
            logger.error(e)
            return None

        # Since the keeper command hits the Yahoo API so many times we will
        # look for a local draft file to read our results from. If it does
        # not exist, we will create it with results returned from Yahoo
        draft_json = {}
        draft_file = '{}_draft_results.json'.format(season)
        if not os.path.exists(draft_file):
            for result in draft_results:
                pick = result['pick']
                round = result['round']
                player = league.player_details(int(result['player_id']))[0]['name']['full']
                draft_json[player] = {}
                draft_json[player]['pick'] = pick
                draft_json[player]['round'] = round
            with open(draft_file, 'w') as fp:
                json.dump(draft_json, fp, indent=4)

        with open(draft_file, 'r') as f:
            draft_results_json = json.load(f)
        for player,value in draft_results_json.items():
            try:
                keeper_lower = re.sub('[^A-Za-z0-9]+', '', keeper).lower()
                player_lower = re.sub('[^A-Za-z0-9]+', '', player).lower()
                if player_lower == keeper_lower:
                    pick = int(value['pick'])
                    round = int(value['round'])
                    drafted = True
                    break
            except:
                pass

        if drafted:
            if round == 1 or round == 2:
                content = '**{}** was drafted at pick #{} in round {}. He is not an eligible keeper.'.format(player, pick, round)
            else:
                content = '**{}** was drafted at pick #{} in round {}. He would cost a pick in **round {}** to keep for next season.'.format(player, pick, round, round - 1)
        else:
            if self.is_valid_player(league, keeper):
                content = '**{}** was not drafted. He would cost a pick in the **7th or 8th round** to keep for next season.'.format(keeper)
            else:
                content = "Sorry, I couldn't find a player with the name **{}**. Please check the player name and try again.".format(keeper)

        return content

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_draft_results(self, league):
        season = league.settings()['season']
        draft_status = league.settings()['draft_status']
        if draft_status == 'postdraft':
            draft_results = league.draft_results()
            return draft_results, season
        else:
            # maybe we renewed the season and haven't drafted yet
            # so we have to get the draft results from the previous season
            season = int(season) - 1
            league = self.get_league(season)
            draft_results = league.draft_results()
            return draft_results, season        
