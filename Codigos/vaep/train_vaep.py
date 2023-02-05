import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
from catboost import CatBoostClassifier, Pool


from vaep.complex_features import calc_complex_feat
from vaep.convert_spadl import convert_spadl

from utils.is_local import asignar_localia, extraer_locales, datos_partidos

df_1 = pd.read_csv('./../data/wyscout_tabular/events_World_Cup.csv')
df_2 = pd.read_csv('./../data/wyscout_tabular/england.csv')
df_3 = pd.read_csv('./../data/wyscout_tabular/spain.csv')
df_4 = pd.read_csv('./../data/wyscout_tabular/germany.csv')
df_5 = pd.read_csv('./../data/wyscout_tabular/france.csv')
df_6 = pd.read_csv('./../data/wyscout_tabular/italy.csv')


partidos_1 = datos_partidos(r".\..\data\wyscout\Matches\matches_England.json")
partidos_2 = datos_partidos(
    r".\..\data\wyscout\Matches\matches_European_Championship.json")
partidos_3 = datos_partidos(r".\..\data\wyscout\Matches\matches_France.json")
partidos_4 = datos_partidos(r".\..\data\wyscout\Matches\matches_Germany.json")
partidos_5 = datos_partidos(r".\..\data\wyscout\Matches\matches_Italy.json")
partidos_6 = datos_partidos(r".\..\data\wyscout\Matches\matches_Spain.json")
partidos_7 = datos_partidos(
    r".\..\data\wyscout\Matches\matches_World_Cup.json")

partidos = [partidos_1, partidos_2, partidos_3,
            partidos_4, partidos_5, partidos_6, partidos_7]
partidos = pd.concat(partidos)

teams = datos_partidos(r".\..\data\teams.json")

dfs = [df_1, df_2, df_3, df_4, df_5, df_6]

df = pd.concat(dfs)
df = df_2

df = df[df['eventName'] != 'Goalkeeper leaving line']
df = df[df['eventName'] != 'Save attempt']
df = df[df['eventName'] != 'Interruption']


def flip_data(df):
    df.loc[df['is_local'] == 0, 'x_inicio'] = 100 - df['x_inicio']
    df.loc[df['is_local'] == 0, 'x_fin'] = 100 - df['x_fin']

    return df


def transf_shots(df):

    tags = ['tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']

    for tag in tags:
        df.loc[df[tag] == 101, 'x_fin'] = 100
        df.loc[df[tag] == 101, 'y_fin'] = 50

    return df


localia = extraer_locales(partidos, teams)
df['is_local'] = df.apply(lambda x: asignar_localia(x.matchId, x.teamId, localia),
                          axis=1)

#df = df[df['is_local'] == 1]
df = transf_shots(df)
df = flip_data(df)


'''
Script dedicated to process data and 

to-do: 
    - lo de que estén  (PARECE QUE SI ESTÁN INVERTIDOS)
      - talvez hay que reinvertirlas
                                                   
                                                   ')

'''

df_spadl = convert_spadl(df)
#df_spadl['matchId'] = df['matchId']
#df_spadl['matchPeriod'] = df['matchPeriod']
#df_spadl['eventSec'] = df['eventSec']
#df_spadl['eventSec'] = df['eventSec']


df_complex = calc_complex_feat(df)

df_proc = pd.concat([df_spadl, df_complex], axis=1)
df_proc['id'] = df['id']  # .reset_index()}


def transf_train_data(df_proc, s_size=3, k=10):
    '''
    '''
    df_states = pd.DataFrame()

    # df_proc = df_proc.sort_values(by=)

    # shift de datos
    for i in range(s_size):
        df_temp = df_proc.shift(i)

        # add the number of iteration to each event of the action
        suffix = "_" + str(i)
        df_temp = df_temp.add_suffix(suffix)

        df_states = pd.concat([df_states, df_temp], axis=1)

    # unir datos (dejar)

    # calcular labels, si está un gol en los siguientes 10 datos (mientras que el partido sea el mismo)

    return df_states

