import numpy as np
import pandas as pd
import optuna.integration.lightgbm as lgb_o
from sklearn.metrics import mean_squared_error

from . import preprocessing
from .right_gbm import my_model as my_right_gbm
from sklearn.model_selection import train_test_split

def pred_toto(toto_n, toto_kind, pred_par_day = False):

    df_toto_preds = get_y_preds(toto_n, toto_kind, pred_par_day)
    yyyyMMdd = df_toto_preds.min(axis=0)['開催日']

    if pred_par_day:
        df_y_preds = pd.read_csv('data/model/y_preds_par_day.csv', index_col=0).reset_index(drop = True)
    else:
        df_y_preds = pd.read_csv('data/model/y_preds_par_year.csv', index_col=0).reset_index(drop = True)
    df_y_preds = df_y_preds[df_y_preds['開催日'] < yyyyMMdd]

    df_toto = pd.read_csv('data/marge/toto_info.csv', index_col=0).reset_index(drop = True)
    df_toto = df_toto[['第n回', '種別', '開催日', 'ホーム', 'アウェイ', 'くじ結果'] ]
    df_toto = df_toto[df_toto['くじ結果'] != '102'].reset_index(drop = True)

    drop_columns = ['第n回', '種別','is_even_1_1_lgbm', 'is_lose_1_1_lgbm', 'w_e_l_2_2_lgbm' ]
    train = pd.merge(df_y_preds, df_toto).drop(columns = drop_columns)
    test = df_toto_preds.drop(columns = drop_columns)

    train = preprocessing.team_to_index(train, 'ホーム')
    train = preprocessing.team_to_index(train, 'アウェイ')
    test = preprocessing.team_to_index(test, 'ホーム')
    test = preprocessing.team_to_index(test, 'アウェイ')

    category_columns = ['ホーム', 'アウェイ']
    for column in category_columns:
        train[column] = pd.Series(train[column]).astype('category')
        test[column] = pd.Series(test[column]).astype('category')

    train, val = train_test_split(train, train_size=0.8)

    x_train = train.drop(columns = ['くじ結果'])
    y_train = train['くじ結果'].values
    x_val = val.drop(columns = ['くじ結果'])
    y_val = val['くじ結果'].values
    x_test = test

    model = model_toto()
    model.fit(x_train, x_val, y_train, y_val)
    y_pred, y_pred_proba = model.predict(x_test)

    df_pred = pd.DataFrame(y_pred_proba, columns=['分', '勝', '敗'])
    df_toto = x_test[['開催日', 'ホーム', 'アウェイ']]
    df_result = pd.concat([df_pred, df_toto], axis=1)
    df_result = preprocessing.index_to_team(df_result, 'ホーム')
    df_result = preprocessing.index_to_team(df_result, 'アウェイ')

    df_result = df_result.reindex(columns=['開催日', 'ホーム', 'アウェイ', '勝', '敗', '分'])

    return df_result

def get_y_preds(toto_n, toto_kind, pred_par_day = False):
    
    if pred_par_day:
    
        # 前処理
        preprocessing.preprocessing(toto_n, toto_kind, pred_par_day)

        # 予測値を算出
        df_result, df_acuracy = my_right_gbm.predict_toto()
        df_result = preprocessing.index_to_team(df_result, 'H_Team')
        df_result = preprocessing.index_to_team(df_result, 'A_Team')
        df_result['toto_n'] = toto_n
        df_result['toto_kind'] = toto_kind

        # 結果を整形
        df_y_preds = pd.read_csv('data/model/y_preds_par_day.csv', index_col=0).reset_index(drop = True)
        df_toto = pd.read_csv('data/marge/toto_info.csv', index_col=0).reset_index(drop = True)
        df_toto = df_toto[['第n回', '種別', '開催日', 'ホーム', 'アウェイ']]

        df_marge = pd.merge(df_toto, df_result, 
                     left_on=['第n回', '種別', 'ホーム'],
                     right_on=['toto_n', 'toto_kind', 'H_Team']).drop(columns = ['H_Team', 'A_Team', '年月日', 'toto_n', 'toto_kind'])

        df_y_preds = pd.concat([df_y_preds, df_marge]).reset_index(drop = True)
        df_y_preds.to_csv("data/model/y_preds_par_day.csv")
        
        return df_marge
    else:
        # 前処理
        df = preprocessing.preprocessing(toto_n, toto_kind, pred_par_day)
        yyyyMMdd = df[df['train_test'] == 'toto'].iloc[:1]['年月日'].values[0]
        year = str(yyyyMMdd)[:4]
        # 予測値を算出
        df_result, df_acuracy = my_right_gbm.predict_toto(year)
        df_result = preprocessing.index_to_team(df_result, 'H_Team')
        df_result = preprocessing.index_to_team(df_result, 'A_Team')
        df_result['toto_n'] = toto_n
        df_result['toto_kind'] = toto_kind

        # 結果を整形
        df_y_preds = pd.read_csv('data/model/y_preds_par_year.csv', index_col=0).reset_index(drop = True)
        df_toto = pd.read_csv('data/marge/toto_info.csv', index_col=0).reset_index(drop = True)
        df_toto = df_toto[['第n回', '種別', '開催日', 'ホーム', 'アウェイ']]

        df_marge = pd.merge(df_toto, df_result, 
                     left_on=['第n回', '種別', 'ホーム'],
                     right_on=['toto_n', 'toto_kind', 'H_Team']).drop(columns = ['H_Team', 'A_Team', '年月日', 'toto_n', 'toto_kind'])

        df_y_preds = pd.concat([df_y_preds, df_marge]).reset_index(drop = True)
        df_y_preds.to_csv("data/model/y_preds_par_year.csv")
        
        return df_marge
    
class model_toto:
    
    def fit(self, x_train, x_val, y_train, y_val):
        
        lgb_train = lgb_o.Dataset(x_train, y_train)
        lgb_eval = lgb_o.Dataset(x_val, y_val) 
        # 学習用パラメータ
        lgbm_params = {
            'objective': 'multiclass',
            'metric': 'multi_logloss',
            'num_class': 3,
            'verbosity': -1
        }
        # 学習
        model = lgb_o.train(lgbm_params,
                        lgb_train,
                        valid_sets=lgb_eval,
                        early_stopping_rounds=100,
                        verbose_eval=200,)
        self.model = model

        y_pred_proba = self.model.predict(x_val, num_iteration=self.model.best_iteration)
        y_pred = np.argmax(y_pred_proba, axis=1)

        # Accuracy の計算
        accuracy = sum(y_val == y_pred) / len(y_val)
        print('accuracy:', accuracy)
        
        return y_pred, y_pred_proba, accuracy
    
    def predict(self, x_test):
        y_pred_proba = self.model.predict(x_test, num_iteration=self.model.best_iteration)
        y_pred = np.argmax(y_pred_proba, axis=1)
        return y_pred, y_pred_proba