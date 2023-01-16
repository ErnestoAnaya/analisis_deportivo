import pandas as pd
import numpy as np


def posession_change(df):
    '''
    checa si en la acción hubo un cambio de posesión. Hay un cambio de posesión
    si el evento pasado es de un equipo diferente. Hay ciertos eventos que no
    se toman en cuenta
    
    match always in descending ordered in descending order (first play goes at the top)
    '''
    #acciones que no se toman en cuenta
    events = [1, 5]
    #y duelos perdidos
    df_extra = df[df['eventId'].isin(events)]
    df_events = df[df['eventId'].isin(events) == False]
    
    df_events['past_team'] = df_events['teamId'].shift(1)
    df_events['past_time'] = df_events['eventSec'].shift(1)
    
    df_extra['posession_change'] = 0
    df_events['posession_change'] = 0
    condition = (df_events['past_team'] != df_events['teamId']) & (df_events['past_time'] < df_events['eventSec'])
    
    df_events['posession_change'] = np.where(condition, 1, df_events['posession_change'])
    
    df_res = pd.concat([df_extra, df_events])
    df_res = df_res.sort_values(by=['matchId', 'matchPeriod', 'eventSec'])
    
    return df_res['posession_change']


def calc_complex_feat(df):
    '''
    calcula la distancia y ángulo del evento y la portería,
    tiempo transcurrido, distancia entre donde empieza y terminan los eventos, 
    si hubo cambio de posesión y tiempo entre eventos
    
    '''
    comp_feat_df = pd.DataFrame()
    
    comp_feat_df['time_diff'] = df['eventSec'].shift(-1) - df['eventSec'] 
    comp_feat_df.loc[comp_feat_df['time_diff'] < 0, 'time_diff'] = 0 
    #es si fue la última acción antes de medio tiempo o tiempo completo
    
    comp_feat_df['goal_dist'] = np.sqrt( (df['x_inicio']-110)**2 +
                                         (df['y_inicio']-35)**2
                                        )
    
    x = 110 - df['x_inicio']
    y1 = np.abs(35+7.32/2 - df['y_inicio'])
    y2 = np.abs(35-7.32/2 - df['y_inicio'])
    
    l1 = np.sqrt(x**2 + y1**2)
    l2 = np.sqrt(x**2 + y2**2)
    l3 = 7.32
    
    angle = np.arccos( (l1**2 + l2**2 - l3**2)/(2*l1*l2) )
    
    comp_feat_df['goal_angle'] = angle
    comp_feat_df['goal_angle'] = np.where(angle<0, np.pi+angle, angle)
    
    comp_feat_df['act_dist'] = np.sqrt((df['x_inicio'] - df['x_fin'])**2 + 
                                       (df['x_fin'] - df['x_fin'])**2) 
    # hay eventos medio raros
    comp_feat_df['matchId'] = df['matchId']
    comp_feat_df['matchPeriod'] = df['matchPeriod']
    comp_feat_df['eventSec'] = df['eventSec']
    comp_feat_df['eventId'] = df['eventId']
    comp_feat_df['teamId'] = df['teamId']
    
    
    comp_feat_df = comp_feat_df.sort_values(by = ['matchId', 'matchPeriod', 'eventSec'])
    
    comp_feat_df['pos_change'] = posession_change(comp_feat_df) #ver que opciones se ignoran
    
    comp_feat_df = comp_feat_df.drop(columns = ['matchId', 'matchPeriod', 'eventSec', 'eventId', 'teamId'])
    
    
    return comp_feat_df