# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 13:46:16 2021

@author: Santiago Fernández del Castillo Sodi

"""
#Les dejo unas visualizaciones graficas y de estadísticas miscelaneas/descriptivas
#con base en la información de los archivos de JSON. Espero haber explicado lo mejor
#posible como se usa y qué hace cada función. Cualquier cosa que no se entienda me dicen
#Saqué 3 de estas funciones del curso: https://uppsala.instructure.com/courses/28112
#Para que le echen un ojo

#Visualización descriptiva y gráfica de los datos
#de un torneo y de un partido dados
#Lo necesitamos para abrir un Json
import json
import pandas as pd

#Lo necesitamos para pintar el terreno de juego
import matplotlib.pyplot as plt
import numpy as np


#Vamos a necesitar navegar diferentes directorios
#importamos os para poder cambiar de directorio
import os
os.chdir("D:\\ExperimentosDatosPersonales")

#Importamos lo necesario para crear un terreno de juego
#Atasquense que hay lodo: https://fcpython.com/
from FCPython import createPitch
largoCampo=120
anchoCampo=80
(fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')

#Abrimos nuestros documentos de JSON
#Primero la base de datos completa
with open('D:\\ExperimentosDatosPersonales\\Curso_Soccermatics\\open-data-master\\data\\competitions.json') as f:
    competiciones = json.load(f)

#Despues obtenemos los datos de la competicion especifica
#que queremos estudiar más de cerca
#Es necesario conocer el nombre de la competición que nos interesa
#las enlisto a continuación
#Champions League (1999/2000 hasta 2018/2019)
#FA Women's Super League (2018/2019 hasta 2019/2020)
#FIFA World Cup (2018)
#La Liga (2004/2005 hasta 2019/2020)
#NWSL (2018)
#Premier League (2003/2004)
#Women's World Cup (2019)
def obtenerIDComp(nombreComp,temporada):
    """Función que arroja el id de la competicion y temporada
    ingresadas manualmente por el usuario como Strings"""
    
    for comp in competiciones:
        nombreCompBD = comp['competition_name']
        nombreCompBD.strip()
        if (nombreCompBD == nombreComp): 
            id_comp = comp['competition_id']
            break;
    
    for comp in competiciones:
        if (id_comp == comp['competition_id']):
            temp = comp['season_name']
            temp.strip()
            if temp == temporada: 
                id_temp = comp['season_id']
                break;
    
    return id_comp,id_temp
            
id_comp,id_temp = obtenerIDComp("FIFA World Cup","2018")
with open('D:\\ExperimentosDatosPersonales\\Curso_Soccermatics\\open-data-master\\data\\matches\\'+str(id_comp)+'\\'+str(id_temp)+'.json') as f:
    partidos = json.load(f)

#Imprimimos todos los resultados de este torneo
#en esa temporada especifica
#Visualizamos cada partido por separado
#e imprimimos el/los resultado/s

def todosPartidos(id_comp,id_temp):
    """Imprime todos los partidos de una competición"""
    with open('D:\\ExperimentosDatosPersonales\\Curso_Soccermatics\\open-data-master\\data\\matches\\'+str(id_comp)+'\\'+str(id_temp)+'.json') as f:
        partidos = json.load(f)
    for partido in partidos:
        local =partido['home_team']['home_team_name']
        visita =partido['away_team']['away_team_name']
        marcadorL =partido['home_score']
        marcadorV =partido['away_score']
        descripcion = 'El partido entre ' + local + ' y ' + visita
        resultado = ' terminó ' + str(marcadorL) +  ' : ' + str(marcadorV)
        print(descripcion + resultado)

    
def partidosEquipo(equipo,partidos):
    """Arroja todos los partidos de un solo equipo en la 
    competición de nuestro interés"""
    for partido in partidos:
        local = partidos['home_team']['home_team_name']
        visita = partidos['away_score']
        marcadorL =partidos['home_score']
        marcadorV = partidos['away_team']['away_team_name']
        if local==equipo or visita==equipo:
            print('El partido entre '+local+' y '+visita+' finalizó'+str(marcadorL)+' : '+str(marcadorV))


def partidoMiscelanea(equipoLocal,equipoVisitante):
    """Obten los datos miscelaneos de un partido dado"""
    for partido in partidos: 
        local =partido['home_team']['home_team_name']
        local.strip()
        visita =partido['away_team']['away_team_name']
        visita.strip()
        if (local == equipoLocal) and (visita == equipoVisitante):
            id_partido = partido['match_id']
            marcadorL =partido['home_score']
            marcadorV =partido['away_score']
            descripcion = local +' ' + str (marcadorL) + ' vs ' + str(marcadorV) + ' '+ visita
            print(descripcion)
            print("Datos del Partido:")
            print('Torneo: '+ partido['competition']['competition_name'])
            print('Jornada ' + str(partido['match_week']))
            print('Estadio: ' + partido['stadium']['name']+ ', '+ partido['stadium']['country']['name'])
            print('Fecha: ' +  str(partido['match_date']))
            print("\n")
            return id_partido
        
def conseguirEventos(id_partido):
    """Busca si los eventos del partido en cuestión están disponibles
    arroja una lectura de los mismos en una
    lista de diccionarios"""
    try:
        with open('D:\\ExperimentosDatosPersonales\\Curso_Soccermatics\\open-data-master\\data\\events\\'+str(id_partido)+'.json',encoding='UTF-8') as f:
           eventos = json.load(f)
           return eventos
    except:
        print("Intente de nuevo. Eventos para este partido no encontrados")

eventos = conseguirEventos(7566)
#Vamos a hacer la lectura de pases y tiros
#Primero tenemos que pasar nuestros datos JSON a una
#Estructura más manejable como un DataFrame
#Básicamente lo que hace es tomar cada llave de los diccionarios de
#JSON y navegarla (cada que toma una nueva llave la anida con _) hasta 
#sus niveles más profundos. Cada uno de estos procesos es una columna
#que se llena con los datos que contiene
#
df_eventos = pd.json_normalize(eventos, sep = "_")

#Hagamos primero los tiros
#Para obtenerlos hay que iterar la columna de tipo y
#almacenar en un dataframe aquellos que esten 
#Catalogados como tiro
tiros = df_eventos.loc[df_eventos['type_name'] == 'Shot'].set_index('id')

#Vamos a "plottear" todos los tiros según su lugar de
#origen y su desenlace final
local = "Mexico"
visita = "Sweden"

def plotTiros(tiros):
    """Función que grafica el punto de inicio de todos los tiros
    de un partido para ambos equipos involucrados"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,tiro in tiros.iterrows():
        x=tiro['location'][0]
        y=tiro['location'][1]
        gol=(tiro['shot_outcome_name']=='Goal')
        equipo= tiro['team_name'].strip()
        
        if (equipo == local):
            if gol:
                ploteo = plt.Circle((x,anchoCampo-y),3,color="red")
                plt.text((x+1),anchoCampo-y+1,tiro['player_name']) 
            else:
                ploteo = plt.Circle((x,anchoCampo-y),2,color="red")     
                ploteo.set_alpha(.2)
        elif (equipo==visita):
            if gol:
                ploteo = plt.Circle((largoCampo-x,y),3,color="blue") 
                plt.text((largoCampo-x+1),y+1,tiro['player_name']) 
            else:
                ploteo = plt.Circle((largoCampo-x,y),2,color="blue")      
                ploteo.set_alpha(.2)
        ax.add_patch(ploteo)
        
    plt.text(5,75,'Tiros de '+ visita) 
    plt.text(80,75,'Tiros de '+local)
    fig.set_size_inches(10, 7)
    plt.title("Tiros del juego: "+local+" vs "+visita)
    plt.show()
    return True

