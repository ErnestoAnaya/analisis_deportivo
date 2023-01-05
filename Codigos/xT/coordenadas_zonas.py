import numpy as np
from collections import Counter
import pandas as pd
import json
import math 
from mplsoccer.pitch import Pitch, VerticalPitch
import matplotlib.pyplot as plt
import os
from xg_model import process_shots, model_xg, calculate_xG, plot_xg
from functools import reduce

def transitionData():
    df = pd.read_csv("events_World_Cup.csv", index_col=0) #eventos mundial
    event_names = pd.read_csv("eventid2name.csv") #id de eventos a nombres de eventos
    tag_names = pd.read_csv("tags2name.csv")
    return df, event_names, tag_names

def transmformCoordinates(df):    
    df['zonaInicio'] = df.apply(lambda x: coordenadas_to_zonas(x['x_inicio'], x['y_inicio']), axis=1)
    df['zonaFin'] = df.apply(lambda x: coordenadas_to_zonas(x['x_fin'], x['y_fin']), axis=1)
    return df

def find_index(arr, K):
    #Binary search para encontrar el índice de un nuevo elemento en un arreglo ordenado
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

def quad_to_index(quad):
    #Dado un cuadrante, regresa sus índices correspondientes de la matriz
    x1 = (quad-1)%12
    x2 = int(np.floor((quad-1)/12))
    return [x1,x2]

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
            
    shotMat = np.zeros((12,16))
    moveMat = np.zeros((12,16))
    
    for k,v in shotZones.items():
        x,y = quad_to_index(k)
        shotMat[x][y] = v/(v+moveZones[k])
        moveMat[x][y] = moveZones[k]/(v+moveZones[k])
        
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

def matrixTxy(df):  
    mov_events = [30,31,32,34,70,80,81,82,83,84,85,86] #estos eventos son: pases, unos tiros libres y acceleration
    df_mov = df.loc[df.subEventId.isin(mov_events)] # codigo original
    quads = list(range(1,193))
    
    #Matriz de transición para cada cuadrante
    for quad in quads:
        aux = df_mov.loc[df_mov.zonaInicio==quad] #Movimientos que empiezan en quad
        movs = len(aux) #Número de movimientos que empiezan en quad
        zonas_fin = aux.zonaFin.unique() #Zonas distintas de finalización que empezaron en quad
        mat = np.zeros((12,16)) #Matriz de transición vacía
    
        #Para cada zona de finalización, cuántos movimientos acabaron ahí
        for zona in zonas_fin:
            coords = quad_to_index(zona) #Coordenadas en la matriz de zona
            movs_zona = len(aux.loc[aux.zonaFin==zona]) #Número de movimientos finalizados en zona
            mat[coords[0]][coords[1]] = movs_zona #Se añade movs_zona al cuadrante correspondiente de la matriz de transición
        div = movs*np.ones(16)
        mat = mat/div #Se divide entre los movimientos totales iniciados en quad para normalizar el valor del cuadrante
        mat_fin = pd.DataFrame(mat)
        try:
            mat_fin.to_csv('./matrix_transition_global/zona'+str(quad)+'.csv') #Se escribe la matriz en un csv (se puede hacer en un pickle también)
        except:
            os.mkdir('./matrix_transition_global')
            mat_fin.to_csv('./matrix_transition_global/zona'+str(quad)+'.csv') #Se escribe la matriz en un csv (se puede hacer en un pickle también)

    
    return True

def sumando1(x,y, xg_zonas, s, zona):
    xG = xg_zonas[xg_zonas['zonaInicio'] == zona]['xG']
    shot_probability = s[x][y]
    return shot_probability * xG

def index_to_quad(x,y):
    row = np.arange(1, 192, 12)
    mat = np.array([row+i for i in range(12)])
    return mat[x][y]

#%% Pruebas
#location = "D:\ExperimentosDatosPersonales\FerEsponda\Wyscout\Events\events_World_Cup.json"

#df1 = extraer_posiciones_events(location)

#df1 = normalizarDimensiones(df1)

#df1['zonaInicio'] = df1.apply(lambda df: coordenadas_to_zonas(df['x_inicio'],df['y_inicio']),
#                                  axis=1)

#df1['zonaFin'] = df1.apply(lambda df: coordenadas_to_zonas(df['x_fin'],df['y_fin']),
#                                  axis=1)

#s, p = probabilityMatrixes(df1)

df = extraer_posiciones_events('./../../data/events_England.json')

