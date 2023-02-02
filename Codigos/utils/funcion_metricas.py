# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 20:27:51 2023

@author: santi
"""
#Instalaciones
# !pip install shapely

import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

df_events = None #Es el dataframe con los eventos

def inTheBox(x,y):
    point = Point(x,y)
    area = Polygon([(84, 19), (100, 19), (84, 81), (100, 81)])
    
    return int(area.contains(point))

def toTheWing(x,y):
    point = Point(x,y)
    area1 = Polygon([(0, 0), (0, 19), (100, 0), (100, 19)])
    area2 = Polygon([(0, 100), (0, 81), (100, 81), (100, 100)])
    
    return int((area1.contains(point)) | (area2.contains(point)))
    
def deepProgression(x0,y0, x1, y1):
    start = Point(x0,y0)
    end = Point(x1,y1)
    
    final_third = Polygon([(66,0),(66,100),(100,0),(100,100)])
    
    if ~final_third.contains(start):
        return int(final_third.contains(end))

def addLocationConditions(df):
    #Toma un buen rato esta. Como 1 minuto x cada 100k datos
    df['end_in_box'] = df.apply(lambda x: inTheBox(x.x_fin,x.y_fin), axis =1)
    df['start_in_box'] = df.apply(lambda x: inTheBox(x.x_inicio,x.y_inicio), axis =1)
    df['to_the_wing'] = df.apply(lambda x: toTheWing(x.x_fin,x.y_fin), axis =1)
    df['deep_progression'] = df.apply(lambda x: deepProgression(x.x_inicio,x.y_inicio,
                                                                x.x_fin,x.y_fin), axis =1)
    return df

addLocationConditions(df_events)

def metricas(df_events):
    
    df = df_events.copy()
    aux = pd.DataFrame()
    
    df["goal_scored"] = df.loc[:,"tag_0":"tag_5"].eq(101).sum(axis=1)
    df["goal_assisted"] = df.loc[:,"tag_0":"tag_5"].eq(301).sum(axis=1)
    df['won'] = df.loc[:,"tag_0":"tag_5"].eq(703).sum(axis=1)
    df['carry'] = (df[df['subEventId'] == 70]
                     .loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)).fillna(0)
    
    df['carry'].fillna(0, inplace = True)
    
    df['interception'] = ((df.loc[:,"tag_0":"tag_5"].eq(1401).sum(axis=1)) *
                         (df.loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)))
    
    df['tackle'] = ((df.loc[:,"tag_0":"tag_5"].eq(1601).sum(axis=1)) *
                         (df.loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)))
    
    df['shot'] = df.loc[:, "subEventId":"id"].eq(100).sum(axis=1)
    
    df['shot_from_outside_box'] = ((df.shot) *
                                   (df.start_in_box))
    
    
    df['succ_cross'] = ((df.loc[:, "subEventId":"id"].eq(80).sum(axis=1)) *
                        (df.loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)))
    
    df['unsucc_cross'] = ((df.loc[:, "subEventId":"id"].eq(80).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(1802).sum(axis=1)))
    
    df['through_balls'] = ((df.loc[:, "eventId":"subEventName"].eq(8).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(901).sum(axis=1)))
    
    df['complete_pass'] = ((df.loc[:, "eventId":"subEventName"].eq(8).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)))
    
    df['pass_into_the_box'] = ((df.complete_pass) *
                               (df.end_in_box))
    
    df['incomplete_pass'] = ((df.loc[:, "eventId":"subEventName"].eq(8).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(1802).sum(axis=1)))
    
    df['key_pass'] = ((df.loc[:, "eventId":"subEventName"].eq(8).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(1801).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(302).sum(axis=1)))
    
    df['yellow_card'] = df.loc[:,"tag_0":"tag_5"].eq(1702).sum(axis=1)
    df['red_card'] = df.loc[:,"tag_0":"tag_5"].eq(1701).sum(axis=1)
    df['second_yellow_card'] = df.loc[:,"tag_0":"tag_5"].eq(1703).sum(axis=1)
    
    df['Foul'] = df.loc[:, "subEventId":"id"].eq(20).sum(axis=1)
    df['Violent_Foul'] = df.loc[:, "subEventId":"id"].eq(27).sum(axis=1)
    
    df['Headers'] = ((df.loc[:, "subEventId":"id"].eq(100).sum(axis=1)) *
                          (df.loc[:,"tag_0":"tag_5"].eq(403).sum(axis=1)))
    
    aux[['playerId','goals']] = (df[~df['subEventName'].isin(["Reflexes", "Save attempt"]) &
                                    (~(df['matchPeriod'] == 'P'))]
                                 .groupby('playerId',as_index = False)['goal_scored']
                                 .sum())
    aux = ((aux
           .merge(df.groupby('playerId', as_index = False)['goal_assisted'].sum(),
                  left_on=('playerId'),
                  right_on=('playerId')))
           .rename(columns = {'goals_assisted':'assists'}))
    
    
    aux = ((aux
           .merge(df[df['subEventId']==100]
                    .groupby('playerId', as_index = False)['subEventId'].count(),
                  left_on=('playerId'),
                  right_on=('playerId')))
           .rename(columns = {'subEventId':'nfk_np_shots'}))
    
    aux = ((aux
            .merge(df.groupby('playerId', as_index = False)['x_inicio'].mean(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'x_inicio':'avg_pos_x'}))
    
    aux = ((aux
            .merge(df.groupby('playerId', as_index = False)['y_inicio'].mean(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'y_inicio':'avg_pos_y'}))
    
    
    aux = ((aux
            .merge(df[(df['subEventId'] == 10) & (df['won'] == 1)]
                      .groupby('playerId')['won'].sum(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'won':'aerial_duels_won'}))
    
    aux = ((aux
            .merge(df[(df['subEventId'] == 12) & (df['won'] == 1)]
                      .groupby('playerId')['won'].sum(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'won':'Ground defending duel_won'}))
    
    aux = ((aux
            .merge(df[(df['subEventId'] == 11) & (df['won'] == 1)]
                      .groupby('playerId')['won'].sum(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'won':'Ground attacking duel_won'}))
    
    aux = ((aux
            .merge(df.groupby('playerId')['matchId'].nunique(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'matchId':'matches'}))
    
    events = ['Carry','interception', 'tackle', 'shot', 'succ_cross', 'unsucc_cross',
              'through_balls', 'complete_pass', 'incomplete_pass', 'key_pass',
              'yellow_card', 'red_card', 'second_yellow_card',
              'Violent_Foul', 'Foul', 'Headers', 'pass_into_the_box',
              'shot_from_outside_box', 'deep_progression', 'to_the_wing']
    
    for e in events:
        aux = (aux.merge(df
                         .groupby('playerId')[e].sum(),
                         left_on=('playerId'),
                         right_on=('playerId')))

    return aux