def plotTirosEquipo(tiros,equipo_tiros):
    """Función que grafica el punto de inicio de todos los tiros
    de un partido para ambos equipos involucrados"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,tiro in tiros.iterrows():
        x=tiro['location'][0]
        y=tiro['location'][1]
        gol=(tiro['shot_outcome_name']=='Goal')
        equipo= tiro['team_name'].strip()
        
        if (equipo == equipo_tiros):
            if gol:
                ploteo = plt.Circle((x,anchoCampo-y),3,color="red")
                plt.text((x+1),anchoCampo-y+1,tiro['player_name']) 
            else:
                ploteo = plt.Circle((x,anchoCampo-y),2,color="red")     
                ploteo.set_alpha(.2)
        ax.add_patch(ploteo)
        
    plt.text(5,75,'Tiros de '+ equipo_tiros) 
    fig.set_size_inches(10, 7)
    plt.show()
    return True

def plotTirosIndividual(tiros, jugador):
    """Función que grafica el punto de inicio de todos los tiros
    de un partido para un jugador específico"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,tiro in tiros.iterrows():
        if tiro['player_name'] == jugador:
            x=tiro['location'][0]
            y=tiro['location'][1]
            gol=(tiro['shot_outcome_name']=='Goal')
            equipo= tiro['team_name'].strip()
            
            if (equipo == local):
                if gol:
                    ploteo = plt.Circle((x,anchoCampo-y),3,color="red")
                    plt.text((x+1),anchoCampo-y+1,tiro['player_name']) 
                else:
                    ploteo = plt.Circle((x,anchoCampo-y),2,color="red")     
                    ploteo.set_alpha(.2)
            elif (equipo==visita):
                if gol:
                    ploteo = plt.Circle((largoCampo-x,y),3,color="blue") 
                    plt.text((largoCampo-x+1),y+1,tiro['player_name']) 
                else:
                    ploteo = plt.Circle((largoCampo-x,y),2,color="blue")      
                    ploteo.set_alpha(.2)
            ax.add_patch(ploteo)
        
    plt.text(5,75,'Tiros de '+ jugador) 
    fig.set_size_inches(10, 7)
    plt.title("Tiros del juego: "+local+" vs "+visita)
    plt.show()
    return True

