import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import model_for_goaldeff
import model_for_stats
import preprocessing

def predict_toto(toto_n, toto_kind):
    train_columns = ['年月日', '節', 'H_勝点', 'H_試合', 'H_勝', 'H_分', 'H_敗', 'H_得点', 'H_失点', 'H_得失点差', 'H_rest_days', 'A_勝点', 'A_試合', 'A_勝', 'A_分', 'A_敗', 'A_得点', 'A_失点', 'A_得失点差', 'A_rest_days', 'J1_flg', 'J2_flg', 'J3_flg', 'H_DF', 'H_MF', 'H_FW', 'A_DF', 'A_MF', 'A_FW', 'H_Team', 'A_Team', 'H_監督', 'A_監督']
    stats_columns = ['H_シュート', 'H_枠内シュート', 'H_PKによるシュート', 'H_直接ＦＫ', 'H_間接ＦＫ', 'H_ＣＫ', 'H_クリア', 'H_インターセプト', 'H_オフサイド', 'H_３０ｍライン進入', 'H_ペナルティエリア進入', 'H_攻撃回数', 'H_チャンス構築率', 'H_ボール支配率', 'A_シュート', 'A_枠内シュート', 'A_PKによるシュート', 'A_直接ＦＫ', 'A_間接ＦＫ', 'A_ＣＫ', 'A_クリア', 'A_インターセプト', 'A_オフサイド', 'A_３０ｍライン進入', 'A_ペナルティエリア進入', 'A_攻撃回数', 'A_チャンス構築率', 'A_ボール支配率', 'H_成功したパス', 'H_失敗したパス', 'H_成功したクロス', 'H_失敗したクロス', 'H_成功したスローイン', 'H_失敗したスローイン', 'H_成功したドリブル', 'H_失敗したドリブル', 'H_成功したタックル', 'H_失敗したタックル', 'A_成功したパス', 'A_失敗したパス', 'A_成功したクロス', 'A_失敗したクロス', 'A_成功したスローイン', 'A_失敗したスローイン', 'A_成功したドリブル', 'A_失敗したドリブル', 'A_成功したタックル', 'A_失敗したタックル']
    drop_columns = ['H_goal', 'A_goal', 'H_result']
    y_column = 'goal_difference'
    
    data = preprocessing.preprocessing(toto_n, toto_kind)
    data.drop(columns = drop_columns, inplace = True)
    
    x_train = data[data['train_test'] == 'train'].drop(columns = [y_column] + ['train_test'])
    x_train, x_val = train_test_split(x_train, train_size=0.80)
    x_test = data[data['train_test'] == 'test'].drop(columns = [y_column] + ['train_test'])
    x_toto = data[data['train_test'] == 'toto'].drop(columns = [y_column] + ['train_test'])
    
    y_train = x_train[stats_columns]
    x_train.drop(columns = stats_columns, inplace = True)
    y_val = x_val[stats_columns]
    x_val.drop(columns = stats_columns, inplace = True)
    y_test = x_test[stats_columns]
    x_test.drop(columns = stats_columns, inplace = True)
    y_toto = x_toto[stats_columns]
    x_toto.drop(columns = stats_columns, inplace = True)
    
    m_stats = model_for_stats.model()
    m_stats.fit(x_train, x_val, x_test, y_train, y_val, y_test)
    y_toto = m_stats.predict(x_toto)
    
    x_train = data[data['train_test'] == 'train'].drop(columns = ['train_test'])
    x_train, x_val = train_test_split(x_train, train_size=0.80)
    x_test = data[data['train_test'] == 'test'].drop(columns = ['train_test'])
    x_toto = pd.concat([x_toto.reset_index(drop = True), y_toto], axis = 1)
    
    y_train = x_train[y_column]
    x_train.drop(columns = [y_column], inplace = True)
    y_val = x_val[y_column]
    x_val.drop(columns = [y_column], inplace = True)
    y_test = x_test[y_column]
    x_test.drop(columns = [y_column], inplace = True)
    
    m_goal = model_for_goaldeff.model()
    m_goal.fit(x_train, x_val, x_test, y_train, y_val, y_test)
    
    y_toto = m_goal.predict(x_toto)
    
    columns = ['第n回', '種別', 'No', '開催日', 'ホーム', 'アウェイ', '試合結果', 'くじ結果']
    df_toto = pd.read_csv("data/marge/toto_info.csv", index_col=0).reset_index(drop = True)
    df_toto = df_toto[(df_toto['第n回'] == toto_n) & (df_toto['種別'] == toto_kind)][columns].reset_index(drop = True)
    
    df_result = pd.concat([df_toto, pd.DataFrame(y_toto, columns = ['rGBM_pred_得失点'])], axis = 1)

    df = pd.read_csv("data/model/toto_pred.csv", index_col=0).reset_index(drop = True)
    df_result = pd.concat([df, df_result])

    df_result.to_csv("data/model/toto_pred.csv")