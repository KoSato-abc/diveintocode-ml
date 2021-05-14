import numpy as np
import pandas as pd
import time
import datetime
import urllib.parse
from urllib.error import HTTPError
import re

class j_match_schedule():
    
    def scraping(self, only_new_data_flg):

        team_id_list = ["14", "362", "269", "54", "270", "29", "271", "1", "94", "40", "35", "3", "27", "2", "11", "22", "4", "45", "21", "5", "34", "272", "6", "12", "273", "28", "46", "274", "78", "41", "275", "7", "13", "276", "347", "8", "39", "24", "9", "20", "18", "44", "42", "10", "330", "48", "36", "37", "369", "23", "43", "33", "47", "38", "31", "371", "338", "277", "339", "340", "341", "278"]
        team_name_list = ["札幌", "八戸", "岩手", "仙台", "秋田", "山形", "福島", "鹿島", "水戸", "栃木", "群馬", "浦和", "大宮", "千葉", "柏", "FC東京", "東京Ｖ", "町田", "川崎Ｆ", "横浜FM", "横浜FC", "YS横浜", "横浜Ｆ", "湘南", "相模原", "甲府", "松本", "長野", "新潟", "富山", "金沢", "清水", "磐田", "藤枝", "沼津", "名古屋", "岐阜", "京都", "Ｇ大阪", "Ｃ大阪", "神戸", "鳥取", "岡山", "広島", "山口", "讃岐", "徳島", "愛媛", "今治", "福岡", "北九州", "鳥栖", "長崎", "熊本", "大分", "宮崎", "鹿児島", "琉球", "Ｆ東23", "Ｇ大23", "Ｃ大23", "J-22"]
        url_head = "https://data.j-league.or.jp/SFMS01/search?team_ids="
        url_foot = "&home_away_select=0&tv_relay_station_name="
        df_result = None
        for i in range(len(team_id_list)):

            url = url_head + team_id_list[i] + url_foot
            time.sleep(1) # スリープ処理
            j_data_list = pd.read_html(url)
            df_j_data = pd.DataFrame(j_data_list[0]) # データフレームに変換

            # チーム名のカラムを追加
            df_j_data["Team"] = team_name_list[i]

            df_result = pd.concat([df_result, df_j_data])

        df_result.to_csv("data/j_league_data_site/j_match_schedule.csv")
        
    def clean(self):
        # データの読み込み
        columns = ['年度', '大会', '節', '試合日', 'ホーム', 'スコア', 'アウェイ', 'スタジアム']
        df = pd.read_csv('data/j_league_data_site/j_match_schedule.csv', index_col=0)
        df = df[columns]

        section_list = []
        yyyyMMdd_list = []
        for i, row in df.iterrows():
            section = row["節"]
            if section is np.nan:
                section_list += [0]
            else:
                section_m = re.findall('第(.*)節', section)
                if len(section_m) == 0:
                    section_list += [0]
                else:
                    section_list += section_m

            year = str(row["年度"])
            day = row["試合日"]
            if day == "未定":
                yyyyMMdd_list += [day]
            else:
                month = re.findall('(.*)/', day)[0]
                day = re.findall('/(.*)\(', day)[0]
                yyyyMMdd_list += [year+month+day]

        df.drop(columns = ["節", "試合日", "年度"], inplace = True)
        df = df.assign(節 = section_list, 試合日 = yyyyMMdd_list)

        # 重複の削除
        df.drop_duplicates(inplace=True)

        columns_list = ['試合日', '節', '大会', 'ホーム', 'スコア', 'アウェイ', 'スタジアム']
        df = df.reindex(columns=columns_list)
        df = df.rename(columns={'試合日': '年月日', 'ホーム': 'H_Team', 'アウェイ': 'A_Team'})
        
        df = df.reset_index(drop=True).copy()
        df.to_csv("data/j_league_data_site/j_match_schedule_cleaned.csv")