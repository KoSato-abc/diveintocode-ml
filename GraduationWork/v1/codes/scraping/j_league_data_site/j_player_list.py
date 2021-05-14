import numpy as np
import pandas as pd
import time
import datetime
import urllib.parse
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup

class j_player_list():
    
    def scraping(self, only_new_data_flg):
        
#         self.make_j_player_list()
        self.make_j_player_list2()
        
    def clean(self):
        df = pd.read_csv('data/j_league_data_site/j_player_list.csv', index_col=0)
        df = df.reset_index(drop = True)
        df.to_csv("data/j_league_data_site/j_player_list_cleaned.csv")
        
        df = pd.read_csv('data/j_league_data_site/j_player_list2.csv', index_col=0)
        df = df.reset_index(drop = True)

        club_lists = []
        max_len = 0
        for teams in df['前所属チーム'].values:
            club_list = teams.replace('Ｕ－', 'Ｕ-').split('－')
            club_lists += [list(reversed(club_list))]
            if len(club_list) > max_len:
                max_len = len(club_list)

        columns = []
        base_str = '前所属チーム'
        for i in range(max_len):
            columns += [base_str + str(i+1)]

        df_clubs = pd.DataFrame(club_lists, columns = columns)
        df_result = pd.concat([df, df_clubs],axis=1).drop(columns = ['前所属チーム'])
        
        df_result.to_csv("data/j_league_data_site/j_player_list2_cleaned.csv")
        
    def make_j_player_list(self):
        head = "https://data.j-league.or.jp/SFIX03/createPlayerListInfoByFirstAlphabetList?player_name_first_alphabet="
        idx_list = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', 'を', 'ん']
        columns = ['全てチェック', '選手名（英語）', '最終所属', 'ポジション', '生年月日', '身長/体重', 'url']
        df_result = pd.DataFrame(columns = columns)

        for idx in idx_list:
            index = urllib.parse.quote(idx)
            url = head + index
            print('処理中 : ' + idx)

            time.sleep(1) # スリープ処理
            data = pd.read_html(url)
            df_tmp = pd.DataFrame(data[0])
            df_tmp['url'] = url
            if df_tmp.columns.values[0] == columns[0]:
                df_result = pd.concat([df_result, df_tmp])

        df_result = df_result[df_result['全てチェック']!='全てチェック']
        df_result = df_result.rename(columns={'全てチェック': '選手名'})

        df_result.to_csv("data/j_league_data_site/j_player_list.csv")
        
    def make_j_player_list2(self):
        j1_team_id_list = ['14', '北海道コンサドーレ札幌', '54', 'ベガルタ仙台', '1', '鹿島アントラーズ', '3', '浦和レッズ', '11', '柏レイソル', '22', 'ＦＣ東京', '21', '川崎フロンターレ', '5', '横浜Ｆ・マリノス', '34', '横浜ＦＣ', '12', '湘南ベルマーレ', '7', '清水エスパルス', '8', '名古屋グランパス', '9', 'ガンバ大阪', '20', 'セレッソ大阪', '18', 'ヴィッセル神戸', '10', 'サンフレッチェ広島', '36', '徳島ヴォルティス', '23', 'アビスパ福岡', '33', 'サガン鳥栖', '31', '大分トリニータ']
        j2_team_id_list = ['270', 'ブラウブリッツ秋田', '29', 'モンテディオ山形', '94', '水戸ホーリーホック', '40', '栃木ＳＣ', '35', 'ザスパクサツ群馬', '27', '大宮アルディージャ', '2', 'ジェフユナイテッド千葉', '4', '東京ヴェルディ', '45', 'ＦＣ町田ゼルビア', '273', 'ＳＣ相模原', '28', 'ヴァンフォーレ甲府', '46', '松本山雅ＦＣ', '78', 'アルビレックス新潟', '275', 'ツエーゲン金沢', '13', 'ジュビロ磐田', '24', '京都サンガF.C.', '42', 'ファジアーノ岡山', '330', 'レノファ山口ＦＣ', '37', '愛媛ＦＣ', '43', 'ギラヴァンツ北九州', '47', 'Ｖ・ファーレン長崎', '277', 'ＦＣ琉球']
        j3_team_id_list = ['362', 'ヴァンラーレ八戸', '269', 'いわてグルージャ盛岡', '271', '福島ユナイテッドＦＣ', '272', 'Ｙ．Ｓ．Ｃ．Ｃ．横浜', '274', 'ＡＣ長野パルセイロ', '41', 'カターレ富山', '276', '藤枝ＭＹＦＣ', '347', 'アスルクラロ沼津', '39', 'ＦＣ岐阜', '44', 'ガイナーレ鳥取', '48', 'カマタマーレ讃岐', '369', 'ＦＣ今治', '38', 'ロアッソ熊本', '371', 'テゲバジャーロ宮崎', '338', '鹿児島ユナイテッドＦＣ']
        all_team_id_list = [j1_team_id_list] + [j2_team_id_list] + [j3_team_id_list]
        url_list = []
        team_list = []
        for i, team_id_list in enumerate(all_team_id_list):

            if i == 0:
                leagu_id = urllib.parse.quote('Ｊ1リーグ')
            elif i == 1:
                leagu_id = urllib.parse.quote('Ｊ２リーグ')
            else:
                leagu_id = urllib.parse.quote('Ｊ3リーグ')

            for j, s in enumerate(team_id_list):
                if j % 2==0:
                    team_id = urllib.parse.quote(s)
                    team_name = urllib.parse.quote(team_id_list[j+1])
                    team_list += [team_id_list[j+1]]
                    url = 'https://data.j-league.or.jp/SFIX02/search?displayId=SFIX02&selectValue='
                    url += str(i+1) + '&displayId=SFIX02&selectValueTeam=' + team_id + '&displayName=&displayNameTeam=' + team_name
                    url_list += [url]
                    
        df_result = None
        for i, url in enumerate(url_list):
            print('処理中：',team_list[i], url)
            time.sleep(1) # スリープ処理
            html = requests.get(url)
            soup = BeautifulSoup(html.content, "html.parser")

            name_list = []
            name_e_list = []
            count = 0
            for name_elements in soup.find_all( class_="s-txt" ):
                if str(name_elements)[1:5] == 'span' and name_elements.text!='（２種）':
                    count+=1
                    if count%2==1:
                        name_list+=[name_elements.text]
                    else:
                        name_e_list+=[name_elements.text]
                else:
                    continue

            club_list = []
            birthday_list = []
            for  elements in soup.find_all( class_="dl-base" ):
                ele_list = str(elements.text).split('\n')
                for j, elements2 in enumerate (ele_list):

                    if elements2 == '6':
                        teams = ele_list[j+1]
                        if teams == '前所属チーム':
                            pass
                        else:
                            club_list += [teams]
                    
                    if elements2 == '2':
                        birthday = ele_list[j+1]
                        if birthday == '生年月日':
                            pass
                        else:
                            birthday_list += [birthday]

            df_club = pd.DataFrame(club_list, columns = ['前所属チーム'])
            df_name = pd.DataFrame(name_list, columns = ['選手名'])
            df_name2 = pd.DataFrame(name_e_list, columns = ['選手名（英字）'])
            df_birthday = pd.DataFrame(birthday_list, columns = ['生年月日'])

            df_tmp = pd.concat([df_name, df_name2, df_club, df_birthday],axis=1)
            df_tmp['所属チーム']=team_list[i]

            df_result = pd.concat([df_result, df_tmp, df_club],axis=0)

        df_result = df_result.dropna(how='any')
        df_result.to_csv("data/j_league_data_site/j_player_list2.csv")