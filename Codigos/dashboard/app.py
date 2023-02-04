from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv('./Codigos/vaep/xgboost_vaep.csv')


#
# dashboard 1
#

# --- players ---

#posición
#peso, edad, país, altura
#equipo

# --- xT ---
# --- VAEP ---
# --- Métricas --- (de wyscout)
#   hacer csv de agregados

#
# dashboard 2
#

# cosas de VAEP y de wyscout
# - wyscout para mapas


fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])














if __name__ == '__main__':
    app.run_server(debug=True)