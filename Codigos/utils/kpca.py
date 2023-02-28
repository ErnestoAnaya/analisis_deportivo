# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 17:48:17 2023

@author: santi
"""

#!pip install shapely

import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn import mixture 
import umap.umap_ as umap
from sklearn.model_selection import train_test_split, cross_val_score


#%%Funciones
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
           .rename(columns = {'goal_assisted':'assists'}))
    
    
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
           .rename(columns = {'won':'Ground_defending_duel_won'}))
    
    aux = ((aux
            .merge(df[(df['subEventId'] == 11) & (df['won'] == 1)]
                      .groupby('playerId')['won'].sum(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'won':'Ground_attacking_duel_won'}))
    
    aux = ((aux
            .merge(df.groupby('playerId')['matchId'].nunique(),
                   left_on=('playerId'),
                   right_on=('playerId')))
           .rename(columns = {'matchId':'matches'}))
    
    events = ['carry','interception', 'tackle', 'shot', 'succ_cross', 'unsucc_cross',
              'through_balls', 'complete_pass', 'incomplete_pass', 'key_pass',
              'yellow_card', 'red_card', 'second_yellow_card',
              'Violent_Foul', 'Foul', 'Headers', 'pass_into_the_box',
              'shot_from_outside_box', 'deep_progression', 'to_the_wing']
    
    for e in events:
        aux = (aux.merge(df
                         .groupby('playerId')[e].sum(),
                         left_on=('playerId'),
                         right_on=('playerId')))
        
    #Add ratios and rates
    aux['shot_conversion_rate'] = aux['goals']/(aux['shot'])
    aux['assists_convertion_rate'] = aux['assists']/aux['complete_pass']
    aux['pass_completion_rate'] = aux['complete_pass'] / (aux['complete_pass'] +
                                                          aux['incomplete_pass'])
    aux['off_def_duel_ratio'] = (aux['Ground_attacking_duel_won'] /
                                 aux['Ground_defending_duel_won'])
    aux['pass_cross_ratio'] = aux['complete_pass'] / (aux['succ_cross'] +1)
    aux['key_pass_per_pass'] = aux['key_pass'] / aux['complete_pass']
    aux['shot_per_pass'] = aux['shot'] / aux['complete_pass']

    return aux

def clusteringPlayers(df, stats, n, comps, plot = True, clusterType = 'GMM', componentType = 'PCA'):
    
    aux = df.copy()
    
    res = df.copy()
    
    res = res.fillna(0)
    
    res = res[stats]
    
    
    if componentType == 'PCA':
        scaler = StandardScaler()
        res_std = scaler.fit_transform(res)
        
        pca = PCA(n_components = comps)
        pca.fit(res_std)
        
        res = pca.transform(res_std)
        
        kmeans_pca = KMeans(n_clusters= n, init = 'k-means++',random_state=42)
    
        kmeans_pca.fit(res)
        
        
        df_segm_pca_kmeans = pd.concat([aux.reset_index(drop=True),pd.DataFrame(res)],axis=1)
        
        df_segm_pca_kmeans.columns.values[-2:] = ['Component 1', 'Component 2']
    else:
        trans = umap.UMAP(n_neighbors=2, random_state=42).fit(res)
        df_segm_pca_kmeans = pd.DataFrame
        df_segm_pca_kmeans['Component 1'] = trans.embedding_[:, 0]
        df_segm_pca_kmeans['Component 2'] = trans.embedding_[:, 1]
        
    
    if clusterType == 'GMM':
        X = df_segm_pca_kmeans[['Component 1', 'Component 2']]
        gmm = mixture.GaussianMixture(n_components=2, covariance_type='full').fit(X)
        labels = gmm.predict(X)
        plt.scatter(X['Component 1'], X['Component 2'], c=labels, s=40, cmap='viridis')
        
        return True
    else:
        df_segm_pca_kmeans['class'] = kmeans_pca.labels_
    
        if plot:    
            print('Hola')
            x = df_segm_pca_kmeans['Component 1']
            y = df_segm_pca_kmeans['Component 2']
            
            # sns.scatterplot(data=df_segm_pca_kmeans,
            #                 x = 'Component 1',
            #                 y = 'Component 2',
            #                 hue='class')
    
            sns.scatterplot(x,y,hue=df_segm_pca_kmeans['class'])
            
        return df_segm_pca_kmeans

def cluster(df, stats, n, comps, plot = True, clusterType = 'GMM', componentType = 'PCA'):
    
    res = clusteringPlayers(df, stats, n, comps, plot, clusterType, componentType)
    
    return res

def jugadoresDF():
    
    with open(r"D:\ExperimentosDatosPersonales\FerEsponda\Wyscout\players.json") as f:
        jugadores = json.load(f)
        
    jugadores = pd.json_normalize(jugadores, sep = "_")
        
    jugadores['Name'] = jugadores['firstName'] + ' ' + jugadores['lastName']
    
    jugadores = jugadores[['Name','wyId','role_name', 'role_code2','role_code3']]
    
    jugadores.rename(columns={"wyId": "playerId"}, inplace=True)
    
    return jugadores



#%%
import os
os.chdir(r"C:\Users\santi\Desktop\ITAM\SportsLab\analisis_deportivo\Codigos\xT")

#Generacion de Metricas
event_names = pd.read_csv("eventid2name.csv") #id de eventos a nombres de eventos
tag_names = pd.read_csv("tags2name.csv")

df = extraer_posiciones_events('./../../data/events_England.json')

df = addLocationConditions(df)

player_season = metricas(df)

try:
    player_season = player_season[player_season['playerId']!=0].fillna(0)
except:
    print("no playerId = 0")


jugadores = jugadoresDF()

x = player_season.columns

df1 = cluster(player_season,x[2:],2,2,True,'GMM','no')

#Ahorita olvidate de esto
df1 = df1[['Player','Pos','class']]


res = (pd.merge(jugadores,df1,
                on=['playerId'],how='right'))[['Name', 'role_name', 'class']]




x = df1[df1['class'] == 0]['Pos'] 
y = df1[df1['class'] == 1]['Pos'] 
z = df1[df1['class'] == 2]['Pos'] 
xa = df1[df1['class'] == 3]['Pos'] 
bins = len(y.unique())

plt.hist([x, y, z,xa], bins, label=['0', '1', '2','xa'])
plt.legend(loc='upper right')
plt.show()


    
