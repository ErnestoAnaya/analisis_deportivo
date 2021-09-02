# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 16:47:49 2020

@author: Sebastian Dulong Salazar, stats: FBRef.com

Sacar probabilidades de resultados usando la distribución Poisson 
"""

import csv
import math
import matplotlib.pyplot as plt
#from scipy.stats import poisson #la parte de poisson se puede hacer así 
                                #no lo he revisado

#abrir el csv de donde vamos a usar los datos
f = open('C:/Users/ssds6/OneDrive/Escritorio/Football_analytics/liguilla.csv')

#se puede hacer lo mismo con pandas 

data = csv.reader(f)
rows = list(data)

f.close()

#colores de los equipos
colors = {
  'León':'green',
  'América':'yellow',
  'UNAM':'darkgoldenrod',
  'Cruz Azul':'blue',
  'Monterrey':'steelblue',
  'UANL':'darkorange',
  'Pachuca':'dodgerblue',
  'Guadalajara': 'r',
  'Santos':'lime',
  'Necaxa':'salmon',
  'Toluca':'red',
  'FC Juárez':'black',
  'Puebla':'aqua',
  'Mazatlán FC':'indigo',
  'Tijuana':'maroon',
  'Atlas':'saddlebrown',
  'Querétaro':'teal',
  'Atlético':'orangered'
}

#todos los datos
def __all__():
    for i in range(len_data()):
        print(rows[i])

#nombres
def team_names():
    for i in range(len_data()):
        print(rows[i][1])
        
#no. equipos (para hacerlo para otras ligas)
def len_data():
    return len(rows)

#hay varias funciones medio pendejas que solo sirven si van a cambiar de liga
#cuantos partidos en casa (el no. de partidos es impar)
def games_home():
    gm=0
    for i in range(len_data()):
        gm+=int(rows[i][2])
    return gm

#fuera de casa
def games_away():
    gm=0
    for i in range(len_data()):
        gm+=int(rows[i][11])
    return gm

#promedio de goles que meten todos los equipos en casa
def avg_homegf():
    gls=0
    games=games_home()
    for i in range(len_data()):
        gls+=int(rows[i][6])
    return gls/games

#promedio de goles que meten todos los equipos fuera 
def avg_homega():
    gls=0
    games=games_home()
    for i in range(len_data()):
        gls+=int(rows[i][7])
    return gls/games

#regresa el indice del ekipo
def find_team(name):
    i=0
    while i<len_data() and rows[i][1]!=name:
        i+=1
    if i<len_data():
        return i
    return -1
#para el calculo de las lambdas (esta forma de sacar strengths no me convence
#se aceptan sugerencias)
def home_atk_str(name):
    str=-1
    loc=find_team(name)
    if loc!=-1:
        str=int(rows[loc][6])/(int(rows[loc][2])*avg_homegf())
    return str

def home_def_str(name):
    str=-1
    loc=find_team(name)
    if loc!=-1:
        str=int(rows[loc][7])/(int(rows[loc][2])*avg_homega())
    return str

def away_atk_str(name):
    str=-1
    loc=find_team(name)
    if loc!=-1:
        str=int(rows[loc][15])/(int(rows[loc][11])*avg_homega())
    return str

def away_def_str(name):
    str=-1
    loc=find_team(name)
    if loc!=-1:
        str=int(rows[loc][16])/(int(rows[loc][11])*avg_homegf())
    return str

def lambdas(home, visit):
    if home_atk_str(home)==-1 or away_atk_str(visit)==-1:
        return [-1,-1]
    return [home_atk_str(home)*away_def_str(visit)*avg_homegf(), away_atk_str(visit)*home_def_str(home)*avg_homega()]
    
def poisson_dist(lamb, k):
    return (math.exp(-lamb)*lamb**k)/math.factorial(k)

def prob_goals_home(home, visit):
    l=[]
    p=lambdas(home,visit)
    if p != [-1,-1]:
        for i in range(5):
            l.append(poisson_dist(lambdas(home,visit)[0], i))
        l.append(1-sum(l))
    return l

def prob_goals_visit(home, visit):
    l=[]
    p=lambdas(home,visit)
    if p != [-1,-1]:
        for i in range(5):
            l.append(poisson_dist(lambdas(home,visit)[1], i))
        l.append(1-sum(l))
    return l
              
def matrix(home, visit):
    mat=[]
    gh=prob_goals_home(home, visit)
    ga=prob_goals_visit(home, visit)
    if gh!=[]:
        mat.append([' ','0','1','2','3','4','5+'])
        for i in range(6):
            l=[i]
            for j in range(6):
                l.append(ga[i]*gh[j]*100)
            mat.append(l)
    return mat

def matrix_2dec(home, visit):
    mat=[]
    gh=prob_goals_home(home, visit)
    ga=prob_goals_visit(home, visit)
    if gh!=[]:
        mat.append([' ',0,1,2,3,4,5])
        for i in range(6):
            l=[i]
            for j in range(6):
                l.append(float(format(ga[i]*gh[j]*100,'.2f')))
            mat.append(l)
    return mat

def matrix_print(home, visit):
    mat=[]
    gh=prob_goals_home(home, visit)
    ga=prob_goals_visit(home, visit)
    if gh!=[]:
        mat.append([' ','0','1','2','3','4','5+'])
        for i in range(6):
            if i!=5:
                l=[i]
            else:
                l=['5+']
            for j in range(6):
                l.append(format(ga[i]*gh[j]*100,".2f"))
            mat.append(l)
    for x in mat:
        print(x)

def prob_win_home(home, visit):
    p=-1
    if find_team(home)!=-1 and find_team(visit)!=-1:
        p=0
        for i in range(1,7):
            for j in range(1,7):
                if i<j:
                    p+=matrix(home, visit)[i][j]
        return format(p,".2f")+'%'
    return p

def prob_win_visit(home, visit):
    p=-1
    if find_team(home)!=-1 and find_team(visit)!=-1:
        p=0
        for i in range(1,7):
            for j in range(1,7):
                if i>j:
                    p+=matrix(home, visit)[i][j]
        return format(p,".2f")+'%'
    return p

def prob_tie(home, visit):
    p=-1
    if find_team(home)!=-1 and find_team(visit)!=-1:
        p=0
        for i in range(1,7):
            for j in range(1,7):
                if i==j:
                    p+=matrix(home, visit)[i][j]
        return format(p,".2f")+'%'
    return p

def gray_area(home, visit):
    p=-1
    if find_team(home)!=-1 and find_team(visit)!=-1:
        p=matrix(home, visit)[6][6]
        return p+'%'
    return p

def prob_score(home, visit, gl_home, gl_away):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(gl_home)==int and type(gl_away)==int and gl_home>=0 and gl_away>=0:
        if gl_home>4 and gl_away>4:
            return gray_area(home, visit)
        else:
            return format(matrix(home, visit)[gl_away+1][gl_home+1],".2f")+'%'
    return -1

def prob_home_win_by(home, visit, dif):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(dif)==int and dif>0:
        if dif>4:
            return '<'+format(matrix(home, visit)[1][6],".2f")+'%'
        else:
            sum=0
            for i in range(1,7):
                for j in range(1,7):
                    if j==i+dif:
                        sum+=matrix(home, visit)[i][j]
            return format(sum,".2f")+'%'
    return -1

def prob_visit_win_by(home, visit, dif):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(dif)==int and dif>0:
        if dif>4:
            return '<'+format(matrix(home, visit)[6][1],".2f")+'%'
        else:
            sum=0
            for i in range(1,7):
                for j in range(1,7):
                    if i==j+dif:
                        sum+=matrix(home, visit)[i][j]
            return format(sum,".2f")+'%'
    return -1

def prob_home_win_by_at_least(home, visit, dif):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(dif)==int and dif>0:
        if dif>4:
            return format(matrix(home, visit)[1][6],".2f")+'%'
        else:
            sum=0
            for i in range(1,7):
                for j in range(1,7):
                    if j>=i+dif:
                        sum+=matrix(home, visit)[i][j]
            return format(sum,".2f")+'%'
    return -1

def prob_visit_win_by_at_least(home, visit, dif):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(dif)==int and dif>0:
        if dif>4:
            return format(matrix(home, visit)[6][1],".2f")+'%'
        else:
            sum=0
            for i in range(1,7):
                for j in range(1,7):
                    if i>=j+dif:
                        sum+=matrix(home, visit)[i][j]
            return format(sum,".2f")+'%'
    return -1

def prob_home_score(home, visit, h_gls):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(h_gls)==int and h_gls>=0:
        sum=0
        if h_gls>4:
            for i in range(1,7):
                sum+=matrix(home, visit)[i][6]
            return '<'+format(sum,".2f")+'%'
        else:
            for i in range(1,7):
                sum+=matrix(home, visit)[i][h_gls+1]
            return format(sum,".2f")+'%'
    return -1

def prob_visit_score(home, visit, v_gls):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(v_gls)==int and v_gls>=0:
        sum=0
        if v_gls>4:
            for i in range(1,7):
                sum+=matrix(home, visit)[6][i]
            return '<'+format(sum,".2f")+'%'
        else:
            for i in range(1,7):
                sum+=matrix(home, visit)[v_gls+1][i]
            return format(sum,".2f")+'%'
    return -1

def prob_home_score_at_least(home, visit, h_gls):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(h_gls)==int and h_gls>=0:
        sum=0
        if h_gls>4:
            for i in range(1,7):
                sum+=matrix(home, visit)[i][6]
            return format(sum,".2f")+'%'
        else:
            for i in range(1,7):
                for j in range(h_gls+1,7):
                    sum+=matrix(home, visit)[i][j]
            return format(sum,".2f")+'%'
    return -1

def prob_visit_score_at_least(home, visit, v_gls):
    if find_team(home)!=-1 and find_team(visit)!=-1 and type(v_gls)==int and v_gls>=0:
        sum=0
        if v_gls>4:
            for i in range(1,7):
                sum+=matrix(home, visit)[6][i]
            return format(sum,".2f")+'%'
        else:
            for i in range(1,7):
                for j in range(v_gls+1,7):
                    sum+=matrix(home, visit)[j][i]
            return format(sum,".2f")+'%'
    return -1

def prob_home_do_score(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        sum=0
        for i in range(1,7):
            sum+=matrix(home, visit)[i][1]
        return format(100-sum,".2f")+'%'
    return -1

def prob_visit_do_score(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        sum=0
        for i in range(1,7):
            sum+=matrix(home, visit)[1][i]
        return format(100-sum,".2f")+'%'
    return -1

def prob_home_dont_score(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        sum=0
        for i in range(1,7):
            sum+=matrix(home, visit)[i][1]
        return format(sum,".2f")+'%'
    return -1

def prob_visit_dont_score(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        sum=0
        for i in range(1,7):
            sum+=matrix(home, visit)[1][i]
        return format(sum,".2f")+'%'
    return -1

def most_likely_result(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        max=[1,1]
        for i in range(1,7):
            for j in range(1,7):
                if(matrix(home, visit)[i][j]>matrix(home, visit)[max[0]][max[1]]):
                    max=[i,j]
        max.append(format(matrix(home,visit)[max[0]][max[1]],'.2f'))
        max[0]-=1
        max[1]-=1
        max[0],max[1]=max[1],max[0]
        
        return max
    return []

def both_score(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        sum=0
        for i in range(2,7):
            for j in range(2,7):
                sum+=matrix(home,visit)[i][j]
        return format(sum,'.2f')+'%'
    return -1

def all_odds(home, visit):
    if find_team(home)!=-1 and find_team(visit)!=-1:
        print(home +': '+prob_win_home(home,visit))
        print('Empate: '+prob_tie(home,visit))
        print(visit +': '+prob_win_visit(home,visit))
        print()
    
def plt_odds(home,visit): #plt.figure().gca ya no va a servir creo
    if find_team(home)!=-1 and find_team(visit)!=-1:
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        m = matrix_2dec(home, visit)

        for i in range(1,7):
            for j in range(1,7):
                mc=colors[visit]
                if i==j:
                    mc='magenta'
                elif i<j:
                    mc=colors[home]
            
                ax.plot([m[0][j]], [m[i][0]], [m[i][j]], markerfacecolor=mc, 
                        markeredgecolor='black', marker='o', markersize=5, alpha=0.6)
        ax.set_xlabel('# goles '+home)
        ax.set_ylabel('# goles '+visit)
        ax.set_zlabel('Probabilidad en %')

#así ven todo
matrix_2dec('Puebla','León')
all_odds('Puebla', 'León')
mlr=most_likely_result('Puebla', 'León')
print(mlr)
print(lambdas('Puebla','León'))
plt_odds('Puebla','León') 

"""
suma=0
#para sacar prob de que atletico gane si el puebla marca al menos 1
for i in range(3,7):
    for j in range(2,7):
        if(i>j):
            suma+=matrix('Puebla', 'Atlético')[i][j]


