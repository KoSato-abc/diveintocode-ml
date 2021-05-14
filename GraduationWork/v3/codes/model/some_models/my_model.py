import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb

def predict_toto(year = None):
    
    data = pd.read_csv('data/model/preprocessing.csv', index_col=0).reset_index(drop = True)
    data = data.sort_values('年月日', ascending=False)
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    y_columns = []
    for col in data.columns:
        if col[:2] == 'y_':
            y_columns += [col]
    
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    toto = data[data['train_test'] == 'toto'].drop(columns = ['train_test'])
    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    toto = toto.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    # trainの引き分けとその他のデータ数を合わせる
    train_0 = train[train['y_H_result'] == 0]
    train_1 = train[train['y_H_result'] == 1]
    train_2 = train[train['y_H_result'] == 2]

    n_row_1_2 = min([train_1.shape[0], train_2.shape[0]])
    n_row = min([train_0.shape[0], n_row_1_2*2])

    train_0 = train_0.iloc[:n_row]
    train_1 = train_1.iloc[:int(n_row/2)]
    train_2 = train_2.iloc[:int(n_row/2)]
    train = pd.concat([train_0, train_1, train_2])
    
    df_result = toto[['年月日', 'H_Team', 'A_Team']]
    
    '''
    得点の回帰(線形回帰)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_H_goal']
    # 学習
    lr = LinearRegression()
    lr.fit(x_train, y_train)
    #評価の実行
    y_toto = lr.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['H_goal_lr'])
    df_result = pd.concat([df_result, df_pred], axis = 1)
    
    '''
    得失点の回帰(線形回帰)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_goal_deff']
    # 学習
    lr = LinearRegression()
    lr.fit(x_train, y_train)
    #評価の実行
    y_toto = lr.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['goal_deff_lr'])
    df_result = pd.concat([df_result, df_pred], axis = 1)
    
    '''
    失点の回帰(線形回帰)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_A_goal']
    # 学習
    lr = LinearRegression()
    lr.fit(x_train, y_train)
    #評価の実行
    y_toto = lr.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['A_goal_lr'])
    df_result = pd.concat([df_result, df_pred], axis = 1)

    '''
    引き分けその他の二値分類(KNeighborsClassifier)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_even_flg']
    # 学習
    model = KNeighborsClassifier(n_neighbors=2)
    model.fit(x_train, y_train)
    #評価の実行
    y_toto = model.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['even_flg_KN'])
    df_result = pd.concat([df_result, df_pred], axis = 1)
    
    '''
    試合結果の三値分類(KNeighborsClassifier)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_H_result']
    # 学習
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(x_train, y_train)
    #評価の実行
    y_toto = model.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['H_result_KN'])
    df_result = pd.concat([df_result, df_pred], axis = 1)
    
    '''
    試合結果の三値分類(XGboost)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_H_result']
    
    dtrain = xgb.DMatrix(x_train, label=y_train)
    dtest = xgb.DMatrix(x_toto)
    
    param = {'objective': 'multi:softmax', 'num_class': 3}
    
    # 学習
    bst = xgb.train(param, dtrain, 1000)
    
    #評価の実行
    y_toto = bst.predict(dtest)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['H_result_XG'])
    df_result = pd.concat([df_result, df_pred], axis = 1)
    
    '''
    引き分けその他の二値分類(XGboost)
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_even_flg']
    
    dtrain = xgb.DMatrix(x_train, label=y_train)
    dtest = xgb.DMatrix(x_toto)
    
    param = {'objective': 'multi:softmax', 'num_class': 2}
    
    # 学習
    bst = xgb.train(param, dtrain, 1000)
    
    #評価の実行
    y_toto = bst.predict(dtest)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['even_flg_XG'])
    df_result = pd.concat([df_result, df_pred], axis = 1)
    
    return df_result