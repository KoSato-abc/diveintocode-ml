import numpy as np
import pandas as pd
import optuna.integration.lightgbm as lgb_o
from sklearn.metrics import mean_squared_error
import pickle

class rightgbm_regression:
    
    def fit(self, x_train, x_val, x_test, y_train, y_val, y_test, year,  title):
        
        do_fit = True
        if year is None:
            pass
        else:
            f_name = 'data/model/right_gbm/' + year + '_' + title + '_' + 'rightgbm_regression.sav'
            try:
                self.model = pickle.load(open(f_name, 'rb'))
                do_fit = False
            except:
                do_fit = True

        if do_fit:
            lgb_train = lgb_o.Dataset(x_train, y_train)
            lgb_eval = lgb_o.Dataset(x_val, y_val) 
            # 学習用パラメータ
            lgbm_params = {
                'objective': 'regression', # 回帰  
                'metric': 'rmse', # rsme(平均二乗誤差の平方根) 
                 'verbosity': -1
            }
            # 学習
            model = lgb_o.train(lgbm_params,
                            lgb_train,
                            valid_sets=lgb_eval,
                            early_stopping_rounds=100,
                            verbose_eval=200,)
            self.model = model
            # 保存
            pickle.dump(self.model, open(f_name, 'wb'))

        # テストデータの予測
        y_pred = self.model.predict(x_test, num_iteration=self.model.best_iteration)

        # rmse : 平均二乗誤差の平方根
        mse = mean_squared_error(y_test, y_pred) # MSE(平均二乗誤差)の算出
        rmse = np.sqrt(mse) # RSME = √MSEの算出
        print('rmse : ', rmse)
        
        return y_pred, rmse
    
    def predict(self, x_toto):
        y_pred = self.model.predict(x_toto, num_iteration=self.model.best_iteration)
        return y_pred