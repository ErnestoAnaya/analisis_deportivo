# -*- coding: utf-8 -*-

import pandas as pd

from xg_model import process_shots, model_xg, calculate_xG
#import matrix_transition_global
import coordenada_zonas

df = pd.read_csv('./../../data/wyscout_tabular/events_World_Cup.csv')
#df = pd.read_csv('./events_World_Cup.csv')

#mirror de los datos coordenadas_zonas

#calculate xG for every shot
shots_model = process_shots(df) #only returns shots
model_summary, b = model_xg(shots_model)

shots_model['xG'] = shots_model.apply(lambda x: calculate_xG(x, b), axis=1) 


# Datos artificiales
#x_coords = 