#Ahora usando los benditos xGs
#Por si no están familiarizados:
#XG measures the quality of a chance by calculating the 
#likelihood that it will be scored from a particular position 
    
def plotTirosXG(tiros):
    """Función que grafica el punto de inicio de todos los tiros
    de un partido para ambos equipos involucrados. Esta vez consideramos el
    XG de cada uno de los tiros"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    xgL = 0
    xgV = 0
    for i,tiro in tiros.iterrows():
        x=tiro['location'][0]
        y=tiro['location'][1]
        gol=(tiro['shot_outcome_name']=='Goal')
        equipo= tiro['team_name'].strip()
        xg = tiro['shot_statsbomb_xg']
        tamaño=np.sqrt(tiro['shot_statsbomb_xg'])*8
        
        if (equipo == local):
            xgL = xgL + xg
            if gol:
                ploteo = plt.Circle((x,anchoCampo-y),tamaño,color="red")
                plt.text((x+1),anchoCampo-y+1,tiro['player_name']) 
            else:
                ploteo = plt.Circle((x,anchoCampo-y),tamaño,color="red")     
                ploteo.set_alpha(.2)
        elif (equipo==visita):
            xgV = xgV + xg
            if gol:
                ploteo = plt.Circle((largoCampo-x,y),tamaño,color="blue") 
                plt.text((largoCampo-x+1),y+1,tiro['player_name']) 
            else:
                ploteo = plt.Circle((largoCampo-x,y),tamaño,color="blue")      
                ploteo.set_alpha(.2)
        ax.add_patch(ploteo)
        
    plt.text(5,85,'Tiros de '+ visita) 
    plt.text(80,85,'Tiros de '+local)
    plt.text(5,10,'xGs '+visita+' : '+ str(round(xgV,4)))
    plt.text(80,10,'xGs '+local+' : '+str(round(xgL,4)))

    fig.set_size_inches(10, 7)
    plt.title("Tiros del juego: "+local+" vs "+visita)
    plt.show()
    return True

def plotTirosIndividualXG(tiros, jugador):
    """Función que grafica el punto de inicio de todos los tiros
    de un partido para un jugador específico tomanado su 
    XG para determinar el radio de las figuras"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    xg = 0
    for i,tiro in tiros.iterrows():
        if tiro['player_name'] == jugador:
            x=tiro['location'][0]
            y=tiro['location'][1]
            gol=(tiro['shot_outcome_name']=='Goal')
            equipo= tiro['team_name'].strip()
            xg += tiro['shot_statsbomb_xg']
            tamaño=np.sqrt(tiro['shot_statsbomb_xg'])*8
            
            if (equipo == local):
                if gol:
                    ploteo = plt.Circle((x,anchoCampo-y),tamaño,color="red")
                    plt.text((x+1),anchoCampo-y+1,tiro['player_name']) 
                else:
                    ploteo = plt.Circle((x,anchoCampo-y),tamaño,color="red")     
                    ploteo.set_alpha(.2)
            elif (equipo==visita):
                if gol:
                    ploteo = plt.Circle((largoCampo-x,y),tamaño,color="blue") 
                    plt.text((largoCampo-x+1),y+1,tiro['player_name']) 
                else:
                    ploteo = plt.Circle((largoCampo-x,y),tamaño,color="blue")      
                    ploteo.set_alpha(.2)
            ax.add_patch(ploteo)
        
    plt.text(5,75,'Tiros de '+ jugador) 
    plt.text(5,10,'xGs '+jugador+' : '+ str(round(xg,4)))
    fig.set_size_inches(10, 7)
    plt.show()
    return True

