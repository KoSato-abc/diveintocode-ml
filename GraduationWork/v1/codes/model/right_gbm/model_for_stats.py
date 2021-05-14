import numpy as np
import pandas as pd
import optuna.integration.lightgbm as lgb_o
from sklearn.metrics import mean_squared_error

class model():
    
    def __init__(self):
        self.model_dict = {}
        self.stats_columns = []
        
    def fit(self, x_train, x_val, x_test, y_trains, y_vals, y_tests):
        
        self.stats_columns = y_trains.columns.tolist()
        
        for y_col in self.stats_columns:

            y_train = y_trains[y_col]
            y_val = y_vals[y_col]
            y_test = y_tests[y_col]

            lgb_train = lgb_o.Dataset(x_train, y_train)
            lgb_eval = lgb_o.Dataset(x_val, y_val) 
            # LightGBM parameters
            params = {
                'objective': 'regression', # 回帰  
                'metric': 'rmse', # rsme(平均二乗誤差の平方根) 
            }
            # モデルの学習
            model = lgb_o.train(params,
                              train_set=lgb_train,
                              valid_sets=lgb_eval,
                              early_stopping_rounds=100,
                              verbose_eval=200,
                              )

            self.model_dict[y_col] = model
            
            # テストデータの予測
            y_pred = model.predict(x_test, num_iteration=model.best_iteration)

            # rmse : 平均二乗誤差の平方根
            mse = mean_squared_error(y_test, y_pred) # MSE(平均二乗誤差)の算出
            rmse = np.sqrt(mse) # RSME = √MSEの算出
            print(y_col,' rmse : ', rmse)
        
    def predict(self, x_toto):
        
        result_df = None
        for y_col in self.stats_columns:
            model = self.model_dict[y_col]
            y_pred = model.predict(x_toto, num_iteration=model.best_iteration)
            df = pd.DataFrame(y_pred, columns = [y_col])
            result_df = pd.concat([result_df, df], axis = 1)
        return result_df