event_names = pd.read_csv("eventid2name.csv") #id de eventos a nombres de eventos
tag_names = pd.read_csv("tags2name.csv") #tags de eventos a nombres de tags


df1 = normalizarDimensiones(df)

df1['zonaInicio'] = df1.apply(lambda df: coordenadas_to_zonas(df['x_inicio'],df['y_inicio']),
                                  axis=1)

df1['zonaFin'] = df1.apply(lambda df: coordenadas_to_zonas(df['x_fin'],df['y_fin']),
                                  axis=1)

s, p = probabilityMatrixes(df1)

matrixTxy(df1)

#%% xG Matrix
def calc_angle(row):
    #print(row)
    x = 110 - row['X']
    y1 = np.abs(35+7.32/2 - row['Y'])
    y2 = np.abs(35-7.32/2 - row['Y'])
    
    l1 = np.sqrt(x**2 + y1**2)
    l2 = np.sqrt(x**2 + y2**2)
    l3 = 7.32
    
    angle = np.arccos( (l1**2 + l2**2 - l3**2)/(2*l1*l2) )
    #if angle <0:
    #    angle = np.pi +angle
        
    return angle

shots_model = process_shots(df1) #only returns shots
shots_model['Angle'] = shots_model[['X', 'Y']].apply(lambda x: calc_angle(x),axis = 1)

model_summary, b = model_xg(shots_model)

shots_model['xG'] = shots_model.apply(lambda x: calculate_xG(x, b), axis=1) 


shots_model['zonaInicio'] = shots_model.apply(lambda df: coordenadas_to_zonas(df['X'],df['Y']),
                                  axis=1)

shots_model.hist('zonaInicio')

#
xg_zonas = shots_model.groupby(by='zonaInicio').mean().reset_index()

zonas = np.arange(1, 193, 1)
df_zonas = pd.DataFrame(zonas, columns=['zonaInicio'])

xg_zonas = pd.merge(df_zonas, xg_zonas[['zonaInicio', 'xG']], how = 'outer', on = 'zonaInicio').fillna(0)



#%% xThreat
import seaborn as sns  


#tener todas las matrices a la mano
matrices_transicion = {}
for z in range(1,193):
    matrices_transicion[z] = pd.read_csv(rf'matrix_transition_global\zona{z}.csv',
                         index_col=[0]).to_numpy()

#Llenar la primera matriz de puros 0
xT = np.zeros((12,16))

#La primera iteracion del xT es s*xG
for zona in range(1,193):
    x,y = quad_to_index(zona)
    #print(sumando1(x, y, xg_zonas, s))
    xT[x][y] = sumando1(x,y,xg_zonas,s, zona)
    
tit = 'xT inicial'
ax = sns.heatmap(xT).set(title=tit)
plt.show()

#Demas iteraciones
#5 iteraciones
for n in range(0,4):
    #Para cada zona
    for z in range(1,193):
        #Indices de la zona
        x,y = quad_to_index(z)
        #Probabilidad de movimiento
        m = p[x][y]
        #Matriz de transicion
        trans = matrices_transicion[z]
        #Para cada zona
        suma = 0
        for j in range(0,16):
            for i in range(0,12):
              #Probabilidad de moverme de (x,y) a la zona (i,j)
              suma += trans[i][j]*xT[i][j]
              #print(xT[i][j])
        #Actualizacion de los valores de xT
        xT[x][y] = suma*m + sumando1(x,y,xg_zonas,s, z) 
        xT = np.nan_to_num(xT)
        #tit = 'trans: '+str(z)
        #ax = sns.heatmap(trans).set(title=tit)
        #plt.show()
        
    tit = 'xT '+str(n)
    ax = sns.heatmap(xT).set(title=tit)

    plt.show()
        
#modificaciones hechas:
#cambiar for loops
#a sumando1, se le agregó un parametro z para mostrar la zona

xg_mat = np.zeros((12,16))

xg_avg = shots_model.groupby(by='zonaInicio').mean().reset_index()
xg_avg['xG'] = xg_avg['xG']

for zona in range(1,193):
    x,y = quad_to_index(zona)
    if xg_avg['zonaInicio'].isin([zona]).any():
        xg_mat[x][y] = xg_avg[xg_avg['zonaInicio'] == zona]['xG']


#%% Obtencion xT individual
# xTA y Riesgo

#Jugada por jugada (eventos)
# Coordenadas a Zonas
# Diferencial entre xT de zonas
# Resta y group by player Id -> sum

#Riesgo (¿qué eventos considero riesgo?)
#Lo mismo acciones defensivas

#Cummulative: 
    # Restas 1 a 1
    