#Vamos a hacer algo similar con los pases
pases = df_eventos.loc[df_eventos['type_name'] == 'Pass'].set_index('id')
def pasesEquipo(pases,equipo_pases):
    """Funcion que nos grafica todos los pases de un equipo
    ingresado por el usuario"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,i_pase in pases.iterrows():
        x=i_pase['location'][0]
        y=i_pase['location'][1]
            
        if (i_pase['team_name']==equipo_pases):
            ploteo=plt.Circle((x,anchoCampo-y),2,color="red")
            ploteo.set_alpha(.2)
            ax.add_patch(ploteo)
        
        
    plt.text(5,75,'Pases de '+equipo_pases)
     
    fig.set_size_inches(10, 7) 
    plt.show()
    
def pasesIndividuales(pases,jugador):
    """Grafica todos los pases de un determinado jugador con
    flechas que señalan el inicio, dirección y final del pase"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,pase in pases.iterrows():
        if pase['player_name']==jugador:
            x=pase['location'][0]
            y=pase['location'][1]
            
            ploteo =plt.Circle((x,anchoCampo-y),2,color="red")
            ax.add_patch(ploteo)
            dirx=pase['pass_end_location'][0]-x
            diry=pase['pass_end_location'][1]-y
            flecha=plt.Arrow(x,anchoCampo-y,dirx,diry,width=1)
            ax.add_patch(flecha)
    
    plt.text(5,75,'Pases de '+jugador)     
    fig.set_size_inches(10, 7) 
    plt.show()

#Podemos hacer algo similar con los carries de balon
carries = df_eventos.loc[df_eventos['type_name'] == 'Carry'].set_index('id')
def carriesEquipo(carries,equipo_carry):
    """Funcion que nos grafica todos los carries de un equipo
    ingresado por el usuario"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,carry in carries.iterrows():
        x=carry['location'][0]
        y=carry['location'][1]
            
        if (carry['team_name']==equipo_carry):
            ploteo =plt.Circle((x,anchoCampo-y),1,color="red")
            ploteo.set_alpha(.2)
            ax.add_patch(ploteo)
            dirx=carry['carry_end_location'][0]-x
            diry=carry['carry_end_location'][1]-y
            flecha=plt.Arrow(x,anchoCampo-y,dirx,diry,width=1)
            ax.add_patch(flecha)
        
        
    plt.text(5,75,'Carries de '+equipo_carry)     
    fig.set_size_inches(10, 7) 
    plt.show()
    
def carriesIndividuales(carries,jugador):
    """Funcion que nos grafica todos los carries de un jugador
    ingresado por el usuario"""
    (fig,ax) = createPitch(largoCampo,anchoCampo,'yards','gray')
    for i,carry in carries.iterrows():
        if (carry['player_name']==jugador):
            x=carry['location'][0]
            y=carry['location'][1]
            ploteo =plt.Circle((x,anchoCampo-y),1,color="red")
            ploteo.set_alpha(.2)
            ax.add_patch(ploteo)
            dirx=carry['carry_end_location'][0]-x
            diry=carry['carry_end_location'][1]-y
            flecha=plt.Arrow(x,anchoCampo-y,dirx,diry,width=1)
            ax.add_patch(flecha)
        
        
    plt.text(5,75,'Carries de '+jugador)     
    fig.set_size_inches(10, 7) 
    plt.show()
    
#Vamos a calcular un estimado de la posesión de cada
#equipo del partido en cuestión. Es un estimado que se basa únicamente
#el tiempo de posesión del balón y no toma en cuenta otras variables}
#Igual, contrastandolo con los datos del partido que reporta
#La FIFA, no es una estimación tan lejana de la realidad
def posesion(eventos):
    """Estima la posesión de cada equipo durante el partido"""
    i = 0
    paises = []
    posLoc = 0
    posVis = 0
    for i,evento in eventos.iterrows():
        if evento["possession_team_name"] == local:
            if not np.isnan(evento["duration"]):
                posLoc += evento["duration"]
        elif evento["possession_team_name"] == visita:
            if not np.isnan(evento["duration"]):
                posVis += evento["duration"]
    
    posTot = posVis + posLoc
    perVis = posVis/posTot
    perVis = round(perVis,3)*100
    perLoc = posLoc/posTot
    perLoc = round(perLoc,3)*100
    return (perVis,perLoc)    
