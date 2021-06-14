import requests
import json

import pandas as pd
import pandasql as ps
import numpy as np

import os
from dotenv import load_dotenv

from highcharts import Highchart

# silencing false positives from pandas' SettingWithCopyWarning
pd.options.mode.chained_assignment = None

print('Initializing data extraction from OpenDota API...')

load_dotenv()
API_KEY = os.getenv('API_KEY')

# instantiating a counter to track how many calls we make to opendota's API
api_counter = 0

save_file_path = "..\\data\\DPC1S2\\animajor\\{}"
dfs_to_convert = {}
jsons_to_upload = {}

api = 'https://api.opendota.com/api'
link = '{}/proMatches?api_key={}'.format(api, API_KEY)

r = requests.get(link)
api_counter += 1
data = json.loads(r.text)
df = pd.DataFrame(data)

# --- INTITAL DATA PULL --- #

print('Pulling all relevant matches...')

# time at which the first match of the animajor started
start_time = 1622513391

while df[-1::]['start_time'].iloc[0] > start_time:
    print('Appending new set of data ending in match_id: {}'.format(df[-1::]['match_id'].iloc[0]))
    temp_link = '{}&less_than_match_id={}'.format(link, df[-1::]['match_id'].iloc[0])
    r = requests.get(temp_link)
    api_counter += 1
    data = json.loads(r.text)
    df = df.append(pd.DataFrame(data))

# --- ANIMAJOR DATA FILTER--- #

# animajor league ID
league_id = 12964 

animajor_matches = df[df['leagueid'] == league_id]
dfs_to_convert['animajor_matches'] = animajor_matches

hero_stats = pd.DataFrame()
total_pbs = pd.DataFrame()

# server crashed during these games or something idk
excluded_match_ids = [6025172903, 6023211594, 6023110186, 6034640592]

print('Extracting detailed match data...')

for match_id in animajor_matches['match_id'].tolist():
    if match_id not in excluded_match_ids:
        match_link = '{}/matches/{}?api_key={}'.format(api, match_id, API_KEY)
        r = requests.get(match_link)
        api_counter += 1
        data = json.loads(r.text)

        draft_timings_df = pd.DataFrame(data['draft_timings'])
        draft_timings_df['match_id'] = match_id

        draft_pbs_df = pd.DataFrame(data['picks_bans'])
        draft_pbs_df['team'] = ['Radiant' if i == 0 else 'Dire' for i in draft_pbs_df['team'].tolist()]

        if data['radiant_win']:
            draft_pbs_df['winning_team'] = 'Radiant' 
            hero_stats['winning_team'] = 'Radiant'
        else:
            draft_pbs_df['winning_team'] = 'Dire'
            hero_stats['winning_team'] = 'Dire'

        hero_stats = hero_stats.append(draft_timings_df, sort = False)
        hero_stats.reset_index(drop = True, inplace = True)

        total_pbs = total_pbs.append(draft_pbs_df, sort = False)
        total_pbs.reset_index(drop = True, inplace = True)
        
first_picks = total_pbs[total_pbs['order'] == 4].reset_index(drop = True)
dfs_to_convert['first_picks'] = first_picks

# --- HEROES DATA --- #

print('Extracting hero data...')

heroes_link = '{}/heroes'.format(api)

r = requests.get(heroes_link)
api_counter += 1
data = json.loads(r.text)
heroes_df = pd.DataFrame(data)
heroes = heroes_df[['id', 'localized_name', 'primary_attr']]
heroes = heroes.replace({'Outworld Destroyer': 'Outworld Devourer'})

# --- HERO PICKS & BANS --- #

print('Creating data transformation for hero picks and bans...')

sql_query = """
SELECT  total_pbs.hero_id,
        heroes.localized_name AS hero_name,
        SUM(CASE 
            WHEN total_pbs.is_pick = True THEN 1
            ELSE 0
        END) AS hero_picks,
        SUM(CASE 
            WHEN total_pbs.is_pick = False THEN 1
            ELSE 0
        END) AS hero_bans
FROM total_pbs
JOIN heroes
ON total_pbs.hero_id = heroes.id
GROUP BY hero_id, heroes.localized_name
"""

hero_counts = ps.sqldf(sql_query)

hero_counts['total_pbs'] = hero_counts['hero_picks'] + hero_counts['hero_bans']
hero_counts = hero_counts.astype({'hero_id': 'int32'})

for i in heroes[['id', 'localized_name']].iterrows():
    hero_id = i[1][0]
    hero_name = i[1][1]
    
    if hero_name not in hero_counts['hero_name'].tolist():
        hero_counts = hero_counts.append({'hero_id': hero_id, 'hero_name': hero_name, 'hero_picks': 0, 'hero_bans': 0, 'total_pbs': 0}, ignore_index = True)
        
