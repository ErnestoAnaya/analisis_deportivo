from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc


app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

#df_vaep = pd.read_csv('./Codigos/vaep/xgboost_vaep.csv')
df_players = pd.read_csv('./Codigos/dashboard/player_info_dash.csv')

#
# dashboard 1
#

roles = df_players.role.unique()


# --- players ---

#posición
#peso, edad, país, altura
#equipo




#
# dashboard 2
#

# cosas de VAEP y de wyscout
# - wyscout para mapas

# --- xT ---
# --- VAEP ---
# --- Métricas --- (de wyscout)
#   hacer csv de agregados


#fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(

    html.Div([
        html.H1('Player Search'),
        html.Br(),
        html.Br(),
        
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.RangeSlider(15,35,1,
                                   id='slider_age',
                                   marks={i: '{}'.format(5 ** i) for i in range(4)},
                                   #value=35,
                                   updatemode="drag"
                            ),
                        dcc.RangeSlider(15,60,1,
                                   id='slider_price',
                                   marks={i: '{}'.format(5 ** i) for i in range(4)},
                                   #value=35,
                                   updatemode="drag"
                            )
                        ])
                    ]),
                dbc.Col([
                    html.H5("OTROS FILTROS")
                    ])
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.H5("Nombre", style={'text-align': 'center','fontWeight': 'bold'}),
                    html.H3(id='name', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                    ]),
                dbc.Col([
                    html.Br(),
                    html.H5("Edad", style={'text-align': 'center','fontWeight': 'bold'}),
                    html.H3(id='age', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                    ]),
                dbc.Col([
                    html.Br(),
                    html.H5("Equipo", style={'text-align': 'center','fontWeight': 'bold'}),
                    html.H3(id='team', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                    ]),
                dbc.Col([
                    html.Br(),
                    html.H5("xT / VAEP", style={'text-align': 'center','fontWeight': 'bold'}),
                    html.H3(id='xt_vaep', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                    ]),
                dbc.Col([
                    html.Br(),
                    html.H5("Metricas", style={'text-align': 'center','fontWeight': 'bold'}),
                    html.H3(id='metrics', style={'text-align': 'center','fontWeight': 'bold', 'color': '#9f9f9f'})
                    ])
                
                ])
            ]),
        html.Br(),
        html.Br(),
        html.Div(children=
        '''
            Adv Stats
        ''')
        ])
                 )

@app.callback(
    [Output('name', 'children'),
     Output('age', 'children'),
     Output('team', 'children'),
     Output('xt_vaep', 'children'),
     Output('metrics', 'children'),
     ],
    [Input('slider_age', 'value'),
     Input('slider_price', 'value')]
)

def update_player(age, price):
    age = age[0]
    player = df_players[df_players.age == age]
    
    p_name = player.firstName.iloc[0]
    p_age = player.age.iloc[0]
    p_team = player.officialName.iloc[0]
    p_xt = player.goals.iloc[0]
    p_met = player.assists.iloc[0]
    
    
    return p_name, p_age, p_team, p_xt, p_met
                 



if __name__ == '__main__':
    app.run_server(debug=True)