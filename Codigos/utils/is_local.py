# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 13:39:10 2023

@author: santi
"""
import pandas as pd
import json
import os

def extraer_posiciones_events(location):
    with open(location,'r',encoding='utf8') as json_file:
        data=json.load(json_file)
    for parada in data: 
        location=parada.pop("positions")
        parada['x_inicio']=location[0]['x']
        parada['y_inicio']=location[0]['y']
        if len(location)>1:
            parada['x_fin']=location[1]['x']
            parada['y_fin']=location[1]['y']
        if 'tags' in parada.keys():
            etiquetas=parada.pop("tags")
            for i in range(0,len(etiquetas)):
                tags_ind='tag_'+str(i)
                parada[tags_ind]=etiquetas[i]['id']
    df=pd.DataFrame(data)
    return df

#event_names = pd.read_csv("eventid2name.csv") #id de eventos a nombres de eventos
#tag_names = pd.read_csv("tags2name.csv") #tags de eventos a nombres de tags

#df = extraer_posiciones_events('./../../data/events_World_Cup.json')

#%% Extraer Localia

def datos_partidos(location):
    partidos=pd.read_json(location)
    return partidos

def datos_equipo(location):
    equipos=pd.read_json(location)
    return equipos

# partidos = datos_partidos(r".\..\..\data\matches_World_Cup.json")
# teams = datos_partidos(r".\..\..\data\teams.json")

def extraer_locales(partidos, equipos):
    aux = partidos.copy()
    
    aux.label = (aux
                 .label
                 .str
                 .replace('([a-zA-Z0-9& ]+)( - )([a-zA-Z0-9& ]+)(, )(.+)',
                          '\\1,\\3', regex = True)
                 .str
                 .split(','))
    
    dict_equipos = (teams[['wyId','name']]
            .set_index('name').to_dict()) 
    
    aux[['local','visita']] = pd.DataFrame(aux.label.tolist(), index= aux.index)
    
    aux = aux[['wyId','local','visita']]
    
    aux2 = equipos[['wyId','name']]
    
    aux['local'] = aux['local'].map(aux2.set_index('name')['wyId'])
    
    aux['visita'] = aux['visita'].map(aux2.set_index('name')['wyId'])
    
    aux = aux.set_index('wyId').to_dict()
    
    return aux

#localia = extraer_locales(partidos, teams)

def asignar_localia(match_id, team_id, localia):
    local = localia['local'][match_id]
    if local == team_id:
        return 1
    else:
        return 0
    
    return None

#Uso:
# df['is_local'] = df.apply(lambda x: asignar_localia(x.matchId,x.teamId, localia),
#                           axis=1)

    