#%% xT inidividual
#GLOBAL

def xTPreprocessing(xT, type_ = 1):
    
    if type_:
        row = np.arange(1, 192, 12)
        mat = np.array([row+i for i in range(12)])
    else:
        mat = np.flip(np.flip(mat,axis=1),axis=0)

    matf = mat.flatten()
    xTf = xT.flatten()

    zonexT = {k:v for k, v in zip(matf, xTf)}

    return zonexT

def jugadoresDF():
    
    with open(r"D:\ExperimentosDatosPersonales\FerEsponda\Wyscout\players.json") as f:
        jugadores = json.load(f)
        
    jugadores = pd.json_normalize(jugadores, sep = "_")
    
    jugadores['Name'] = jugadores['firstName'] + ' ' + jugadores['lastName']
    
    jugadores = jugadores[['Name','wyId','role_name']]
    
    jugadores.rename(columns={"wyId": "playerId"}, inplace=True)
    
    return jugadores

jugadores = jugadoresDF()

def xTPlayers(id_equipo=-1):
    if id_equipo == -1:
        aux = df1.copy()
    else:
        aux = df1[df1['teamId']==id_equipo]
        
    zonexTf = xTPreprocessing(xT)
        
    events = ['Simple pass', 'High pass', 'Head pass','Smart pass',
              'Free Kick', 'Cross', 'Shot','Corner',
              'Acceleration','Free kick cross', 'Free kick shot']
        
    aux = aux[aux['subEventName'].isin(events)]
        
    aux.replace({'zonaInicio': zonexTf,'zonaFin': zonexTf},inplace=True)
    aux['xT'] = aux['zonaFin'] - aux['zonaInicio']
    aux = aux.groupby('playerId')['xT'].sum()
    aux.sort_values(ascending=False, inplace = True)
    
    aux2 = pd.merge(aux,jugadores,on='playerId',how='left')
    
    del aux
    
    aux2.sort_values(by=['xT'], ascending=False, inplace=True)
    
    return aux2
    

def xTSaved_Players(id_equipo=-1):
    if id_equipo == -1:
        aux = df1.copy()
    else:
        aux = df1[df1['teamId']==id_equipo]
        
    zonexTf = xTPreprocessing(xT,0)    
    
    events = ['Ground defending duel', 'Clearance']
    
    aux = aux[aux['subEventName'].isin(events)]
    
    tags = ['703','1401','1501','2101','602']
    
    headers = ''
    
    for t in tags:
        for i in range(0,6):
            headers += f'tag_{i} == {t} or '
    
    headers = headers[:-4]
    
    aux = aux.query(headers)
        
    aux.replace({'zonaInicio': zonexTf,'zonaFin': zonexTf},inplace=True)
    aux['xTSaved'] = aux['zonaInicio']
    aux = aux.groupby('playerId')['xTSaved'].sum()
    aux.sort_values(ascending=False, inplace = True)
    
    aux2 = pd.merge(aux,jugadores,on='playerId',how='left')
    
    del aux
    
    aux2.sort_values(by=['xTSaved'], ascending=False, inplace=True)
    
    return aux2
    
def xTRisk(id_equipo=-1):
    if id_equipo == -1:
        aux = df1.copy()
    else:
        aux = df1[df1['teamId']==id_equipo]
            
    tags = ['102','2001','1302','601','701']
    
    zonexTf = xTPreprocessing(xT,0)
    
    headers = ''
    
    for t in tags:
        for i in range(0,6):
            headers += f'tag_{i} == {t} or '
    
    headers = headers[:-4]
    
    aux = aux.query(headers)
        
    aux.replace({'zonaInicio': zonexTf,'zonaFin': zonexTf},inplace=True)
    aux['xTRisk'] = aux['zonaInicio']
    aux = aux.groupby('playerId')['xTRisk'].sum()
    aux.sort_values(ascending=False, inplace = True)
    
    aux2 = pd.merge(aux,jugadores,on='playerId',how='left')
    
    del aux
    
    aux2.sort_values(by=['xTRisk'], ascending=False, inplace=True)
    
    return aux2

# CASO DE USO
# data_frames = [xTPlayers(),xTSaved_Players(),xTRisk()]

# res = reduce(lambda left,right: pd.merge(left,right,on=['playerId'],
#                                          how='outer'), data_frames).fillna(0)
# res = res[['playerId','Name_x','role_name_x','xT','xTSaved','xTRisk']]

# res['Total'] = res['xT'] + res['xTSaved'] - res['xTRisk']
    
    