hero_counts.sort_values(by = ['total_pbs', 'hero_picks', 'hero_bans'], ascending = False, inplace = True)
hero_counts['drilldown_picks'] = hero_counts['hero_name']

dfs_to_convert['hero_counts'] = hero_counts

hero_picks = hero_counts[['hero_name', 'hero_picks']]
hero_picks['drilldown'] = hero_picks['hero_name'] + ' Picks'
hero_picks = hero_picks.rename(columns = {'hero_name': 'name', 'hero_picks': 'y'})

dfs_to_convert['hero_picks'] = hero_picks

hero_bans = hero_counts[['hero_name', 'hero_bans']]
hero_bans['drilldown'] = hero_bans['hero_name'] + ' Bans'
hero_bans = hero_bans.rename(columns = {'hero_name': 'name', 'hero_bans': 'y'})

dfs_to_convert['hero_bans'] = hero_bans

# --- TEAM PICKS & BANS --- # 

print('Creating data transformation for team specific picks and bans...')

sql_query = """
SELECT  total_pbs.match_id,
        heroes.localized_name AS hero_name,
        CASE 
            WHEN total_pbs.is_pick = True THEN 'pick'
            WHEN total_pbs.is_pick = False THEN 'ban'
        END AS draft_type,
        CASE 
            WHEN total_pbs.team = 'Radiant' THEN am.radiant_name
            WHEN total_pbs.team = 'Dire' THEN am.dire_name
        END AS picking_team,
        CASE 
            WHEN total_pbs.team = 'Radiant' THEN am.dire_name
            WHEN total_pbs.team = 'Dire' THEN am.radiant_name
        END AS opposing_team,
        CASE 
            WHEN total_pbs.winning_team = 'Radiant' THEN am.radiant_name
            WHEN total_pbs.winning_team = 'Dire' THEN am.dire_name
        END AS winning_team,
        total_pbs.ord AS draft_order
FROM total_pbs
JOIN heroes
ON total_pbs.hero_id = heroes.id
JOIN animajor_matches AS am
ON total_pbs.match_id = am.match_id
"""

team_pbs = ps.sqldf(sql_query)

team_bans_against = team_pbs[team_pbs['draft_type'] == 'ban'].groupby(['hero_name', 'opposing_team']).count()['match_id'].reset_index().sort_values(by = 'match_id', ascending = False).reset_index(drop = True).rename({'match_id': 'bans_against', 'opposing_team': 'team'}, axis = 'columns')
team_picks_for = team_pbs[team_pbs['draft_type'] == 'pick'].groupby(['hero_name', 'picking_team']).count()['match_id'].reset_index().sort_values(by = 'match_id', ascending = False).reset_index(drop = True).rename({'match_id': 'picks_for', 'picking_team': 'team'}, axis = 'columns')

total_team_pbs = team_picks_for.merge(team_bans_against, how = 'outer', left_on = ['hero_name', 'team'], right_on = ['hero_name', 'team'])
total_team_pbs.fillna({'bans_against': 0, 'picks_for': 0}, inplace = True)

total_team_pbs['total'] = total_team_pbs['picks_for'] + total_team_pbs['bans_against']
total_team_pbs.sort_values(by = 'total', ascending = False, inplace = True)
total_team_pbs.reset_index(drop = True, inplace = True)

dfs_to_convert['total_team_pbs'] = total_team_pbs

team_picks_and_bans = []

for hero in sorted(total_team_pbs['hero_name'].unique()):
    temp_df = total_team_pbs[total_team_pbs['hero_name'] == hero]
    team_picks_and_bans.append({'name': hero + ' Picks For', 'id': hero + ' Picks', 'data': temp_df[['team', 'picks_for']].to_numpy().tolist()})
    team_picks_and_bans.append({'name': hero + ' Bans Against', 'id': hero + ' Bans', 'data': temp_df[['team', 'bans_against']].to_numpy().tolist()})

jsons_to_upload['team_picks_and_bans'] = team_picks_and_bans

# --- HERO WIN RATES --- #

print('Creating data transformation for hero win rates...')

sql_query = """
SELECT  heroes.localized_name AS hero_name,
        hero_stats.match_id,
        CASE 
            WHEN hero_stats.active_team = 2 THEN 'Radiant'
            ELSE 'Dire'
        END AS picking_team,
        CASE
            WHEN am.radiant_win = True THEN 'Radiant'
            ELSE 'Dire'
        END AS winning_team
FROM hero_stats
JOIN heroes
ON hero_stats.hero_id = heroes.id
JOIN animajor_matches AS am
ON hero_stats.match_id = am.match_id
WHERE hero_stats.pick = True
"""

