from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

from dotenv import load_dotenv
import openai
import os 

import random

app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

load_dotenv()
openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_API_KEY']


df = pd.read_csv('./../../data/wyscout_tabular/germany.csv')
teams = pd.read_json('./../../data/wyscout/Teams/teams.json')
matches = pd.read_json('./../../data/wyscout/Matches/matches_Germany.json')
players = pd.read_json('./../../data/wyscout/players.json')

df = df.merge(teams, left_on='teamId', right_on='wyId', how='left')
df  = df.merge(players, left_on='playerId', right_on ='wyId', how='left')

teams_list = list(df['name'].unique()) #list(teams['name'].unique())




def get_gpt3_completion(prompt, engine="davinci", **kwargs):
    engines = {
        'davinci': 'text-davinci-002',
        'curie': 'text-curie-001',
        'babbage': 'text-babbage-001',
        'ada': 'text-ada-001'
    }
    
    engine = engines.get(engine, engine)
    
    default = dict(
        max_tokens=3500 if engine == 'text-davinci-002' else 1500,
        stop=" END" if engine not in engines else None
    )
    
    final_kwargs = {**default, **kwargs}
    response = openai.Completion.create(
        prompt=prompt,
        engine=engine,
        **final_kwargs
    )
    
    answer = response['choices'][0]['text']
    return answer



def create_prompt(event):
    
    team = str(event['name']).encode('utf-8').decode('unicode_escape')
    player = str(event['shortName']).encode('utf-8').decode('unicode_escape')
    event_type = event['eventName']
    
    game_sec = int(event['eventSec']%60)
    game_min = int(event['eventSec']/60)
    half = event['matchPeriod']
    
    if game_sec < 10:
        game_sec = "0"+str(game_sec)
    if half == '2H':
        game_min +=45
    if game_min < 10:
        game_min = "0"+str(game_min)
        
    prompt = f"""Data of the event:
    - player: {player}
    - team: {team}
    - action: {event_type}
    - game time: {game_min}:{game_sec}
    
    Rewrite the event as a tweet
    """
        
    return prompt



app.layout = html.Div(

    html.Div([
        html.Br(),
        html.Br(),
        html.H1('Player Search'),
        html.Br(),
        html.Br(),
        
        html.Div([
            dbc.Row([
                dbc.Col([
                    #col 1
                    html.Div([
                        dcc.Dropdown(teams_list, teams_list[0], id='teams-ddown'),
                        html.Br(),
                        
                        html.H3("Datos crudos"),
                        html.H5(id='event-data', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                        ])
                    ]),
                
                dbc.Col([
                    #col 2
                    
                    #output completo
                    html.Br(),
                    html.Br(),
                    html.H3("Datos procesados"),
                    html.H5(id='prompt-output', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                    ])
                ]),
            html.Br(),
            dbc.Row([
                
                ])
            ]),
        html.Br(),
        html.Br(),
        html.Div(children=
        '''
        
        ''')
        ])
                 )


@app.callback(
    [Output('event-data', 'children'),
     Output('prompt-output', 'children'),
     ],
    Input('teams-ddown', 'value')
)

def update_player(team):
    df_team = df[df['name'] == team]
    index = random.randint(0, df_team.shape[0]-1)
    
    event = df_team.iloc[index]
    
    prompt = create_prompt(event)
    comp = get_gpt3_completion(prompt)
    
    
    
    return event.to_string(), comp
                 



if __name__ == '__main__':
    app.run_server(debug=True)