'''
def get_labels(df, k=10):
    #se usa el df original

    #luego se une con los datos ya listos

    tags = ['tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']
    tags_lag = ['tag_0_lag', 'tag_1_lag', 'tag_2_lag',
                'tag_3_lag', 'tag_4_lag', 'tag_5_lag']

    df['label'] = 0

    for i in range(1, k+1):  # buscar gol en las siguientes 10 acciones
        df[tags_lag] = df[tags].shift(i)

        for tag in tags_lag:
            #condition = ((df[tag] == 101) &
            #             (df['is_local'] == 1)
            #             )  
            
            #df['label'] = np.where(condition, 1,0)
            df.loc[df[tag] == 101, 'label'] = 1
            
    #df.loc[df['is_local'] == 0, 'label'] = 0
    #df.loc[df[tag].isin(fail_tags), 'succesful'] = 0

    return df[['id', 'label']]
'''

def get_labels(df, k=10):
    
    df['label'] = 0
    df.loc[df['local_goal'] == 1, 'label'] = 1
    
    for i in range(1, k+1):  # buscar gol en las siguientes 10 acciones
        df['goal_lag'] = df['local_goal'].shift(i)
        
        df.loc[df['goal_lag'] == 1, 'label'] = 1
        
    return df[['id', 'label']]
    

def get_local_goals(df):
    
    tags = ['tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5']
    
    df['local_goal'] = 0
    
    for tag in tags:
        df.loc[ ((df[tag] == 101) & (df['is_local'] == 1 )), 'local_goal'] = 1
    
    
    return df['local_goal']

##
# make training data
##
df_proc = df_proc.drop(
    columns=['player', 'team'])

train_df = transf_train_data(df_proc)

# extra

#labels_df = get_labels(df)

#
# train data
#

train_data = pd.get_dummies(train_df)
df['local_goal'] = get_local_goals(df)
train_labels = get_labels(df)  # ['label']


all_data = (train_data.merge(train_labels, left_on='id_2', right_on='id')
            .drop(columns=['id_0', 'id_1', 'id_2', 'id'])
            .sort_values(by='label', ascending=False)
    )

train_data = all_data.loc[:, all_data.columns != 'label']
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


probs = pd.DataFrame(preds_proba, columns=['prob_0', 'prob_1'])
# probs['id'] =
probs['class'] = preds_class
probs['label'] = train_labels


class_1 = probs[probs['label'] == 1]
class_1['correct'] = 0
class_1.loc[class_1['label'] == class_1['class'], 'correct'] = 1

print(class_1['correct'].sum()/class_1['correct'].count())


###############################################################################
###############################################################################

feat_imp_df = pd.DataFrame({'feature_importance': model.get_feature_importance(),
                            'feature_names': train_data.columns}).sort_values(by=['feature_importance'],
                                                                              ascending=False)

shots = train_data[train_data['action_type_2_Shot'] == 1]

#sns.scatterplot(data=shots, x='start_x_1', y='start_y_1')


#shots = df_3[df_3['eventName'] == 'Shot']
#sns.scatterplot(data = shots, x='x_inicio', y = 'y_inicio')

#
# save results
#
end_results = all_data.reset_index().merge(probs.reset_index(), on='index')


sns.scatterplot(data=probs, x="label", y="prob_1")


x = probs[probs['label'] == 1]
y = probs[probs['label'] == 0]

x['prob_1'] = x['prob_1']*100
y['prob_1'] = y['prob_1']*100

x = x['prob_1']
y = y['prob_1']

plt.hist([x], color=['r'], alpha=0.5)

sns.displot(probs, x="prob_1", hue="label", stat="probability", common_norm=False)

sns.displot(probs[probs['label'] == 1], x="prob_1",  stat="probability", common_norm=False)
sns.displot(probs[probs['label'] == 0], x="prob_1",  stat="probability", common_norm=False)











