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
#dfx = normalizarDimensiones(dfmid)

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
#dfx2 = normalizarDirecciones(dfx)

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

def crear_is_home(df):
    '''
    Agregar al df una columna is_home, establece un equipo de un partido como referencia,
    notar que el valor es 0 o otro entero. NORTA: podría ser 0 o 1.
    
    La función se usa en cambiar_coordenadas()
    
    Returns:
        df: df con la columna extra de is_home
    '''
    
    #df2 va a ser un df que por cada partido, tiene columnas separadas para cada equipo del partido
    df2 = df[['matchId','teamId','x_inicio']]
    
    df2 = df.groupby(['matchId','teamId']).size().reset_index().rename(columns={0:'count'})
    df2['team2'] = df2['teamId'].shift(-1)
    df2['match2'] = df2['matchId'].shift(-1)
    df2['same_match'] = df2['matchId']-df2['match2']
    
    df2.loc[df2.same_match == -1, "team2"] = df2.teamId
    df2.dropna(subset = ['same_match'], inplace=True)
    
    
    df2 = df2[df2['teamId'] != df2['team2']]
    df2['team1'] = df2['teamId']
    df2 = df2.drop(columns=['teamId'])
    
    #join del df con df2, así ya podemos fijar un equipo como "local"
    # la nueva columna permite afectar eventos de un solo equipo por cada partido.
    result = pd.merge(df,df2, how="left", on="matchId")
    result = result.drop(columns=['same_match'])
    result['is_home'] = result['teamId']-result['team1'] 
        
    return result

def cambiar_coordenadas(df):
    '''
    Recibe un df de eventos. Agrega la columna is_home y luego voltea todos los 
    eventos de un equipo para cada partido. Se mantienen las coordenadas originales 
    
    NOTA: esta versión si voltea las coordenadas, pero el equipo que se toma 
    como referencia es arbitrario.
    
    LIMPIAR CODIGO
    
    '''
    norm1 = crear_is_home(df)
    
    #declarar las nuevas columnas
    norm1['x_inic_norm']  = df.x_inicio
    norm1['x_fin_norm'] = df.x_fin
    
    norm1['x_inic_norm'] = df.loc[df.is_home != 0, "x_inicio"] = 100-df.x_inicio
    norm1['x_fin_norm'] = df.loc[df.is_home != 0, "x_fin"] = 100-df.x_fin
    
    
    ##Aun hay que checar que con diferentes datos, las cooerdenadas se voltean 
    # de forma adecuada
    
    #para los del mundial tenía que correr el siguiente bloque 
    
    #ojo: luego hay que cambiar todo lo de '2H'. Si no estárían al revés. en 1h todos de izq a der y en 2h de der a izq
    #norm1['x_inic_norm'] = result.loc[result.matchPeriod != '1H', "x_inic_norm"] = 100-result.x_inicio
    #norm1['x_fin_norm'] = result.loc[result.matchPeriod != '1H', "x_fin"] = 100-result.x_fin
    
    return norm1