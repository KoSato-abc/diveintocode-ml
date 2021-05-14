from codes.model import my_model_for_toto as my_model
import numpy as np
import pandas as pd
import pickle

def get_toto_sim(toto_n, toto_kind):

    if toto_kind == 'toto':
        f_name = 'toto_dic.sav'
    elif toto_kind == 'mini toto-A組':
        f_name = 'toto_miniA_dic.sav'
    else:
        f_name = 'toto_miniB_dic.sav'

    try:
        toto_dic = pickle.load(open('data/simulation_toto/' + f_name, 'rb'))
    except:
        toto_dic = {}
    
    if toto_n in toto_dic:
        toto_sim = toto_dic[toto_n]
    else:
        toto_sim = toto_simulator(toto_n, toto_kind)
        toto_dic[toto_n] = toto_sim
        pickle.dump(toto_dic, open('data/simulation_toto/' + f_name, 'wb'))
    return toto_sim
    
class toto_simulator():
    
    def __init__(self, toto_n, toto_kind):
        self.toto_n = toto_n
        self.toto_kind = toto_kind
        self.df_pred = my_model.pred_toto(self.toto_n, self.toto_kind)
        
    def show_df(self):
        df_toto = pd.read_csv('data/marge/toto_info.csv', index_col=0).reset_index(drop = True)

        df_toto = df_toto[['第n回', '開催日', '種別', 'ホーム', 'アウェイ', 'くじ結果']]
        df_toto = df_toto[(df_toto['種別'] == self.toto_kind) & (df_toto['第n回'] == self.toto_n)]

        df_result = pd.merge(df_toto, self.df_pred, how = 'left')
        
        columns = ['第n回', '開催日', '種別', 'ホーム', 'アウェイ','分', '勝', '敗', 'くじ結果',]
        df_result = df_result.reindex(columns=columns)
        return df_result.rename(columns={'勝': '勝(1)', '敗': '敗(2)', '分': '分(0)'})
        
    def get_buy_list(self, toto_funds):
        
        pred_list = np.array(self.df_pred[['分', '勝', '敗']].values)
        buy_list = np.array(np.zeros([len(pred_list),3]))
    
        # 各試合で予測確率が最大のものを購入
        for i in range(len(pred_list)):
            max_idx = np.argmax(pred_list[i])
            pred_list[i][max_idx] = 0
            buy_list[i][max_idx] = 1
        purchase_price, _, _, _ = self.calc_purchase_price(buy_list.copy())

        continue_buy_flg = True
        while continue_buy_flg:
            # 新たに購入
            new_pred_list, new_buy_list = self.buy_one_more(pred_list, buy_list)
            
            # 購入金額を算出
            new_purchase_price, single, double, triple = self.calc_purchase_price(new_buy_list)
            
            # さらに購入できるかをチェック
            continue_buy_flg = self.check_continue(new_purchase_price, single, double, triple, toto_funds)
            
            if continue_buy_flg:
                pred_list = new_pred_list.copy()
                buy_list = new_buy_list.copy()
                purchase_price = new_purchase_price
                
        df_buy = pd.concat([self.df_pred.copy(), pd.DataFrame(buy_list)], axis = 1)
        df_buy.drop(columns = ['勝', '敗', '分'], inplace = True)
        
        return df_buy, purchase_price
                
    def buy_one_more(self, pred_list, buy_list):
        pred_list, buy_list = pred_list.copy(), buy_list.copy()
        max_val = pred_list.max()
        for i in range(len(pred_list)):
            if max_val == pred_list[i].max():
                max_idx = np.argmax(pred_list[i])
                pred_list[i][max_idx] = 0
                buy_list[i][max_idx] = 1
        return pred_list, buy_list
    
    def check_continue(self, purchase_price, single, double, triple, toto_funds):
        if toto_funds < purchase_price:
            return False
        
        if self.toto_kind[:4] == 'toto':
            if double == 0:
                if 5 < triple:
                    return False
            elif double == 1:
                if 4 < triple:
                    return False
            elif double == 2:
                if 4 < triple:
                    return False
            elif double == 3:
                if 3 < triple:
                    return False
            elif double == 4:
                if 3 < triple:
                    return False
            elif double == 5:
                if 2 < triple:
                    return False
            elif double == 6:
                if 1 < triple:
                    return False
            elif double == 7:
                if 1 < triple:
                    return False
            elif double == 8:
                if 0 < triple:
                    return False
            else:
                return False
        else:
             if 5 == triple:
                return False
        return True
    
    def calc_purchase_price(self, buy_list):
        single = 0
        double = 0
        triple = 0
        for row in buy_list:
            count_buy = np.sum(row)

            if count_buy == 1:
                single+=1
            elif count_buy == 2:
                double +=1
            else:
                triple += 1
        purchase_price = 100*(2**double)*(3**triple)

        return purchase_price, single, double, triple
    
    def get_result(self, price):
        df_buy, purchase_price = self.get_buy_list(price)
        df_buy['種別'] = self.toto_kind

        df_toto = pd.read_csv('data/marge/toto_info.csv', index_col=0).reset_index(drop = True)

        df_toto = df_toto[['第n回', '開催日', '種別', 'ホーム', 'アウェイ', 'くじ結果']]
        df_toto = df_toto[(df_toto['種別'] == self.toto_kind) & (df_toto['第n回'] == self.toto_n)]

        df_result = pd.merge(df_toto, df_buy, how = 'right')
        
        if df_result[:1]['くじ結果'].values[0] == '未実施':
            df_result[0] = df_result[0].astype(int)
            df_result[1] = df_result[1].astype(int)
            df_result[2] = df_result[2].astype(int)
            
            columns = ['第n回', '開催日', '種別', 'ホーム', 'アウェイ', 'くじ結果', 1,0,2]
            df_result = df_result.reindex(columns=columns)
            return df_result
        
        df_result['くじ結果'] = df_result['くじ結果'].astype(int)

        winning_list = []
        for i, row in df_result.iterrows():
            idx = row['くじ結果']
            if (idx == 0) | (idx == 1) | (idx == 2):
                if row[idx] == 1:
                    winning_list += [1]
                else:
                    winning_list += [0]
            else:
                winning_list += [1]
        df_result = df_result.assign(当選フラグ = winning_list)

        count_miss = sum(df_result['当選フラグ'].values == 0)
        df_result['外したくじ数'] = count_miss
        
        df_result[0] = df_result[0].astype(int)
        df_result[1] = df_result[1].astype(int)
        df_result[2] = df_result[2].astype(int)

        return df_result