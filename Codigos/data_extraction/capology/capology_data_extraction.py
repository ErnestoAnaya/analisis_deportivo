#lxml is also needed

# Python ≥3.5 (ideally)
import platform 
import sys
assert sys.version_info >= (3, 5)
import json
import glob
import random
import time
import pandas as pd
import os
from selenium import webdriver

'''
cosas a considerar: 
    - scrape_capology_season_prev() se puede mejorar. se puede hacer header = 1
      y team se puede modificar antes de asignarlo al df (sospecho que es un poquito m{as rápido})
    - las operaciones hechas en pandas seguro se pueden hacer de forma más ordenada
      y sin tantos "df intermedios"
'''

# Python / module versions used here for reference
print('Python: {}'.format(platform.python_version()))
print('pandas: {}'.format(pd.__version__))

#load dictionary 
f = open('./../../data_extraction/cpology/competitions_teams.json')
comps_dict = json.load(f)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Set up initial paths to subfolders
base_dir = os.path.join('..', '..')
base_dir = os.path.join(base_dir, '..')
data_dir = os.path.join(base_dir, 'data')
data_dir_capology = os.path.join(base_dir, 'data', 'capology')

# Define function for scraping a defined season of Capology data
def scrape_capology_season_prev(lst_teams, season, comp):
    '''
    given the list of teams participating in one season of a given competition.
    It returns the salary table from acpology from said team.

    '''
    print(f'Scraping for {comp} for the {season} season has now started...')  

    ## Create empty list for DataFrame
    dfs_players = []

    for team in lst_teams:
        if not os.path.exists(os.path.join(data_dir_capology + f'/raw/{comp}/{season}/{team}_{comp}_{season}.csv')):
            ##Creo que desde aquí se puede modificar team y league
            
            url = f'https://www.capology.com/club/{team}/salaries/{season}/'
            print(f'Scraping {team} for the {season} season')
            print(url)
            wd = webdriver.Chrome('chromedriver', options=options)
            wd.get(url)
            html = wd.page_source
            random_lb = random.randint(5, 7)
            random_ub = random.randint(10, 14)
            sleep_time = random.randint(random_lb, random_ub)
            time.sleep(sleep_time)
            html = wd.page_source
            df = pd.read_html(html, header=0)#[1] ## Creo que con poner header = 1 se puede evitar 2 lineas
            
            if len(df)>1:
                df = df[1]
            else:
                df = df[0]

            ### Data Engineering
            df_test = df.copy()
            df_test = df_test.rename(columns=df_test.iloc[0])
            df_test = df_test.rename(columns={df_test.columns[6]: 'Country'})

            df_test = df_test.iloc[1: , :]
            df_test = df_test[:-1]
            df_test['Team'] = team
            df_test['Team'] = df_test['Team'].str.replace('-', ' ').str.title().str.replace('Fc', 'FC').str.replace('Ac', 'AC')
            df_test['League'] = comp
            df_test['League'] = df_test['League'].str.replace('-', ' ').str.title()
            df_test['Season'] = season
            print(f'Saving DataFrame of {team} for the {season} season')

            ### Save to CSV
            df_test.to_csv(data_dir_capology + f'/raw/{comp}/{season}/{team}_{comp}_{season}.csv')

            ### Append to joint DataFrame
            dfs_players.append(df_test)

        else:
            df_test = pd.read_csv(data_dir_capology + f'/raw/{comp}/{season}/{team}_{comp}_{season}.csv', index_col=None, header=0)
            print(f'{team} already scraped and saved for the {season} season')

            ### Append to joint DataFrame
            dfs_players.append(df_test)

    df_players_all = pd.concat(dfs_players)

    ## Engineer unified data
    df_players_all['Team'] = df_players_all['Team'].str.replace('-', ' ').str.title().str.replace('Fc', 'FC')
    df_players_all['League'] = df_players_all['League'].str.replace('-', ' ').str.title()

    df_players_all.to_csv(data_dir_capology + f'/raw/{comp}/{season}/all_{comp}_{season}.csv')

    print(f'Scraping for {comp} for the {season} season is now complete')

    return df_players_all


def make_league_dirs(leagues):
    '''
    Given the list of leagues, a folder is made for each league
    '''
    
    for folder in leagues:
        path = os.path.join(data_dir_capology, 'raw', folder)
        if not os.path.exists(path):
            os.mkdir(path)


#download data
def download_data(comps_dict):
    '''
    ejecutar scrape_capology_season_prev(teams, season, league) para 
    todos los datos que tenemos
    '''
    for league in list(comps_dict.keys()):
        seasons = list(comps_dict[league].keys())
        
        for season in seasons:
            teams = comps_dict[league][season]
            
            if ( (season == '2018-2019') & (league == 'la-liga') ):
                if('leganes' in teams):
                    teams.remove('leganes')
                
            df_players_all = scrape_capology_season_prev(teams, season, league)
            
    return df_players_all


#unify data
def unify_data():
    '''
    Juntar todos los archivos y guardarlos
    '''
    
    # Show files in directory
    all_files = glob.glob(os.path.join(data_dir_capology + '/raw/*/*/all_*.csv'))
    all_files
    
    lst_all_teams = []    # pd.concat takes a list of DataFrames as an argument
    
    for filename in all_files:
        df_temp = pd.read_csv(filename, index_col=None, header=0)
        lst_all_teams.append(df_temp)
    
    df_players_all = pd.concat(lst_all_teams, axis=0, ignore_index=True)
    
    # Engineer unified data
    
    df_players_all['Team'] = df_players_all['Team'].str.replace('-', ' ').str.title().str.replace('Fc', 'FC')
    df_players_all['League'] = df_players_all['League'].str.replace('-', ' ').str.title()
    
    
    ## Drop duplicates
    df_players_all = df_players_all.drop_duplicates()
    
    df_players_all.to_csv(os.path.join(data_dir_capology, 'all_players_2016_2021.csv'))


#download, save and unify data
make_league_dirs(['bundesliga', 'la-liga', 'ligue-1', 'premier-league', 'serie-a'])

download_data(comps_dict)

unify_data()
