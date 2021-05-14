import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# import preprocessing
from . import rightgbm_category
from . import rightgbm_regression

def predict_toto(year = None):
    
    acuracy_val_list = []
    acuracy_title_list = []
    
    model_category =  rightgbm_category.rightgbm_category()
    model_regression =  rightgbm_regression.rightgbm_regression()
    
    data = pd.read_csv('data/model/preprocessing.csv', index_col=0).reset_index(drop = True)
    data = data.sort_values('年月日', ascending=False)
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    y_columns = []
    for col in data.columns:
        if col[:2] == 'y_':
            y_columns += [col]
    
    '''
    引き分け、その他の二値分類
    '''
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    test = data[data['train_test'] == 'test'].drop(columns = ['train_test'])
    toto = data[data['train_test'] == 'toto'].drop(columns = ['train_test'])
    if test.shape[0] == 0:
        train, test = train_test_split(train, test_size=0.05)
    
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
    
    # trainとvalに分ける
    train, val = train_test_split(train, train_size=0.8)

    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    val = val.sort_values('年月日', ascending=False).reset_index(drop = True)
    test = test.sort_values('年月日', ascending=False).reset_index(drop = True)
    toto = toto.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_val = val.drop(columns = y_columns)
    x_test = test.drop(columns = y_columns)
    x_toto = toto.drop(columns = y_columns)
    y_train = train['y_even_flg']
    y_val = val['y_even_flg']
    y_test = test['y_even_flg']
    
    df_result = x_toto[['年月日', 'H_Team', 'A_Team']]
    
    # 学習
    y_pred, y_pred_proba, accuracy = model_category.fit(x_train, x_val, x_test, y_train, y_val, y_test, 2, year, 'is_even_lgbm')
    # 予測
    y_toto, y_toto_proba = model_category.predict(x_toto)
    
    df_pred_even = pd.DataFrame(y_toto, columns = ['is_even_lgbm'])
    df_pred_even_prova = pd.DataFrame(y_toto_proba, columns = ['is_even_0_1_lgbm', 'is_even_1_1_lgbm'])
    df_pred_even_prova['is_even_lgbm_acc'] = accuracy
    df_result = pd.concat([df_result, df_pred_even, df_pred_even_prova], axis = 1)
    acuracy_val_list += [accuracy]
    acuracy_title_list += ['is_even_lgbm']
    
    '''
    勝敗の二値分類
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    test = data[data['train_test'] == 'testa'].drop(columns = ['train_test'])
    if test.shape[0] == 0:
        train, test = train_test_split(train, test_size=0.05)
    
    # trainの勝敗のみを使用
    train = train[train['y_H_result'] != 0]
    
    # trainとvalに分ける
    train, val = train_test_split(train, train_size=0.8)

    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    val = val.sort_values('年月日', ascending=False).reset_index(drop = True)
    test = test.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    train['y_H_result'] = train['y_H_result'] -1
    val['y_H_result'] = val['y_H_result'] -1
    test['y_H_result'] = test['y_H_result'] -1
    
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_val = val.drop(columns = y_columns)
    x_test = test.drop(columns = y_columns)
    y_train = train['y_H_result']
    y_val = val['y_H_result']
    y_test = test['y_H_result']
    
    # 学習
    y_pred, y_pred_proba, accuracy = model_category.fit(x_train, x_val, x_test, y_train, y_val, y_test, 2, year, 'is_lose_lgbm')
    # 予測
    y_toto, y_toto_proba = model_category.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['is_lose_lgbm'])
    df_pred_prova = pd.DataFrame(y_toto_proba, columns = ['is_lose_0_1_lgbm', 'is_lose_1_1_lgbm'])
    df_pred_prova['is_lose_lgbm_acc'] = accuracy
    df_result = pd.concat([df_result, df_pred, df_pred_prova], axis = 1)
    acuracy_val_list += [accuracy]
    acuracy_title_list += ['is_lose_lgbm']
    
    '''
    勝分敗の3値分類
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    test = data[data['train_test'] == 'testa'].drop(columns = ['train_test'])
    if test.shape[0] == 0:
        train, test = train_test_split(train, test_size=0.05)
        
    # trainとvalに分ける
    train, val = train_test_split(train, train_size=0.8)

    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    val = val.sort_values('年月日', ascending=False).reset_index(drop = True)
    test = test.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_val = val.drop(columns = y_columns)
    x_test = test.drop(columns = y_columns)
    y_train = train['y_H_result']
    y_val = val['y_H_result']
    y_test = test['y_H_result']
    
    # 学習
    y_pred, y_pred_proba, accuracy = model_category.fit(x_train, x_val, x_test, y_train, y_val, y_test, 3, year, 'w_e_l_lgbm')
    # 予測
    y_toto, y_toto_proba = model_category.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['w_e_l_lgbm'])
    df_pred_prova = pd.DataFrame(y_toto_proba, columns = ['w_e_l_0_2_lgbm', 'w_e_l_1_2_lgbm', 'w_e_l_2_2_lgbm'])
    df_pred_prova['w_e_l_lgbm_acc'] = accuracy
    df_result = pd.concat([df_result, df_pred, df_pred_prova], axis = 1)
    acuracy_val_list += [accuracy]
    acuracy_title_list += ['w_e_l_lgbm']
    
    '''
    得失点の回帰
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    test = data[data['train_test'] == 'testa'].drop(columns = ['train_test'])
    if test.shape[0] == 0:
        train, test = train_test_split(train, test_size=0.05)
        
    # trainとvalに分ける
    train, val = train_test_split(train, train_size=0.8)

    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    val = val.sort_values('年月日', ascending=False).reset_index(drop = True)
    test = test.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_val = val.drop(columns = y_columns)
    x_test = test.drop(columns = y_columns)
    y_train = train['y_goal_deff']
    y_val = val['y_goal_deff']
    y_test = test['y_goal_deff']
    
    # 学習
    y_pred, rmse = model_regression.fit(x_train, x_val, x_test, y_train, y_val, y_test, year, 'goal_deff_lgbm')
    # 予測
    y_toto = model_regression.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['goal_deff_lgbm'])
    df_pred['goal_deff_lgbm_rmse'] = rmse
    df_result = pd.concat([df_result, df_pred], axis = 1)
    acuracy_val_list += [rmse]
    acuracy_title_list += ['goal_deff_lgbm']
    
    '''
    得点の回帰
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    test = data[data['train_test'] == 'testa'].drop(columns = ['train_test'])
    if test.shape[0] == 0:
        train, test = train_test_split(train, test_size=0.05)
        
    # trainとvalに分ける
    train, val = train_test_split(train, train_size=0.8)

    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    val = val.sort_values('年月日', ascending=False).reset_index(drop = True)
    test = test.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_val = val.drop(columns = y_columns)
    x_test = test.drop(columns = y_columns)
    y_train = train['y_H_goal']
    y_val = val['y_H_goal']
    y_test = test['y_H_goal']
    
    # 学習
    y_pred, rmse = model_regression.fit(x_train, x_val, x_test, y_train, y_val, y_test, year, 'H_goal_lgbm')
    # 予測
    y_toto = model_regression.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['H_goal_lgbm'])
    df_pred['H_goal_lgbm_rmse'] = rmse
    df_result = pd.concat([df_result, df_pred], axis = 1)
    acuracy_val_list += [rmse]
    acuracy_title_list += ['H_goal_lgbm']
    
    '''
    失点の回帰
    '''
    # y_columns = ['y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    # train、test、totoに分ける
    train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    test = data[data['train_test'] == 'testa'].drop(columns = ['train_test'])
    if test.shape[0] == 0:
        train, test = train_test_split(train, test_size=0.05)
        
    # trainとvalに分ける
    train, val = train_test_split(train, train_size=0.8)

    train = train.sort_values('年月日', ascending=False).reset_index(drop = True)
    val = val.sort_values('年月日', ascending=False).reset_index(drop = True)
    test = test.sort_values('年月日', ascending=False).reset_index(drop = True)
    
    # x_とy_に分ける
    x_train = train.drop(columns = y_columns)
    x_val = val.drop(columns = y_columns)
    x_test = test.drop(columns = y_columns)
    y_train = train['y_A_goal']
    y_val = val['y_A_goal']
    y_test = test['y_A_goal']
    
    # 学習
    y_pred, rmse = model_regression.fit(x_train, x_val, x_test, y_train, y_val, y_test, year, 'A_goal_lgbm')
    # 予測
    y_toto = model_regression.predict(x_toto)
    # 結果を保存
    df_pred = pd.DataFrame(y_toto, columns = ['A_goal_lgbm'])
    df_pred['A_goal_lgbm_rmse'] = rmse
    df_result = pd.concat([df_result, df_pred], axis = 1)
    acuracy_val_list += [rmse]
    acuracy_title_list += ['A_goal_lgbm']
    
#     df_result.drop(columns = ['even_1_lgbm', 'wl_1_lgbm', 'wel_2_lgbm'])
    df_acuracy = pd.DataFrame([acuracy_val_list], columns = acuracy_title_list).T
    return df_result, df_acuracy