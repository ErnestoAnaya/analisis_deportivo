# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt 

import statsmodels.api as sm
import statsmodels.formula.api as smf

import FCPython



#extraer goles
def get_goals(shots):
    '''
    dado un df de tiros, regresa los goles
    
    '''
    
    goals = shots[(shots['tag_0'] == 101) | #747 goles de tiros
                      (shots['tag_1'] == 101) |
                      (shots['tag_2'] == 101) |
                      (shots['tag_3'] == 101) |
                      (shots['tag_4'] == 101) |
                      (shots['tag_5'] == 101)]  
    
    return goals




def get_shots(df):
    
    shots = df[(df['eventName'] == 'Shot') |
               (df['subEventName'] == 'Free kick shot')] #6898 tiros totales
    

    
    return shots

def process_shots(df):
    '''
    Versión nueva

    '''
    shots_model = get_shots(df)
    headers = "tag_0 != 403 and tag_1 != 403 and tag_2 != 403 and tag_3 != 403 and tag_4 != 403 and tag_5 != 403"

    shots_model = shots_model.query(headers)

    shots_model['Goal'] = np.where((shots_model['tag_0'] == 101) | 
                          (shots_model['tag_1'] == 101) |
                          (shots_model['tag_2'] == 101) |
                          (shots_model['tag_3'] == 101) |
                          (shots_model['tag_4'] == 101) |
                          (shots_model['tag_5'] == 101), 1, 0)
    

    
    shots_model = shots_model.rename(
        columns={"x_inicio": "X", "y_inicio": "Y"})
    
    shots_model['C'] = abs(shots_model['Y'] - 50)
    
    shots_model['Distance']=np.sqrt((shots_model['X']*105/100)**2 + 
                                    (shots_model['C']*65/100)**2)
    
    ####
    '''
    #alternative method to calculate the angle
    
    #print(row)
    x = 110 - shots_model['X']
    y1 = np.abs(35+7.32/2 - shots_model['Y'])
    y2 = np.abs(35-7.32/2 - shots_model['Y'])
    
    l1 = np.sqrt(x**2 + y1**2)
    l2 = np.sqrt(x**2 + y2**2)
    l3 = 7.32
    
    #angle = np.arccos( (l1**2 + l2**2 - l3**2)/(2*l1*l2) )
    
    shots_model['Angle'] = angle
    shots_model['Angle'] = np.where(angle<0, np.pi+angle, angle)
    '''
    #####
    
    #original method to calculate the angle
    
    a = np.arctan(7.32 *(shots_model['X']*105/100) /
                  ((shots_model['X']*105/100)**2 + (shots_model['C']*65/100)**2 - (7.32/2)**2))
    
    shots_model['Angle'] = np.where(a<0, np.pi+a, a)
            
    #posibles parametros extra
    
    #squaredX = shots_model['X']**2
    #shots_model = shots_model.assign(X2=squaredX)
    #squaredC = shots_model['C']**2
    #shots_model = shots_model.assign(C2=squaredC)
    #AX = shots_model['Angle']*shots_model['X']
    #shots_model = shots_model.assign(AX=AX)
    shots_model['Goal'] = shots_model['Goal'].astype(str)
    
    return shots_model

def model_xg(shots_model,  model_variables = ['Angle', 'Distance']):
    '''
    
    '''
    
    model=''
    for v in model_variables[:-1]:
        model = model  + v + ' + '
    model = model + model_variables[-1]
    
    #Fit the model
    test_model = smf.glm(formula="Goal ~ " + model, data=shots_model, 
                               family=sm.families.Binomial()).fit()
    model_summary = test_model.summary()     
    b=test_model.params
    
    
    return model_summary, b


def calculate_xG(sh, model_params, model_variables = ['Angle', 'Distance']):
    '''
    Recibe un tiro (renglon del df) y calcula el xg

    '''
    b = model_params
    
    bsum=b[0]
    for i,v in enumerate(model_variables):
        bsum=bsum+b[i+1]*sh[v]
    xG = 1/(1+np.exp(bsum)) 
    
    return xG 

def plot_xg(model_params):
    #Create a 2D map of xG

    pgoal_2d=np.zeros((65,65))
    for x in range(65):
        for y in range(65):
            sh=dict()
            a = np.arctan(7.32 *x /(x**2 + abs(y-65/2)**2 - (7.32/2)**2))
            if a<0:
                a = np.pi + a
            sh['Angle'] = a
            sh['Distance'] = np.sqrt(x**2 + abs(y-65/2)**2)
            sh['D2'] = x**2 + abs(y-65/2)**2
            sh['X'] = x
            sh['AX'] = x*a
            sh['X2'] = x**2
            sh['C'] = abs(y-65/2)
            sh['C2'] = (y-65/2)**2
            
            pgoal_2d[x,y] =  calculate_xG(sh, model_params)

    (fig,ax) = FCPython.createGoalMouth()
    pos=ax.imshow(pgoal_2d, extent=[-1,65,65,-1], aspect='auto',cmap=plt.cm.Reds,vmin=0, vmax=0.3)
    fig.colorbar(pos, ax=ax)
    ax.set_title('Probability of goal')
    plt.xlim((0,66))
    plt.ylim((-3,35))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

#
# EJEMPLO 
#

df = pd.read_csv('./../../data/wyscout_tabular/events_World_Cup.csv')

shots_model = process_shots(df)#

###



###

model_summary, b = model_xg(shots_model)

shots_model['xG'] = shots_model.apply(lambda x: calculate_xG(x, b), axis=1) 

print(model_summary)
plot_xg(b)

import seaborn as sns
sns.scatterplot(data = shots_model, x = 'X', y = 'Y', hue='xG')





