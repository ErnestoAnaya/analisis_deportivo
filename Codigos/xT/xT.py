# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xg_model import process_shots, model_xg, calculate_xG
#import matrix_transition_global
import coordenadas_zonas as cz

import seaborn as sns
import matplotlib.pyplot as plt

#df = pd.read_csv('./../../data/wyscout_tabular/events_World_Cup.csv')
df = cz.extraer_posiciones_events('./../../data/events_World_Cup.json')

df = cz.normalizarDimensiones(df)


#calculate xG for every shot
shots_model = process_shots(df) #only returns shots
model_summary, b = model_xg(shots_model)

shots_model['xG'] = shots_model.apply(lambda x: calculate_xG(x, b), axis=1) 


shots_model['zonaInicio'] = shots_model.apply(lambda df: cz.coordenadas_to_zonas(df['X'],df['Y']),
                                  axis=1)

shots_model.hist('zonaInicio')

#
xg_zonas = shots_model.groupby(by='zonaInicio').mean().reset_index()

zonas = np.arange(1, 193, 1)
df_zonas = pd.DataFrame(zonas, columns=['zonaInicio'])

xg_zonas = pd.merge(df_zonas, xg_zonas[['zonaInicio', 'xG']], how = 'outer', on = 'zonaInicio').fillna(0)


