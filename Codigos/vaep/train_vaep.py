import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
from catboost import CatBoostClassifier, Pool


from complex_features import calc_complex_feat
from convert_spadl import convert_spadl

df_1 = pd.read_csv('./../../data/wyscout_tabular/events_World_Cup.csv')
df_2 = pd.read_csv('./../../data/wyscout_tabular/england.csv')
df_3 = pd.read_csv('./../../data/wyscout_tabular/spain.csv')
df_4 = pd.read_csv('./../../data/wyscout_tabular/germany.csv')
df_5 = pd.read_csv('./../../data/wyscout_tabular/france.csv')
df_6 = pd.read_csv('./../../data/wyscout_tabular/italy.csv')

dfs = [df_1, df_2, df_3, df_4, df_5, df_6]

df = pd.concat(dfs)
df = df_2

'''
Script dedicated to process data and 

to-do: 
    - lo de que estén invertidos
    - que estén solo las columnas que nos importan(hay un par de id's que hay que quitar
                                                   
                                                   ')

'''

df_spadl = convert_spadl(df)
#df_spadl['matchId'] = df['matchId']
#df_spadl['matchPeriod'] = df['matchPeriod']
#df_spadl['eventSec'] = df['eventSec']
#df_spadl['eventSec'] = df['eventSec']


df_complex = calc_complex_feat(df)

df_proc = pd.concat([df_spadl, df_complex], axis = 1)
df_proc['id'] = df['id'] #.reset_index()


def transf_train_data(df_proc, s_size = 3, k=10):
    '''
    '''
    df_states = pd.DataFrame()
    
    #df_proc = df_proc.sort_values(by=)
    
    #shift de datos
    for i in range(s_size):
        df_temp = df_proc.shift(i)
        
        suffix = "_" + str(i) #add the number of iteration to each event of the action
        df_temp = df_temp.add_suffix(suffix)
        
        df_states = pd.concat([df_states, df_temp], axis = 1)
    
    #unir datos (dejar)
    
    #calcular labels, si está un gol en los siguientes 10 datos (mientras que el partido sea el mismo)
    
    return df_states

def get_labels(df, k = 10):
    '''
    se usa el df original
    
    luego se une con los datos ya listos
    '''
    
    tags = ['tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']
    tags_lag = ['tag_0_lag', 'tag_1_lag', 'tag_2_lag', 'tag_3_lag', 'tag_4_lag', 'tag_5_lag']
    
    df['label'] = 0
    
    for i in range(1,k+1): #buscar gol en las siguientes 10 acciones
        df[tags_lag] = df[tags].shift(i)
        
        for tag in tags_lag:
            df.loc[df[tag] == 101, 'label'] = 1
    
    #df.loc[df[tag].isin(fail_tags), 'succesful'] = 0
    
    return df[['id','label']]

##
## make training data
##
df_proc = df_proc.drop(columns = ['player', 'team'])

train_df = transf_train_data(df_proc)
#labels_df = get_labels(df)

#
# train data
#

train_data = pd.get_dummies(train_df)
train_labels = get_labels(df)#['label']

all_data = train_data.merge(train_labels, left_on='id_2', right_on='id').drop(columns = ['id_0', 'id_1', 'id_2', 'id'] )

train_data = all_data.loc[:, all_data.columns!='label']
train_labels = all_data['label']

test_data = catboost_pool = Pool(train_data, 
                                 train_labels)

model = CatBoostClassifier(iterations=2,
                           depth=2,
                           learning_rate=1,
                           loss_function='Logloss',
                           verbose=True)

model.fit(train_data, train_labels)
# make the prediction using the resulting model
preds_class = model.predict(test_data)
preds_proba = model.predict_proba(test_data)
print("class = ", preds_class)
print("proba = ", preds_proba)


probs = pd.DataFrame(preds_proba, columns = ['prob_0', 'prob_1'])
#probs['id'] = 
probs['class'] = preds_class
probs['label'] = train_labels

class_1 = probs[probs['label'] == 1]
class_1['correct'] = 0
class_1.loc[class_1['label'] == class_1['class'], 'correct'] = 1

print(class_1['correct'].sum()/class_1['correct'].count())



###############################################################################

feat_imp_df = pd.DataFrame({'feature_importance': model.get_feature_importance(), 
              'feature_names': train_data.columns}).sort_values(by=['feature_importance'], 
                                                           ascending=False)



