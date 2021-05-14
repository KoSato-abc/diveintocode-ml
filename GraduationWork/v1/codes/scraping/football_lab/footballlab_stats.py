import numpy as np
import pandas as pd
import datetime
import time

class footballlab_stats():
    
    def __init__(self):
        self.wait_s = 1
        # Jリーグに所属するチームのリスト（2021年時点）
        self.j1_team_id_list = ["sapp", "send", "kasm", "uraw", "kasw", "f-tk", "ka-f", "y-fm", "y-fc", "shon", "shim", "nago", "g-os", "c-os", "kobe", "hiro", "toku", "fuku", "tosu", "oita"]
        self.j1_team_name_list = ["北海道コンサドーレ札幌", "ベガルタ仙台", "鹿島アントラーズ", "浦和レッズ",  "柏レイソル", "ＦＣ東京", "川崎フロンターレ", "横浜Ｆ・マリノス", "横浜ＦＣ", "湘南ベルマーレ", "清水エスパルス", "名古屋グランパス", "ガンバ大阪", "セレッソ大阪", "ヴィッセル神戸", "サンフレッチェ広島", "徳島ヴォルティス", "アビスパ福岡", "サガン鳥栖", "大分トリニータ"]
        self.j2_team_id_list = ["aki", "yama", "mito", "toch", "gun", "omiy", "chib", "tk-v", "mcd", "sagm", "kofu", "mats", "niig", "kana", "iwat", "kyot", "okay", "r-ya", "ehim", "kiky", "ngsk", "ryuk"]
        self.j2_team_name_list = ["ブラウブリッツ秋田", "モンテディオ山形", "水戸ホーリーホック", "栃木ＳＣ", "ザスパクサツ群馬", "大宮アルディージャ", "ジェフユナイテッド千葉", "東京ヴェルディ", "ＦＣ町田ゼルビア", "ＳＣ相模原", "ヴァンフォーレ甲府", "松本山雅ＦＣ", "アルビレックス新潟", "ツエーゲン金沢", "ジュビロ磐田", "京都サンガF.C.", "ファジアーノ岡山", "レノファ山口ＦＣ", "愛媛ＦＣ", "ギラヴァンツ北九州", "Ｖ・ファーレン長崎", "ＦＣ琉球"]
        self.j3_team_id_list = ["hach", "iwte", "fksm", "yscc", "naga", "toya", "fuji", "numa", "gifu", "totr", "sanu", "imab", "kuma", "myzk", "kufc"]
        self.j3_team_name_list = ["ヴァンラーレ八戸", "いわてグルージャ盛岡", "福島ユナイテッドＦＣ", "Ｙ．Ｓ．Ｃ．Ｃ．横浜", "ＡＣ長野パルセイロ", "カターレ富山", "藤枝ＭＹＦＣ", "アスルクラロ沼津", "ＦＣ岐阜", "ガイナーレ鳥取", "カマタマーレ讃岐", "ＦＣ今治", "ロアッソ熊本", "テゲバジャーロ宮崎", "鹿児島ユナイテッドＦＣ"]
        self.other_team_id_list = ["g-23","fct", "c-23", "j-22"]
        self.other_team_name_list = ["ガンバ大阪U-23", "ＦＣ東京U-23", "セレッソ大阪U-23", "Ｊリーグ・アンダー２２選抜"]
        self.team_id_list = self.j1_team_id_list + self.j2_team_id_list + self.j3_team_id_list + self.other_team_id_list
        self.team_name_list = self.j1_team_name_list + self.j2_team_name_list + self.j3_team_name_list + self.other_team_name_list
    
    # スクレイピング
    def scraping(self, only_new_data_flg):
        
        # 試合情報を取得
        df_info = self._scraping_info(only_new_data_flg)
        
        # 試合ごとのスタッツを付加
        df_stats = self._scraping_stats(df_info, only_new_data_flg)
        
        # csv出力
        df_stats.to_csv("data/footballlab/footballlab_stats.csv")
        df_info.to_csv("data/footballlab/footballlab_info.csv")
    
    # csvファイルのお掃除
    def clean(self):
    
        columns = ['節', '開催日', '相手', 'スコア', 'HomeAway', '会場', '天候', '自チーム', '年度',
               'H_シュート', 'H_枠内シュート', 'H_PKによるシュート', 'H_パス', 'H_クロス',
               'H_直接ＦＫ', 'H_間接ＦＫ', 'H_ＣＫ', 'H_スローイン', 'H_ドリブル', 'H_タックル', 'H_クリア',
               'H_インターセプト', 'H_オフサイド', 'H_警告', 'H_退場', 'H_３０ｍライン進入', 'H_ペナルティエリア進入',
               'H_攻撃回数', 'H_チャンス構築率', 'H_ボール支配率', 'H_パス成功率', 'H_クロス成功率',
               'H_スローイン成功率', 'H_ドリブル成功率', 'H_タックル成功率', 'A_シュート', 'A_枠内シュート',
               'A_PKによるシュート', 'A_パス', 'A_クロス', 'A_直接ＦＫ', 'A_間接ＦＫ', 'A_ＣＫ', 'A_スローイン',
               'A_ドリブル', 'A_タックル', 'A_クリア', 'A_インターセプト', 'A_オフサイド', 'A_警告', 'A_退場',
               'A_３０ｍライン進入', 'A_ペナルティエリア進入', 'A_攻撃回数', 'A_チャンス構築率', 'A_ボール支配率',
               'A_パス成功率', 'A_クロス成功率', 'A_スローイン成功率', 'A_ドリブル成功率',
               'A_タックル成功率']

        # データの読み込み
        df = pd.read_csv('data/footballlab/footballlab_stats.csv', index_col=0)
        df = df[columns]
        M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()

        # チーム名を統一
        df = self._df_rename_team(df, '自チーム', M_TEAM_NAMES)
        df = self._df_rename_team(df, '相手', M_TEAM_NAMES)

        # H_Team , A_Team, H_goal, A_goal, goal_difference, H_result, 年月日 を作成
        H_teams = []
        A_teams = []
        H_goal_list = []
        A_goal_list = []
        goal_difference_list = []
        result_list = []
        yyyymmdd_list = []
        for i, row in df.iterrows():
            left = int(row["スコア"].split('-')[0])
            right = int(row["スコア"].split('-')[1])
            year = str(row["年度"])
            mmdd = str(row["開催日"])

            if row["HomeAway"] == "H":
                H_teams += [row["自チーム"]]
                A_teams += [row["相手"]]
                H_goal = left
                A_goal = right
            elif row["HomeAway"] == "A":
                H_teams += [row["相手"]]
                A_teams += [row["自チーム"]]
                H_goal = right
                A_goal = left
            else:
                print("例外")

            if H_goal < A_goal:
                result = "2"
            elif H_goal > A_goal:
                result = "1"
            else:
                result = "0"

            if len(mmdd) == 3:
                month = mmdd[:1].zfill(2)
            else:
                month = mmdd[:2]
            day = mmdd[-2:]

            yyyymmdd_list += [year+month+day]
            H_goal_list += [H_goal]
            A_goal_list += [A_goal]
            goal_difference_list += [H_goal - A_goal]
            result_list += [result]

        df = df.assign(H_Team = H_teams, A_Team = A_teams, H_goal = H_goal_list, A_goal = A_goal_list, goal_difference = goal_difference_list, H_result = result_list, 年月日 = yyyymmdd_list)
        df.drop(columns = ["スコア", "HomeAway", "自チーム", "相手", "開催日","年度"], inplace = True)

        # データに含まれる%、()を削除
        tar_col_list = ["チャンス構築率", "ボール支配率", "パス成功率", "クロス成功率", "スローイン成功率", "ドリブル成功率", "タックル成功率"]
        header_list = ["H_", "A_"]
        dic = {'(':None, ')':None, '%':None}
        for _, header in enumerate(header_list):
            for _, col in enumerate(tar_col_list):

                target_col = header + col
                df[target_col] = df[target_col].apply(lambda x : x.translate(str.maketrans(dic)))

        # 重複を削除
        df.drop_duplicates(inplace=True)

        # カラムの並び替え
        columns = ['年月日', '節', 'H_Team', 'A_Team', '会場', '天候', 'H_シュート', 'H_枠内シュート', 'H_PKによるシュート', 'H_パス', 'H_クロス',
               'H_直接ＦＫ', 'H_間接ＦＫ', 'H_ＣＫ', 'H_スローイン', 'H_ドリブル', 'H_タックル', 'H_クリア',
               'H_インターセプト', 'H_オフサイド', 'H_警告', 'H_退場', 'H_３０ｍライン進入', 'H_ペナルティエリア進入',
               'H_攻撃回数', 'H_チャンス構築率', 'H_ボール支配率', 'H_パス成功率', 'H_クロス成功率',
               'H_スローイン成功率', 'H_ドリブル成功率', 'H_タックル成功率', 'A_シュート', 'A_枠内シュート',
               'A_PKによるシュート', 'A_パス', 'A_クロス', 'A_直接ＦＫ', 'A_間接ＦＫ', 'A_ＣＫ', 'A_スローイン',
               'A_ドリブル', 'A_タックル', 'A_クリア', 'A_インターセプト', 'A_オフサイド', 'A_警告', 'A_退場',
               'A_３０ｍライン進入', 'A_ペナルティエリア進入', 'A_攻撃回数', 'A_チャンス構築率', 'A_ボール支配率',
               'A_パス成功率', 'A_クロス成功率', 'A_スローイン成功率', 'A_ドリブル成功率',
               'A_タックル成功率', 'H_goal', 'A_goal', 'goal_difference', 'H_result']
        df = df.reindex(columns=columns)

        df.to_csv("data/footballlab/footballlab_stats_cleaned.csv")
        return df.copy()

    def _scraping_stats(self, df_info, only_new_data_flg):
        now_year= datetime.datetime.now().year
        df_result = None
        df_info_cp = df_info.copy()
        count_df = len(df_info_cp)
        name = "_scraping_stats ："
        count = 0
        
        if only_new_data_flg:
            df_result = pd.read_csv("data/footballlab/footballlab_stats.csv", index_col=0)
            df_result = df_result[df_result["年度"] != now_year].copy()
