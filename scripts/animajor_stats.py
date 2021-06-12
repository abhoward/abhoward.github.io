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

save_file_path = "..\\data\\{}"
dfs_to_convert = {}

api = 'https://api.opendota.com/api'

link = '{}/proMatches?api_key={}'.format(api, API_KEY)

r = requests.get(link)
data = json.loads(r.text)
df = pd.DataFrame(data)

# --- INTITAL DATA PULL --- #

print('Pulling all relevant matches...')

animajor_start = 1622513391

while df[-1::]['start_time'].iloc[0] > animajor_start:
    print('Appending new set of data ending in match_id: {}'.format(df[-1::]['match_id'].iloc[0]))
    temp_link = '{}&less_than_match_id={}'.format(link, df[-1::]['match_id'].iloc[0])
    r = requests.get(temp_link)
    data = json.loads(r.text)
    df = df.append(pd.DataFrame(data))

# --- ANIMAJOR DATA FILTER--- #

# animajor ID
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
data = json.loads(r.text)
heroes_df = pd.DataFrame(data)
heroes = heroes_df[['id', 'localized_name', 'primary_attr']]

# --- HERO PICKS & BANS --- #

print('Creating data transformation for hero picks and bans...')

sql_query = """
SELECT  hero_stats.hero_id,
        heroes.localized_name AS hero_name,
        SUM(CASE 
            WHEN hero_stats.pick = 1 THEN 1
            ELSE 0
        END) AS hero_picks,
        SUM(CASE 
            WHEN hero_stats.pick = 0 THEN 1
            ELSE 0
        END) AS hero_bans
FROM hero_stats
JOIN heroes
ON hero_stats.hero_id = heroes.id
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

# --- TEAM SPECIFIC PICKS & BANS --- # 

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

# --- HERO WINS & LOSSES --- #

print('Creating data transformation for hero wins and losses...')

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

dfs_to_convert['total_hero_wins'] = total_hero_wins

# --- RADIANT VS DIRE PICK ORDERS --- # 

print('Creating data transformation for radiant versus dire pick orders...')

radiant_first_picks_num = len(first_picks[first_picks['team'] == 'Radiant'])
dire_first_picks_num = len(first_picks[first_picks['team'] == 'Dire'])

wins_first_picks_num = len(first_picks[first_picks['team'] == first_picks['winning_team']])
losses_first_picks_num = len(first_picks[first_picks['team'] != first_picks['winning_team']])

rad_rad = len(first_picks[(first_picks['winning_team'] == 'Radiant') & (first_picks['team'] == 'Radiant')])
rad_dire = len(first_picks[(first_picks['winning_team'] == 'Radiant') & (first_picks['team'] == 'Dire')])
dire_dire = len(first_picks[(first_picks['winning_team'] == 'Dire') & (first_picks['team'] == 'Dire')])
dire_rad = len(first_picks[(first_picks['winning_team'] == 'Dire') & (first_picks['team'] == 'Radiant')])

fps_dict = {'rad_fps': radiant_first_picks_num, 'dire_fps': dire_first_picks_num, 'wins_fps': wins_first_picks_num, 'losses_fps': losses_first_picks_num, 'rad_fps_rad_wins': rad_rad, 'dire_fps_rad_wins': rad_dire, 'dire_fps_dire_wins': dire_dire, 'rad_fps_dire_wins': dire_rad}

print('Storing pick order data...')

with open(save_file_path.format('fps_dict.json'), 'w', encoding='utf-8') as f:
    json.dump(fps_dict, f, ensure_ascii=False, indent=4)

# --- MATCH LENGTH --- #

print('Creating data transformation for match lengths...')

match_lengths = animajor_matches[['radiant_name', 'dire_name', 'radiant_win', 'duration']]

match_length = match_lengths.sort_values(by = 'duration', ascending = True) 

match_lengths['name'] = match_lengths['radiant_name'] + ' vs ' + match_lengths['dire_name']
match_lengths['running_total'] = range(len(match_lengths), 0, -1)

max_duration = max(match_lengths['duration'])
xaxis = np.linspace(0, max_duration + 300, max_duration + 301).tolist()
time_list = []

for i in range(len(match_lengths)):
    series = match_lengths.iloc[i]
    duration = series['duration']
    running_total = series['running_total']
    name = series['name']
    time_list.append({'match': name, 'y': int(running_total), 'name': int(duration)})

print('Storing match length data...')

with open(save_file_path.format('time_list.json'), 'w', encoding='utf-8') as f:
    json.dump(time_list, f, ensure_ascii=False, indent=4)

for name, df in dfs_to_convert.items():
    print('Storing {} python data...'.format(name))
    df.to_json(save_file_path.format('{}.json'.format(name)), orient = 'records')