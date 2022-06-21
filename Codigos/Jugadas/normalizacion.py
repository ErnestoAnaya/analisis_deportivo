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
