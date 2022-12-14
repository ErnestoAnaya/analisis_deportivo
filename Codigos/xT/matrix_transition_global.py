import pandas as pd
import numpy as np

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

# Se ve como
# 1 13 25 ... 181
# 2 14 26 ... 182
# ...
# 12 24 36 ... 192     


#Leer datos
df = pd.read_csv("events_World_Cup.csv", index_col=0) #eventos mundial
event_names = pd.read_csv("eventid2name.csv") #id de eventos a nombres de eventos
tag_names = pd.read_csv("tags2name.csv") #tags de eventos a nombres de tags



#Para cada coordenada de un evento, su zona (cuadrante) correspondiente
df['quad1'] = df.apply(lambda x: coordenadas_to_zonas(x['x_inicio'], x['y_inicio']), axis=1)
df['quad2'] = df.apply(lambda x: coordenadas_to_zonas(x['x_fin'], x['y_fin']), axis=1)


def quad_to_index(quad):
    #Dado un cuadrante, regresa sus índices correspondientes de la matriz
    x1 = (quad-1)%12
    x2 = int(np.floor((quad-1)/12))
    return [x1,x2]

#Definimos eventos que se consideran movimientos 
mov_events = [30,31,32,34,70,80,81,82,83,84,85,86]
df_mov = df.loc[df.subEventId.isin(mov_events)]
quads = list(range(1,193))

#Matriz de transición para cada cuadrante
for quad in quads:
    aux = df_mov.loc[df_mov.quad1==quad] #Movimientos que empiezan en quad
    movs = len(aux) #Número de movimientos que empiezan en quad
    zonas_fin = aux.quad2.unique() #Zonas distintas de finalización que empezaron en quad
    mat = np.zeros((12,16)) #Matriz de transición vacía

    #Para cada zona de finalización, cuántos movimientos acabaron ahí
    for zona in zonas_fin:
        coords = quad_to_index(zona) #Coordenadas en la matriz de zona
        movs_zona = len(aux.loc[aux.quad2==zona]) #Número de movimientos finalizados en zona
        mat[coords[0]][coords[1]] = movs_zona #Se añade movs_zona al cuadrante correspondiente de la matriz de transición
    div = movs*np.ones(16)
    mat = mat/div #Se divide entre los movimientos totales iniciados en quad para normalizar el valor del cuadrante
    mat_fin = pd.DataFrame(mat)
    mat_fin.to_csv('./matrix_transition_global/zona'+str(quad)+'.csv') #Se escribe la matriz en un csv (se puede hacer en un pickle también)