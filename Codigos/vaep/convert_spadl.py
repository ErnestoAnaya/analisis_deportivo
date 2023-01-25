import pandas as pd
import numpy as np



'''
Función principal: convert_spadl

funciones extra:
    - flip coords
    - 

        
'''

def check_coords(df):
    '''
    Checa si las coordenadas están volteadas, si si lo están voltea las coordenadas
    - las coordenadas de un equipo siempre van a la misma dirección
    
    se usan los eventos de porteros y tiros para cambiar las coordenadas
    '''
    
    return



def was_succesful(df):
    '''
    dado los eventos, ve si  fueron exitosos o no
    
    esto se determina de acuerdo con los tags: 
    failed: blocked, interception, missed_ball, lost, dangerous ball lost
    - puede que estos tags dependan de 
    
    parece que solo aparecen en tag_0, pero por si acaso se busca en los 6
    '''
    
    fail_tags = [2101, 701, 1302, 1401, 2001]
    tags = ['tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']
    
    df['succesful'] = 1
    
    for tag in tags:
        df.loc[df[tag].isin(fail_tags), 'succesful'] = 0
    
    return df['succesful']



def get_body_part(df):
    '''
    calcula con que parte del cuerpo se hizo la acción
    
    si no se detecta, se 
    '''
    
    df['body_part'] = 'right'
    tags = ['tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']
    
    for tag in tags:
        
        df.loc[df[tag] == 401, 'body_part'] = 'left'
        df.loc[df[tag] == 403, 'body_part'] = 'head_body'
        
    return df['body_part']
        


def convert_spadl(df):
    '''
    recibe los datos tabulares de wyscout y los convierte en 
    '''
    spadl_df = pd.DataFrame()
    
    spadl_df['start_time'] = df['eventSec']
    
    #el shift debe tener un 
    spadl_df['end_time'] = df['eventSec'].shift(-1) #hay que hacer un shift  
    spadl_df['start_x'] = df['x_inicio']
    spadl_df['start_y'] = df['y_inicio']
    spadl_df['end_x'] = df['x_fin']
    spadl_df['end_y'] = df['y_fin']
    spadl_df['player'] = df['playerId']
    spadl_df['team'] = df['teamId']
    spadl_df['action_type'] = df['eventName'] 
    #$spad_df['matchId']
    
    spadl_df['body_part'] = get_body_part(df)
    spadl_df['result'] = was_succesful(df)
    
    spadl_df = spadl_df[spadl_df['action_type'] != 'Save attempt']
    
    return spadl_df



def process_spadl(spadl_df):
    '''
    del df en formato SPADL, aqui se toman en cuenta los que se usan para entrenar
    el modelo. 
    BORRARRRRRR
    '''
    proc_spadl_df = pd.DataFrame()
    
    proc_spadl_df['action_type'] = spadl_df['action_type']
    proc_spadl_df['result'] = spadl_df['result']
    proc_spadl_df['body_part'] = spadl_df['body_part']
    proc_spadl_df['start_x'] = spadl_df['start_x']
    proc_spadl_df['start_y'] = spadl_df['start_y']
    proc_spadl_df['end_x'] = spadl_df['end_x']
    proc_spadl_df['end_y'] = spadl_df['end_y']
    proc_spadl_df['start_time'] = spadl_df['start_time']
    
    return proc_spadl_df
