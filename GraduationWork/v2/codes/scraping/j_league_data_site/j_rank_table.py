import numpy as np
import pandas as pd
import time
import datetime
import urllib.parse
from urllib.error import HTTPError

class j_rank_table():
    
    def scraping(self, only_new_data_flg):

        url1 = "https://data.j-league.or.jp/SFRT01/?competitionSectionIdLabel="
        url2 = "&competitionIdLabel="
        competitionIdLabel_j1 = ["Ｊリーグ　ディビジョン１", "Ｊリーグ　ディビジョン１", "Ｊリーグ　ディビジョン１", "明治安田生命Ｊ１リーグ １ｓｔ", "明治安田生命Ｊ１リーグ ２ｎｄ", "明治安田生命Ｊ１リーグ １ｓｔ", "明治安田生命Ｊ１リーグ ２ｎｄ", "明治安田生命Ｊ１リーグ", "明治安田生命Ｊ１リーグ", "明治安田生命Ｊ１リーグ", "明治安田生命Ｊ１リーグ", "明治安田生命Ｊ１リーグ"]
        competitionIdLabel_j2 = ["Ｊリーグ　ディビジョン２", "Ｊリーグ　ディビジョン２", "Ｊリーグ　ディビジョン２", "明治安田生命Ｊ２リーグ", "明治安田生命Ｊ２リーグ", "明治安田生命Ｊ２リーグ", "明治安田生命Ｊ２リーグ", "明治安田生命Ｊ２リーグ", "明治安田生命Ｊ２リーグ", "明治安田生命Ｊ２リーグ"]
        competitionIdLabel_j3 = ["明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ", "明治安田生命Ｊ３リーグ"]
        competitionId_j1 = ["322", "347", "372", "397", "398", "411", "412", "428", "444", "460", "477", "492"]
        competitionId_j2 = ["323", "348", "373", "400", "413", "429", "445", "467", "478", "493"]
        competitionId_j3 = ["380", "399", "414", "430", "446", "468", "479", "494"]
        url3 = "&yearIdLabel="
        url4 = "&yearId="
        url5 = "&competitionId="
        url6 = "&competitionSectionId="
        url7 = "&search=search"
        df_result = None
        df_result_has_stage = None
        now_year= datetime.datetime.now().year

        if only_new_data_flg:
            df_result = pd.read_csv("data/j_league_data_site/j_rank_table.csv", index_col=0)
            df_result = df_result[df_result["year"] != now_year].copy()
            df_result_has_stage = pd.read_csv("data/j_league_data_site/j_rank_table_has_st.csv", index_col=0)
            df_result_has_stage = df_result_has_stage[df_result_has_stage["year"] != now_year].copy()

        for year in range(2012, now_year+1):
            if only_new_data_flg and now_year !=year:
                continue
            year_id = urllib.parse.quote(str(year)+"年")

            for section in range(1, 50):
                section_Id = urllib.parse.quote("第"+str(section)+"節")
                is_ok_j1_1 = False
                is_ok_j1_2 = False
                is_ok_j2 = False
                is_ok_j3 = False
                print("処理中 :", year, section)
                # J1
                for i in range(len(competitionIdLabel_j1)):
                    competition_Id = urllib.parse.quote(competitionIdLabel_j1[i], safe='　')
                    competition_Id = competition_Id.replace(' ', '%E3%80%80')
                    url_j1 = url1+section_Id+url2+competition_Id+url3+year_id+url4+str(year)+url5+competitionId_j1[i]+url6+str(section)+url7
                    time.sleep(0.5) # スリープ処理
                    try:
                        data_list = pd.read_html(url_j1)
                        df_data = pd.DataFrame(data_list[0]) # データフレームに変換
                        df_data["year"] = year
                        df_data["カテゴリ"] = "J1"
                        df_data["節"] = section

                        comLabel = competitionIdLabel_j1[i]
                        if comLabel == "明治安田生命Ｊ１リーグ １ｓｔ":
                            is_ok_j1_1 = True
                            df_data["stage"] = "１ｓｔ"
                            df_result_has_stage = pd.concat([df_result_has_stage, df_data])
                        elif comLabel == "明治安田生命Ｊ１リーグ ２ｎｄ":
                            is_ok_j1_2 = True
                            df_data["stage"] = "2ｓｔ"
                            df_result_has_stage = pd.concat([df_result_has_stage, df_data])
                        else:
                            is_ok_j1_1 = True
                            is_ok_j1_2 = True
                            df_result = pd.concat([df_result, df_data])
                    except HTTPError:
                        continue

                # J2
                for i in range(len(competitionIdLabel_j2)):
                    competition_Id = urllib.parse.quote(competitionIdLabel_j２[i], safe='　')
                    competition_Id = competition_Id.replace(' ', '%E3%80%80')
                    url_j2 = url1+section_Id+url2+competition_Id+url3+year_id+url4+str(year)+url5+competitionId_j2[i]+url6+str(section)+url7
                    time.sleep(0.5) # スリープ処理
                    try:
                        data_list = pd.read_html(url_j2)
                        df_data = pd.DataFrame(data_list[0]) # データフレームに変換
                        df_data["year"] = year
                        df_data["カテゴリ"] = "J2"
                        df_data["節"] = section
                        df_result = pd.concat([df_result, df_data])
                        is_ok_j2 = True
                    except HTTPError:
                        continue

                # J3
                for i in range(len(competitionIdLabel_j3)):
                    competition_Id = urllib.parse.quote(competitionIdLabel_j3[i])
                    url_j3 = url1+section_Id+url2+competition_Id+url3+year_id+url4+str(year)+url5+competitionId_j3[i]+url6+str(section)+url7
                    time.sleep(0.5) # スリープ処理
                    try:
                        data_list = pd.read_html(url_j3)
                        df_data = pd.DataFrame(data_list[0]) # データフレームに変換
                        df_data["year"] = year
                        df_data["カテゴリ"] = "J3"
                        df_data["節"] = section
                        df_result = pd.concat([df_result, df_data])
                        is_ok_j3 = True
                    except HTTPError:
                        continue
        # csv出力
        df_result.to_csv("data/j_league_data_site/j_rank_table.csv")
        df_result_has_stage.to_csv("data/j_league_data_site/j_rank_table_has_st.csv")
        
    def _add_val(self, row1, row2, column):
        return row1[column].values[0] + row2[column].values[0]

    def clean(self):
        rank_columns = ['year', '節', 'カテゴリ', 'チーム', '順位', '勝点', '試合', '勝', '分', '敗', '得点', '失点', '得失点差', ]
        df_rank = pd.read_csv('data/j_league_data_site/j_rank_table.csv', index_col=0)
        df_rank = df_rank[rank_columns]
        df_rank2 = pd.read_csv('data/j_league_data_site/j_rank_table_has_st.csv', index_col=0)
        df_rank2 = df_rank2[rank_columns + ['stage', '年間勝点順位', '総勝点']]

        # df_rankとdf_rank2を結合
        j = 0
        for i in range(df_rank2.shape[0]):
            row_2st = df_rank2.iloc[i:i+1]

            if row_2st["stage"].values[0] == "2ｓｔ":
                team = row_2st["チーム"].values[0]
                year = row_2st["year"].values[0]

                row_1st = df_rank2[(df_rank2["stage"]=="１ｓｔ") & (df_rank2["チーム"]==team) & (df_rank2["year"]==year) & (df_rank2["節"]==17)]

                df_rank2.iloc[i:i+1,1] = int(row_2st['節'] + 17)
                df_rank2.iloc[i:i+1,4] = int(row_2st['年間勝点順位'])
                df_rank2.iloc[i:i+1,5] = self._add_val(row_1st, row_2st, '勝点')
                df_rank2.iloc[i:i+1,6] = self._add_val(row_1st, row_2st, '試合')
                df_rank2.iloc[i:i+1,7] = self._add_val(row_1st, row_2st, '勝')
                df_rank2.iloc[i:i+1,8] = self._add_val(row_1st, row_2st, '分')
                df_rank2.iloc[i:i+1,9] = self._add_val(row_1st, row_2st, '敗')
                df_rank2.iloc[i:i+1,10] = self._add_val(row_1st, row_2st, '得点')
                df_rank2.iloc[i:i+1,11] = self._add_val(row_1st, row_2st, '失点')
                df_rank2.iloc[i:i+1,12] = self._add_val(row_1st, row_2st, '得失点差')
            else:
                pass
        df_rank2.drop(columns = ["stage", "年間勝点順位", "総勝点"], inplace = True)
        df_rank = pd.concat([df_rank, df_rank2])

        # n節の順位表をn節終了時のデータから試合前のデータに書き換え
        df =  df_rank.copy()
        df_result = None
        for i, row in df.iterrows():
            tar_section = row["節"] - 1
            while tar_section >= 0:
                if tar_section == 0:
                    row["順位"] = 0
                    row["勝点"] = 0
                    row["試合"] = 0
                    row["勝"] = 0
                    row["分"] = 0
                    row["敗"] = 0
                    row["得点"] = 0
                    row["失点"] = 0
                    row["得失点差"] = 0
                    break
                else:
                    row_past = df[(df["year"]==row["year"]) & (df["チーム"]==row["チーム"]) & (df["節"]==tar_section)]
                    if row_past.shape[0]!=1:
                        tar_section -= 1
                        continue
                    else:

                        rank = row_past["順位"].values[0]
                        if rank == "※":
                            rank = "0"
                        row["順位"] = rank
                        row["勝点"] = row_past["勝点"].values[0]
                        row["試合"] = row_past["試合"].values[0]
                        row["勝"] = row_past["勝"].values[0]
                        row["分"] = row_past["分"].values[0]
                        row["敗"] = row_past["敗"].values[0]
                        row["得点"] = row_past["得点"].values[0]
                        row["失点"] = row_past["失点"].values[0]
                        row["得失点差"] = row_past["得失点差"].values[0]
                        break

            df_tmp = pd.DataFrame([row])
            df_result = pd.concat([df_result, df_tmp],axis=0)
        df_rank = df_result.reset_index(drop=True).copy()
        
        df_rank.to_csv("data/j_league_data_site/j_rank_table_cleaned.csv")
        return df_rank