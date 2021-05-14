import numpy as np
import pandas as pd
import time
import datetime
import urllib.parse

import numpy as np
import pandas as pd
import time
import datetime
import urllib.parse

class j_starting_member():
    
    def  scraping(self, only_new_data_flg):
        columns_1 = ["日付", "キックオフ時刻", "スタジアム", "入場者数", "天候", "気温", "湿度"]
        columns_2 = ["H_team", "H_監督", "H_ポジション1", "H_選手1", "H_ポジション2", "H_選手2", "H_ポジション3", "H_選手3", "H_ポジション4", "H_選手4", "H_ポジション5", "H_選手5", "H_ポジション6", "H_選手6", "H_ポジション7", "H_選手7", "H_ポジション8", "H_選手8", "H_ポジション9", "H_選手9", "H_ポジション10", "H_選手10", "H_ポジション11", "H_選手11"]
        columns_3 = ["A_team", "A_監督", "A_ポジション1", "A_選手1", "A_ポジション2", "A_選手2", "A_ポジション3", "A_選手3", "A_ポジション4", "A_選手4", "A_ポジション5", "A_選手5", "A_ポジション6", "A_選手6", "A_ポジション7", "A_選手7", "A_ポジション8", "A_選手8", "A_ポジション9", "A_選手9", "A_ポジション10", "A_選手10", "A_ポジション11", "A_選手11"]
        columns = columns_1 + columns_2 + columns_3 + ["url"]

        if only_new_data_flg:
            df = pd.read_csv('data/j_league_data_site/j_starting_member.csv').dropna()
            now_year= datetime.datetime.now().year
            last_year_index_list = df[df['日付'].str.contains(str(now_year-1))]['日付']
            start_id = last_year_index_list.index[-1] + 1 # 去年の最後の試合の試合IDを取得
            end_id = start_id + 2000
            df_result = df[df['Unnamed: 0'] < start_id].drop(columns =['Unnamed: 0'])
        else:
            df_result = pd.DataFrame(columns = columns).copy()
            start_id = 1
            end_id = 27000

        for i in range(start_id, end_id):
            print("処理中：match_card_id = " + str(i) + " (" + str(i-start_id+1) +"/" + str(end_id-start_id) + ")" )
            df_tmp = pd.DataFrame(columns = columns, index = [i]).copy()
            url = "https://data.j-league.or.jp/SFMS02/?match_card_id=" + str(i)
            df_tmp["url"] = url
            getted_h_pleayer = False
            getted_h_coach = False
            time.sleep(0.5) # スリープ処理
            try:
                data = pd.read_html(url)
            except:
                df_result = pd.concat([df_result, df_tmp])
                continue

            for j, i_df in enumerate(data):

                if i_df.shape[0]==0:
                    continue

                if j == 0:
                    df_tmp["H_team"] = i_df.iat[0,0]
                    df_tmp["A_team"] = i_df.iat[0,-1]

                if i_df.iat[0,0] == 'GK' and i_df.shape[0] == 11:
                    if not getted_h_pleayer:
                        H_position_list = i_df.iloc[:11, 0].values
                        H_player_list = i_df.iloc[:11, 2].values
                        getted_h_pleayer = True
                        for k in range(11):
                            df_tmp["H_選手"+str(k+1)] =  H_player_list[k]
                            df_tmp["H_ポジション"+str(k+1)] =  H_position_list[k]
                    else:
                        A_position_list = i_df.iloc[:11, 0].values
                        A_player_list = i_df.iloc[:11, 2].values
                        for k in range(11):
                            df_tmp["A_選手"+str(k+1)] =  A_player_list[k]
                            df_tmp["A_ポジション"+str(k+1)] =  A_position_list[k]

                if i_df.shape == (1,3) and getted_h_pleayer:
                    if not getted_h_coach:
                        df_tmp["H_監督"] = i_df.iat[0,-1]
                        getted_h_coach = True
                    else:
                        df_tmp["A_監督"] = i_df.iat[0,-1]

                if i_df.columns[0] == '日付':
                    df_tmp["日付"] = i_df["日付"].values[0]
                    df_tmp["キックオフ時刻"] = i_df["キックオフ時刻"].values[0]
                    df_tmp["スタジアム"] = i_df["スタジアム"].values[0]
                    df_tmp["入場者数"] = i_df["入場者数"].values[0]
                    df_tmp["天候"] = i_df["天候"].values[0]
                    df_tmp["気温"] = i_df["気温"].values[0]
                    df_tmp["湿度"] = i_df["湿度"].values[0]

            df_result = pd.concat([df_result, df_tmp])

        df_result.to_csv("data/j_league_data_site/j_starting_member.csv")
        return df_result
    
    def  clean(self):
        df = pd.read_csv('data/j_league_data_site/j_starting_member.csv', index_col=0).dropna()

        yyyyMMdd_list = []
        for i, row in df.iterrows():
            yyyyMMdd_list += [row["日付"].replace('/', '')]

        df.drop(columns = ["日付"], inplace = True)
        df = df.assign(年月日 = yyyyMMdd_list)
        
        # データに含まれる%、()を削除
        dic = {'(':None, ')':None, '%':None}
        df["湿度"] = df["湿度"].apply(lambda x : x.translate(str.maketrans(dic)))


        columns_list = ['年月日', 'キックオフ時刻', 'スタジアム', '入場者数', '天候', '気温', '湿度', 'H_team', 'H_監督',
               'A_team', 'A_監督',
               'H_ポジション1', 'H_選手1', 'H_ポジション2', 'H_選手2', 'H_ポジション3', 'H_選手3',
               'H_ポジション4', 'H_選手4', 'H_ポジション5', 'H_選手5', 'H_ポジション6', 'H_選手6',
               'H_ポジション7', 'H_選手7', 'H_ポジション8', 'H_選手8', 'H_ポジション9', 'H_選手9',
               'H_ポジション10', 'H_選手10', 'H_ポジション11', 'H_選手11', 
               'A_ポジション1', 'A_選手1', 'A_ポジション2', 'A_選手2', 'A_ポジション3', 'A_選手3',
               'A_ポジション4', 'A_選手4', 'A_ポジション5', 'A_選手5', 'A_ポジション6', 'A_選手6',
               'A_ポジション7', 'A_選手7', 'A_ポジション8', 'A_選手8', 'A_ポジション9', 'A_選手9',
               'A_ポジション10', 'A_選手10', 'A_ポジション11', 'A_選手11', 'url']
        df = df.reindex(columns=columns_list)
        df.to_csv("data/j_league_data_site/j_starting_member_cleaned.csv")