all_odds('Guadalajara', 'América')
mlr=most_likely_result('Guadalajara', 'América')
print(mlr)
print(lambdas('Guadalajara', 'América'))
plt_odds('Guadalajara', 'América')
print()

all_odds('UANL', 'Cruz Azul')
mlr=most_likely_result('UANL', 'Cruz Azul')
print(mlr)
print(lambdas('UANL', 'Cruz Azul'))
plt_odds('UANL', 'Cruz Azul')
print()

all_odds('Pachuca', 'UNAM')
mlr=most_likely_result('Pachuca', 'UNAM')
print(mlr)
print(lambdas('Pachuca', 'UNAM'))
plt_odds('Pachuca', 'UNAM')
print()


all_odds('Pachuca', 'Necaxa')
mlr=most_likely_result('Pachuca', 'Necaxa')
print(mlr)
print()
all_odds('Guadalajara', 'Monterrey')
mlr=most_likely_result('Guadalajara', 'Monterrey')
print(mlr)
print()
all_odds('UANL', 'Atlas')
mlr=most_likely_result('UANL', 'Atlas')
print(mlr)
print()
all_odds('Cruz Azul', 'UNAM')
mlr=most_likely_result('Cruz Azul', 'UNAM')
print(mlr)
print()
all_odds('Toluca', 'León')
mlr=most_likely_result('Toluca', 'León')
print(mlr)
print()
all_odds('Santos', 'Mazatlán FC')
mlr=most_likely_result('Santos', 'Mazatlán FC')
print(mlr)
print()
all_odds('Querétaro', 'Tijuana')
mlr=most_likely_result('Querétaro', 'Tijuana')
print(mlr)
print()
"""
