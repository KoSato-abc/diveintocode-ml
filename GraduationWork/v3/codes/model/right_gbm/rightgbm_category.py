import numpy as np
import pandas as pd
import optuna.integration.lightgbm as lgb_o
from sklearn.metrics import mean_squared_error
import pickle

class rightgbm_category:
    
    def fit(self, x_train, x_val, x_test, y_train, y_val, y_test, num_class, year,  title):
        
        do_fit = True
        if year is None:
            pass
        else:
            f_name = 'data/model/right_gbm/' + year + '_' + title + '_' + 'rightgbm_category.sav'
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
                'objective': 'multiclass',
                'metric': 'multi_logloss',
                'num_class': num_class,
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

        y_pred_proba = self.model.predict(x_test, num_iteration=self.model.best_iteration)
        y_pred = np.argmax(y_pred_proba, axis=1)

        # Accuracy の計算
        accuracy = sum(y_test == y_pred) / len(y_test)
        print('accuracy:', accuracy)
        
        return y_pred, y_pred_proba, accuracy
    
    def predict(self, x_toto):
        y_pred_proba = self.model.predict(x_toto, num_iteration=self.model.best_iteration)
        y_pred = np.argmax(y_pred_proba, axis=1)
        return y_pred, y_pred_proba