import numpy as np
from collections import Counter
import pandas as pd
import json
import math 
from mplsoccer.pitch import Pitch, VerticalPitch
import matplotlib.pyplot as plt

def find_index(arr, K):
    n = len(arr)
    start = 0
    end = n - 1
 
    while start<= end:
        mid =(start + end)//2
        if arr[mid] == K:
            return mid
        elif arr[mid] < K:
            start = mid + 1
        else:
            end = mid-1
    return end + 1

def coordenadas_to_zonas(x, y, len_pitch=112, height_pitch=72) -> int:
    #Pasa de coordenadas x,y a zona del 1 al 192
    #La y se toma como si fuera de arriba hacia abajo y la x de izquierda a derecha
    div_x = np.arange(len_pitch/16, len_pitch*17/16, len_pitch/16)
    div_y = np.arange(height_pitch/12, height_pitch*13/12, height_pitch/12)
    x_zone = find_index(div_x, x)
    y_zone = find_index(div_y, y)
    row = np.arange(1, 192, 12)
    mat = np.array([row+i for i in range(12)])

    return mat[y_zone][x_zone]   

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

def normalizarDimensiones(df,tam=[112,72]):
    '''
    Esta función normaliza los valores de las columnas de coordenadas y regresa un
    DataFrame nuevo con los valores entre [0:tam] sin alterar los valores originales.

    Args:
        df (TYPE): DataFrame con los datos originales. No será alterado.
        tam (NUMERIC, optional): Valores normalizados
                                Defaults to [110,70].

    Returns:
        df1 (DATAFRAME): Nuevo dataframe con los valores de las columnas normalizados entre
                        0 y tam.

    '''
    df1 = df.copy()
    df1[['x_inicio','x_fin']] = (df1[['x_inicio','x_fin']]
                                 .apply(lambda x: tam[0]*(x-x.min())/(x.max()-x.min())))
    df1[['y_inicio','y_fin']] = (df1[['y_inicio','y_fin']]
                                 .apply(lambda x: tam[1]*(x-x.min())/(x.max()-x.min())))
    
    return df1

def probabilityMatrixes(df, visualize = True):
    #Obtenemos todos los tiros
    shotZones = df[(df['subEventName'] == 'Shot') |
                    (df['subEventName'] == 'Free kick shot')]['zonaInicio']
    
    #Obtenemos todas las acciones en esa zona que no son tiro
    # Tomamos Corner, Free Kick, Free Kick Cross, Goal Kick, Cross
    # Head Pass, High Pass, Launch, Simple pass, Smart pass, Acceleration
    moves = ['Corner', 'Free Kick', 'Free Kick Cross', 'Goal Kick', 'Cross',
             'Head Pass','High Pass', 'Launch', 'Simple pass',
             'Smart pass', 'Acceleration']
    
    moveZones = df[df['subEventName'].isin(moves)]['zonaInicio']
    
    #Apariciones en cada zona
    shotZones = Counter(shotZones)
    moveZones = Counter(moveZones)
    
    for i in range(1,193):
        try:
            shotZones[i] += 0
        except:
            shotZones[i] = 0
        
        try: 
            moveZones[i] += 0
        except:
            moveZones[i] = 0
        
    row = np.arange(1, 192, 12)
    zones = np.array([row+i for i in range(12)])
    
    shotMat = np.zeros((12,16))
    moveMat = np.zeros((12,16))
    
    for k,v in shotZones.items():
        i = list(zones[(k%12)-1]).index(k)
        shotMat[(k%12)-1][i] = v/(v+moveZones[k])
        moveMat[(k%12)-1][i] = moveZones[k]/(v+moveZones[k])
        
    mat = {'Shot':shotMat, 'Movement': moveMat}
        
    if visualize: 
        for k,v in mat.items():
            pitch = Pitch(line_color='black', half=True)
    
            fig, ax = pitch.draw()
            fig.set_size_inches(7, 5)
            ax.set_xlim([0,120])
            ax.set_ylim([0,80])
    
            plt.imshow(v, cmap='YlGn',alpha=0.90, extent = (0, 120, 0, 80))
            plt.title(f'{k} Probability Given Start Zone')
            plt.show()
        
    return shotMat, moveMat

#%% Pruebas
#location = "D:\ExperimentosDatosPersonales\FerEsponda\Wyscout\Events\events_World_Cup.json"

#df1 = extraer_posiciones_events(location)

#df1 = normalizarDimensiones(df1)

#df1['zonaInicio'] = df1.apply(lambda df: coordenadas_to_zonas(df['x_inicio'],df['y_inicio']),
#                                  axis=1)

#df1['zonaFin'] = df1.apply(lambda df: coordenadas_to_zonas(df['x_fin'],df['y_fin']),
#                                  axis=1)

#s, p = probabilityMatrixes(df1)

    