#             df_result['開催日'] = df_result['開催日'].apply(lambda x : "0"+str(x)[-5:-1])
        
        for i, row in df_info_cp.iterrows():
                count += 1
                month, day = row["開催日"][:2], row["開催日"][2:]
                team_id = row["team_id"]
                year = row["年度"]
                url = "https://www.football-lab.jp/"+team_id+"/report/?year="+year+"&month="+month+"&date="+day
                
                if only_new_data_flg and now_year !=int(year):
                    continue
                
                if type(row["スコア"])==type(0.1):
                    print(name, "pass url=", url,"(", count, "/", count_df,")") # デバッグ用
                    continue

                print(name, "url=", url,"(", count, "/", count_df,")") # デバッグ用
                time.sleep(self.wait_s) # スリープ処理
                data = pd.read_html(url, match='ペナルティエリア進入') # 読み込み
                df = pd.DataFrame(data[0]) # データフレームに変換
                try:
                    df = df[df['総数'].str.match("(\d)(?!.*ライン進入)")] # 不要な行削除
                except ValueError:
                    # スタッツデータが未掲載
                    continue
                columns = df["Unnamed: 3"].values.tolist()

                colmns_stats = np.empty(0)
                columns_success_rate = ['シュート', 'パス', 'クロス', 'スローイン', 'ドリブル', 'タックル']
                for _, header in enumerate(["H_", "A_"]):
                    for _, col in enumerate(columns):
                        colmns_stats = np.append(colmns_stats, header + col)
                    for _, col in enumerate(columns_success_rate):
                        colmns_stats = np.append(colmns_stats, header + col + "成功率")

                home_stats = np.empty(0)
                away_stats = np.empty(0)
                home_success_rate = np.empty(0)
                away_success_rate = np.empty(0)
                for _, col in enumerate(columns):
                    val = df[df['Unnamed: 3'] == col].values[0]
    
                    home_stats = np.append(home_stats, val[2])
                    away_stats = np.append(away_stats, val[4])
    
                    if col in columns_success_rate:
                        home_success_rate = np.append(home_success_rate, val[1])
                        away_success_rate = np.append(away_success_rate, val[5])
        
                home_stats = np.append(home_stats, home_success_rate)
                away_stats = np.append(away_stats, away_success_rate)
                home_away_stats = np.append(home_stats, away_stats)
                s_stats = pd.Series(home_away_stats, index=colmns_stats)
    
                s_row_stats = row.append(s_stats)
                
                if df_result is None:
                    df_result = pd.DataFrame(columns=s_row_stats.index.tolist())
                df_result = df_result.append(s_row_stats, ignore_index=True)
        
        return df_result
    
    def _scraping_info(self, only_new_data_flg):

        df_result = None
        drop_columns = ["Unnamed: 2", "観客数", "チャンス構築率", "シュート", "シュート成功率", "支配率", "攻撃CBP", "パスCBP", "奪取P", "守備P", "得点者", "AGI", "KAGI"]
        no_data_url_list = ["https://www.football-lab.jp/aki/match/?year=2012", "https://www.football-lab.jp/aki/match/?year=2013", "https://www.football-lab.jp/mcd/match/?year=2013", "https://www.football-lab.jp/sagm/match/?year=2012", "https://www.football-lab.jp/sagm/match/?year=2013", "https://www.football-lab.jp/kana/match/?year=2012", "https://www.football-lab.jp/kana/match/?year=2013", "https://www.football-lab.jp/r-ya/match/?year=2012", "https://www.football-lab.jp/r-ya/match/?year=2013", "https://www.football-lab.jp/r-ya/match/?year=2014", "https://www.football-lab.jp/ngsk/match/?year=2012", "https://www.football-lab.jp/ryuk/match/?year=2012", "https://www.football-lab.jp/ryuk/match/?year=2013", "https://www.football-lab.jp/hach/match/?year=2012", "https://www.football-lab.jp/hach/match/?year=2013", "https://www.football-lab.jp/hach/match/?year=2014", "https://www.football-lab.jp/hach/match/?year=2015", "https://www.football-lab.jp/hach/match/?year=2016", "https://www.football-lab.jp/hach/match/?year=2017", "https://www.football-lab.jp/hach/match/?year=2018", "https://www.football-lab.jp/mori/match/?year=2012", "https://www.football-lab.jp/mori/match/?year=2013", "https://www.football-lab.jp/fksm/match/?year=2012", "https://www.football-lab.jp/fksm/match/?year=2013", "https://www.football-lab.jp/yscc/match/?year=2012", "https://www.football-lab.jp/yscc/match/?year=2013", "https://www.football-lab.jp/naga/match/?year=2012", "https://www.football-lab.jp/naga/match/?year=2013", "https://www.football-lab.jp/fuji/match/?year=2012", "https://www.football-lab.jp/fuji/match/?year=2013", "https://www.football-lab.jp/numa/match/?year=2012", "https://www.football-lab.jp/numa/match/?year=2013", "https://www.football-lab.jp/numa/match/?year=2014", "https://www.football-lab.jp/numa/match/?year=2015", "https://www.football-lab.jp/numa/match/?year=2016", "https://www.football-lab.jp/sanu/match/?year=2012", "https://www.football-lab.jp/sanu/match/?year=2013", "https://www.football-lab.jp/imab/match/?year=2012", "https://www.football-lab.jp/imab/match/?year=2013", "https://www.football-lab.jp/imab/match/?year=2014", "https://www.football-lab.jp/imab/match/?year=2015", "https://www.football-lab.jp/imab/match/?year=2016", "https://www.football-lab.jp/imab/match/?year=2017", "https://www.football-lab.jp/imab/match/?year=2018", "https://www.football-lab.jp/imab/match/?year=2019", "https://www.football-lab.jp/myzk/match/?year=2012", "https://www.football-lab.jp/myzk/match/?year=2013", "https://www.football-lab.jp/myzk/match/?year=2014", "https://www.football-lab.jp/myzk/match/?year=2015", "https://www.football-lab.jp/myzk/match/?year=2016", "https://www.football-lab.jp/myzk/match/?year=2017", "https://www.football-lab.jp/myzk/match/?year=2018", "https://www.football-lab.jp/myzk/match/?year=2019", "https://www.football-lab.jp/myzk/match/?year=2020", "https://www.football-lab.jp/kufc/match/?year=2012", "https://www.football-lab.jp/kufc/match/?year=2013", "https://www.football-lab.jp/kufc/match/?year=2014", "https://www.football-lab.jp/kufc/match/?year=2015", "https://www.football-lab.jp/g-23/match/?year=2012", "https://www.football-lab.jp/g-23/match/?year=2013", "https://www.football-lab.jp/g-23/match/?year=2014", "https://www.football-lab.jp/g-23/match/?year=2015", "https://www.football-lab.jp/fct/match/?year=2012", "https://www.football-lab.jp/fct/match/?year=2013", "https://www.football-lab.jp/fct/match/?year=2014", "https://www.football-lab.jp/fct/match/?year=2015", "https://www.football-lab.jp/fct/match/?year=2020", "https://www.football-lab.jp/c-23/match/?year=2012", "https://www.football-lab.jp/c-23/match/?year=2013", "https://www.football-lab.jp/c-23/match/?year=2014", "https://www.football-lab.jp/c-23/match/?year=2015", "https://www.football-lab.jp/j-22/match/?year=2012", "https://www.football-lab.jp/j-22/match/?year=2013", "https://www.football-lab.jp/j-22/match/?year=2016", "https://www.football-lab.jp/j-22/match/?year=2017", "https://www.football-lab.jp/j-22/match/?year=2018", "https://www.football-lab.jp/j-22/match/?year=2019", "https://www.football-lab.jp/j-22/match/?year=2020"]
        url_head = "https://www.football-lab.jp/"
        url_foot = "/match/?year="
        now_year= datetime.datetime.now().year
        from_y, to_y = 2012, now_year+1
        
        name = "_scraping_info :"
        count_y = len(range(from_y, to_y))
        count_max = count_y * len(self.team_id_list)
        
        # チームごとに繰り返す
        for i, team_id in enumerate(self.team_id_list):
    
            # 2012年から2021年のデータを取得
            for year in range(from_y, to_y):
                new_team_id = self._get_team_id(team_id, year)
                url =  url_head + new_team_id + url_foot + str(year)
                
                if only_new_data_flg and now_year !=int(year):
                    continue
                
                try:
                    print(name, self.team_name_list[i], year, "url=", url,"(", i*count_y + year - from_y + 1, "/", count_max,")") # デバッグ用
                    time.sleep(self.wait_s) # スリープ処理
                    data =  pd.read_html(url) # 読み込み
                    df = pd.DataFrame(data[0]) # データフレームに変換
                except ValueError:
                    if url in no_data_url_list:
                        pass # 確認済みエラー
                    else:
                        print("例外発生 ： ", url)
                    continue
                
                # 整形
                df["自チーム"] = self.team_name_list[i]
                df["年度"] = str(year)
                df["team_id"] = new_team_id
                df.drop(columns=drop_columns, inplace = True, errors = "ignore")
                df = df[df["開催日"] != "開催日"]
                df['開催日'] = df['開催日'].apply(lambda x : x.split('.')[0].zfill(2)+x.split('.')[1].zfill(2))
                df = df.rename(columns={'Unnamed: 5': 'HomeAway'})
                
                df_result = pd.concat([df_result, df])
        
        df_result.drop_duplicates(inplace=True)
        return df_result
    
    # urlのチームIDが年度で変わる奴があるためその対応
    def _get_team_id(self, team_id, year):
        
        if team_id == "f-tk": 
            if year > 2014:
                return "fctk"
        elif team_id == "gun": 
            if year == 2012:
                return "kusa"
        elif team_id == "iwte": 
            if year <= 2018:
                return "mori"
            
        return team_id
    
    def _df_rename_team(self,df, tar_col, m_team_list):
        df = df.copy()
        new_name_list = []

        for i, row in df.iterrows():
            count_change = 0
            for i, team_list in enumerate(m_team_list):
                if row[tar_col] in team_list:
                    new_name_list += [team_list[0]]
                    count_change += 1
            if count_change == 1:
                pass
            else:
                print(f"例外あり：{row[tar_col]}")

        df.drop(columns = [tar_col], inplace = True)

        df_tmp = pd.DataFrame(new_name_list, columns = [tar_col])
        df = pd.concat([df, df_tmp],axis=1)
        
        return df