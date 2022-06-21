import pandas as pd
import math 
import numpy as np

def normalizarDimensiones(df,tam=[110,70]):
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
    df1[['x_inicio','x_fin']] = df1[['x_inicio','x_fin']].apply(lambda x: tam[0]*(x-x.min())/(x.max()-x.min()))
    df1[['y_inicio','y_fin']] = df1[['y_inicio','y_fin']].apply(lambda x: tam[1]*(x-x.min())/(x.max()-x.min()))
    return df1


#Test Case: sobre el DF de jugadas
dfx = normalizarDimensiones(dfmid)

def normalizarDirecciones(df,tam=[110,75]):
    '''
    Función para normalizar la dirección de las acciones. Con ella se logra
    que el equipo que ataca hacia la derecha en el primer tiempo (1H), "ataque" hacia
    la derecha también en el segundo tiempo (2H). 
    
    Se rotan las variables (x,y) sobre su propio eje restándolas del largo y ancho de la
    cancha respectivamente. 

    Args:
        df (TYPE): DataFrame con los datos originales. No será alterado.
        tam (NUMERIC, optional): Valores normalizados
                                Defaults to [110,70].

    Returns:
        df1 (TYPE): Nuevo dataframe con los valores de las columnas con las direcciones
                    normalizadas.

    '''
    
    df1 = df.copy()
    
    df1.loc[df1.matchPeriod=="2H",['x_inicio','x_fin']] = (tam[0] - 
                                                           df1.loc[df1.matchPeriod=="2H",['x_inicio','x_fin']])
    df1.loc[df1.matchPeriod=="2H",['y_inicio','y_fin']] = (tam[1] - 
                                                           df1.loc[df1.matchPeriod=="2H",['y_inicio','y_fin']])

    return df1

#Test Case
dfx2 = normalizarDirecciones(dfx)

def distanciaGol(x,y,team=0,tam=[110,75],return_angle=True):
    '''
    Funcion para calcular la distancia y angulo entre un punto (x,y)
    y la porteria que ataca el equipo team.
    
    Puede o no regresar el angulo segun lo desee el usuario.

    Args:
        x (NUMERIC): coordenada x.
        y (NUMERIC): coordenada y.
        team (NUMERIC, optional): Equipo a estudiar. Si es 0 el equipo que ataca
                                 la porteria en (0,maxY/2) en el periodo 1H. Si es 1 el que ataca
                                 la porteria en (maxX, maxY/2). Defaults to 0.
        tam (LIST, optional): Dimensiones de la cancha [maxX,maxY]. Defaults to [110,75].
        return_angle (BOOLEAN, optional): Condición para regresar o no el angulo.
                                          Defaults to True.

    Returns:
        dist (NUMERIC): distancia entre (x,y) y la porteria que se ataca.
        ang (NUMERIC, optional): angulo en radianes entre el punto (x,y) y 

    '''
    
    if team:
        dist = math.sqrt((tam[0]-x)**(2) + (tam[1]/2-y)**(2))
    else:
        dist = math.sqrt((0-x)**(2) + (tam[1]/2-y)**(2))
    
    if return_angle:
        v2 = [0,tam[0]]
        if team:
            v1 = [tam[0]-x,tam[1]/2-y]
        else:
            v1 = [0-x,tam[1]/2-y]
            
        u1 = v1 / np.linalg.norm(v1)
        u2 = v2 / np.linalg.norm(v2)
        ang = np.arccos(np.dot(u1, u2))
        return (dist,ang)
    else:
        return (dist,None)
    
#Test Case
#x = 70, y = 50
distancia,angulo = distanciaGol(70,50,1)