hero_wins = ps.sqldf(sql_query)
hero_wins['match_won'] = [True if i == j else False for i, j in hero_wins[['picking_team', 'winning_team']].itertuples(index = False)]

total_hero_wins = hero_wins.groupby('hero_name')['match_won'].agg(['sum', 'count']).rename(columns = {'sum': 'matches_won', 'count': 'matches_played'}).reset_index()
total_hero_wins['win_rate'] = total_hero_wins['matches_won'] / total_hero_wins['matches_played']
total_hero_wins.sort_values(by = ['matches_played', 'matches_won'], ascending = False, inplace = True)

hero_matches_played = total_hero_wins[['hero_name', 'matches_played']].rename(columns = {'matches_played': 'y'})
hero_matches_won = total_hero_wins[['hero_name', 'matches_won']].rename(columns = {'wins': 'y'})
hero_win_rates = total_hero_wins[['hero_name', 'win_rate']].rename(columns = {'win_rate': 'y'})

hero_matches_played['drilldown'] = hero_matches_played['hero_name'] + ' Matches Played'
hero_matches_won['drilldown'] = hero_matches_won['hero_name'] + ' Matches Won'
hero_win_rates['drilldown'] = hero_win_rates['hero_name'] + ' Win Rate'

dfs_to_convert['hero_matches_played'] = hero_matches_played
dfs_to_convert['hero_matches_won'] = hero_matches_won
dfs_to_convert['hero_win_rates'] = hero_win_rates

# -- TEAM WIN RATES --- #

sql_query = """
SELECT  match_id,
        radiant_name AS team,
        CASE
            WHEN radiant_win = True THEN 1
            ELSE 0
        END AS result,
        duration
FROM animajor_matches
UNION ALL
SELECT  match_id,
        dire_name AS team,
        CASE
            WHEN radiant_win = True THEN 0
            ELSE 1
        END AS result,
        duration
FROM animajor_matches
"""

team_stats = ps.sqldf(sql_query)

team_stats = team_stats.groupby('team').agg({'result': 'sum', 'match_id': 'count', 'duration': 'mean'}).reset_index(drop = False).rename(columns = {'team': 'name', 'result': 'matches_won', 'match_id': 'matches_played', 'duration': 'avg_match_length'})
team_stats['win_rate'] = 100*(team_stats['matches_won'] / team_stats['matches_played'])

team_matches_played = team_stats[['name', 'matches_played']].rename(columns = {'matches_played': 'y'})
team_matches_won = team_stats[['name', 'matches_won']].rename(columns = {'matches_won': 'y'})
team_win_rates = team_stats[['name', 'win_rate']].rename(columns = {'win_rate': 'y'})

team_matches_played['drilldown'] = team_stats['name'] + ' Matches Played'
team_matches_won['drilldown'] = team_stats['name'] + ' Matches Won'
team_win_rates['drilldown'] = team_stats['name'] + ' Win Rate'

dfs_to_convert['team_matches_played'] = team_matches_played
dfs_to_convert['team_matches_won'] = team_matches_won
dfs_to_convert['team_win_rates'] = team_win_rates

# --- TEAM+HERO WIN RATES --- #

print('Creating data transformation for team specific hero win rates...')

sql_query = """
SELECT  picking_team AS team,
        hero_name AS hero,
        SUM(CASE 
                WHEN picking_team = winning_team THEN 1
                ELSE 0
        END) AS matches_won,
        SUM(CASE
                WHEN picking_team != winning_team THEN 1
                ELSE 0
        END) AS matches_lost
FROM team_pbs
WHERE draft_type = 'pick'
GROUP BY team, hero
"""

team_hero_wins = ps.sqldf(sql_query)

team_hero_wins['matches_played'] = team_hero_wins['matches_won'] + team_hero_wins['matches_lost']
team_hero_wins['win_rate'] = team_hero_wins['matches_won'] / team_hero_wins['matches_played']

total_team_heroes = []

for hero in sorted(team_hero_wins['hero'].unique()):
    temp_df = team_hero_wins[team_hero_wins['hero'] == hero]
    total_team_heroes.append({'name': hero + ' Matches Played', 'id': hero + ' Matches Played', 'data': temp_df[['team', 'matches_played']].to_numpy().tolist()})
    total_team_heroes.append({'name': hero + ' Matches Won', 'id': hero + ' Matches Won', 'data': temp_df[['team', 'matches_won']].to_numpy().tolist()})
    total_team_heroes.append({'name': hero + ' Win Rate', 'id': hero + ' Win Rate', 'data': temp_df[['team', 'win_rate']].to_numpy().tolist(), 'type': 'spline', 'yAxis': 1, 'lineWidth': 0, 'states': {'hover': {'enabled': False}}, 'marker': {'symbol': 'diamond', 'radius': 6}})

total_hero_teams = []

for team in sorted(team_hero_wins['team'].unique()):
    temp_df = team_hero_wins[team_hero_wins['team'] == team]
    total_hero_teams.append({'name': team + ' Matches Played', 'id': team + ' Matches Played', 'data': temp_df[['team', 'matches_played']].to_numpy().tolist()})
    total_hero_teams.append({'name': team + ' Matches Won', 'id': team + ' Matches Won', 'data': temp_df[['team', 'matches_won']].to_numpy().tolist()})
    total_hero_teams.append({'name': team + ' Win Rate', 'id': team + ' Win Rate', 'data': temp_df[['team', 'win_rate']].to_numpy().tolist(), 'type': 'spline', 'yAxis': 1, 'lineWidth': 0, 'states': {'hover': {'enabled': False}}, 'marker': {'symbol': 'diamond', 'radius': 6}})

jsons_to_upload['total_team_heroes'] = total_team_heroes
jsons_to_upload['total_hero_teams'] = total_hero_teams

# --- RADIANT VS DIRE FIRST PICKS --- # 

print('Creating data transformation for radiant versus dire pick orders...')

rad_fps = len(first_picks[first_picks['team'] == 'Radiant'])
dire_fps = len(first_picks[first_picks['team'] == 'Dire'])

rad_wins = len(first_picks[first_picks['winning_team'] == 'Radiant'])
dire_wins = len(first_picks[first_picks['winning_team'] == 'Dire'])

wins_fps = len(first_picks[first_picks['team'] == first_picks['winning_team']])
losses_fps = len(first_picks[first_picks['team'] != first_picks['winning_team']])

rad_rad = len(first_picks[(first_picks['winning_team'] == 'Radiant') & (first_picks['team'] == 'Radiant')])
rad_dire = len(first_picks[(first_picks['winning_team'] == 'Radiant') & (first_picks['team'] == 'Dire')])
dire_dire = len(first_picks[(first_picks['winning_team'] == 'Dire') & (first_picks['team'] == 'Dire')])
dire_rad = len(first_picks[(first_picks['winning_team'] == 'Dire') & (first_picks['team'] == 'Radiant')])

fps_dict = {'rad_fps': rad_fps, 'dire_fps': dire_fps, 'wins_fps': wins_fps, 'losses_fps': losses_fps, 'rad_fps_rad_wins': rad_rad, 
            'dire_fps_rad_wins': rad_dire, 'dire_fps_dire_wins': dire_dire, 'rad_fps_dire_wins': dire_rad, 'rad_wins': rad_wins, 'dire_wins': dire_wins}

jsons_to_upload['fps_dict'] = fps_dict

# --- MATCH LENGTH --- #

print('Creating data transformation for match lengths...')

match_lengths = animajor_matches[['radiant_name', 'dire_name', 'radiant_win', 'duration']]
match_lengths['name'] = match_lengths['radiant_name'] + ' vs ' + match_lengths['dire_name']
match_lengths = match_lengths.sort_values(by = 'duration', ascending = True).reset_index(drop = True)
match_lengths['running_total'] = range(len(match_lengths), 0, -1)

num_list = {}
max_duration = max(df['duration'])
num_list['number_list'] = np.linspace(0, max_duration + 300, max_duration + 301).tolist()
time_list = []

for i in range(len(match_lengths)):
    series = match_lengths.iloc[i]
    duration = series['duration']
    running_total = series['running_total']
    name = series['name']
    time_list.append({'match': name, 'y': int(running_total), 'name': int(duration)})

jsons_to_upload['number_list'] = num_list
jsons_to_upload['time_list'] = time_list

# --- FILE CREATION --- #

print('Converting dataframes to JSON files and saving them...')

for name, df in dfs_to_convert.items():
    print('Writing {} to JSON file...'.format(name))
    df.to_json(save_file_path.format('{}.json'.format(name)), orient = 'records')

print('Saving JSON files...')

for name, data in jsons_to_upload.items():
    file_name = '{}.json'.format(name)

    print('Writing {} to JSON file...'.format(file_name))

    with open(save_file_path.format(file_name), 'w+', encoding = 'utf-8') as f:
        json.dump(data, f, ensure_ascii = False, indent = 4)

print('Number of API requests: {}'.format(api_counter))
print('Cost of API requests: ${}'.format((api_counter / 10000)))