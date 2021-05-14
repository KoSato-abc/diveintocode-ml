import numpy as np
import pandas as pd
import datetime

M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()

def marge_csv():
    
    print('marge.csv作成')
    make_marge_csv()
    print('player_list.csv作成')
    make_player_list_csv()
    print('toto_info.csv作成')
    make_toto_info_csv()

def make_marge_csv():
    #     pd.set_option('display.max_rows', 100)
    #     pd.set_option('display.max_columns', 100000)
    
    # 読み込み
    df_stats = pd.read_csv('data/footballlab/footballlab_stats_cleaned.csv', index_col=0)
    df_starting_member = pd.read_csv('data/j_league_data_site/j_starting_member_cleaned.csv', index_col=0)
    df_rank_table = pd.read_csv('data/j_league_data_site/j_rank_table_cleaned.csv', index_col=0)
    df_schedule = pd.read_csv('data/j_league_data_site/j_match_schedule_cleaned.csv', index_col=0)
    df_player_list = pd.read_csv('data/j_league_data_site/j_player_list_cleaned.csv', index_col=0)

    # 2012年〜現在のデータを抽出
    df_starting_member = df_starting_member[df_starting_member['年月日']>20120000]
    df_schedule = df_schedule[df_schedule['年月日'] != '未定'].astype({'年月日': int})
    df_schedule = df_schedule[df_schedule['年月日']>20120000]

    # チーム名を統一
    df_stats = _df_rename_team(df_stats, 'H_Team')
    df_stats = _df_rename_team(df_stats, 'A_Team')
    df_starting_member = _df_rename_team(df_starting_member, 'H_team')
    df_starting_member = _df_rename_team(df_starting_member, 'A_team')
    df_rank_table = _df_rename_team(df_rank_table, 'チーム')
    df_schedule = _df_rename_team(df_schedule, 'H_Team')
    df_schedule = _df_rename_team(df_schedule, 'A_Team')
    df_player_list = _df_rename_team(df_player_list, '最終所属')

    # df_stats にyearを追加
    year_list = []
    for i, row in df_stats.iterrows():
        year = str(row["年月日"])[:4]
        year_list += [int(year)]
    df_stats = df_stats.assign(year = year_list)

    # df_statsとdf_starting_memberをマージ
    df_marge = pd.merge(df_stats, df_starting_member, 
             left_on=['年月日', 'H_Team', 'A_Team'],
             right_on=['年月日', 'H_team', 'A_team']).drop(columns=['H_team', 'A_team'])

    # df_rank_tableをdf_rank_table_Hとdf_rank_table_Aにコピー
    df_rank_columns_H = df_rank_table.columns.values.copy()
    for i, col in enumerate(df_rank_columns_H):
        df_rank_columns_H[i] =  "H_" + col
    df_rank_table_H = df_rank_table.set_axis(df_rank_columns_H, axis='columns').copy()

    df_rank_columns_A = df_rank_table.columns.values.copy()
    for i, col in enumerate(df_rank_columns_A):
        df_rank_columns_A[i] =  "A_" + col
    df_rank_table_A = df_rank_table.set_axis(df_rank_columns_A, axis='columns').copy()

    # df_margeとdf_rank_table_Hをマージ
    df_marge = pd.merge(df_marge, df_rank_table_H, 
             left_on=['year', '節', 'H_Team'],
             right_on=['H_year', 'H_節', 'H_チーム']).drop(columns=['H_year', 'H_節', 'H_チーム'])

    # df_margeとdf_rank_table_Aをマージ
    df_marge = pd.merge(df_marge, df_rank_table_A, 
             left_on=['year', '節', 'A_Team'],
             right_on=['A_year', 'A_節', 'A_チーム']).drop(columns=['A_year', 'A_節', 'A_チーム'])

    df_marge.rename(columns={'H_カテゴリ': 'カテゴリ', '天候_x': '天候'}, inplace=True)
    df_marge.drop(columns=['A_カテゴリ', 'url', '天候_y', '会場'], inplace=True)

    # df_scheduleにカラムrest_daysを追加
    H_rest_days_list = []
    A_rest_days_list = []
    ini_rest_days = 7
    df_schedule = df_schedule.sort_values('年月日', ascending=False)
    for i, row in df_schedule.iterrows():

        H_team = row["H_Team"]
        A_team = row["A_Team"]
        yyyyMMdd_int = row["年月日"]

        yyyyMMdd_str = str(yyyyMMdd_int)
        row_dt = datetime.datetime(year=int(yyyyMMdd_str[:4]), month=int(yyyyMMdd_str[4:6]), day=int(yyyyMMdd_str[6:8]))

        last_dt_list = df_schedule[((df_schedule['H_Team']==H_team)|(df_schedule['A_Team']==H_team))&(df_schedule['年月日']<yyyyMMdd_int)]['年月日'].values
        if last_dt_list.size == 0:
            H_rest_days_list += [ini_rest_days]
        else:
            last_dt = str(last_dt_list[0])
            last_dt = datetime.datetime(year=int(last_dt[:4]), month=int(last_dt[4:6]), day=int(last_dt[6:8]))
            H_rest_days_list += [(row_dt-last_dt).days]

        last_dt_list = df_schedule[((df_schedule['H_Team']==A_team)|(df_schedule['A_Team']==A_team))&(df_schedule['年月日']<yyyyMMdd_int)]['年月日'].values
        if last_dt_list.size == 0:
            A_rest_days_list += [ini_rest_days]
        else:
            last_dt = str(last_dt_list[0])
            last_dt = datetime.datetime(year=int(last_dt[:4]), month=int(last_dt[4:6]), day=int(last_dt[6:8]))
            A_rest_days_list += [(row_dt-last_dt).days]

    df_schedule = df_schedule.assign(H_rest_days = H_rest_days_list)
    df_schedule = df_schedule.assign(A_rest_days = A_rest_days_list)

    # df_scheduleからJリーグの試合だけ抽出
    category_list = ['Ｊ１','Ｊ１ １ｓｔ', 'Ｊ１ ２ｎｄ', 'Ｊ２', 'Ｊ３']
    df_schedule = df_schedule[df_schedule['大会'].isin(category_list)]
    J1 = 'Ｊ１'
    df_schedule['大会'] = df_schedule['大会'].apply(lambda x : x.replace('Ｊ１ １ｓｔ', J1).replace('Ｊ１ ２ｎｄ',J1))

    # df_margeとdf_scheduleをマージ
    df_marge = pd.merge(df_schedule, df_marge, 
             left_on=['年月日', 'H_Team', 'A_Team'],
             right_on=['年月日', 'H_Team', 'A_Team'], how='left')
    
    # 不要な行を削除
    df_marge.rename(columns={'スタジアム_x': 'スタジアム', '節_x': '節'}, inplace=True)
    df_marge.drop(columns=['スタジアム_y', '節_y', '大会', 'スコア', 'year'], inplace=True)
    
    # カラムの並べ替え
    columns = ['年月日', 'カテゴリ', '節', 'H_Team', 'A_Team', 'スタジアム', '天候', 'キックオフ時刻', '入場者数', '気温', '湿度', 'H_監督', 'H_順位', 'H_勝点', 'H_試合', 'H_勝', 'H_分', 'H_敗', 'H_得点', 'H_失点', 'H_得失点差', 'H_rest_days', 'A_監督', 'A_順位', 'A_勝点', 'A_試合', 'A_勝', 'A_分', 'A_敗', 'A_得点', 'A_失点', 'A_得失点差', 'A_rest_days', 'H_シュート', 'H_枠内シュート', 'H_PKによるシュート', 'H_パス', 'H_クロス', 'H_直接ＦＫ', 'H_間接ＦＫ', 'H_ＣＫ', 'H_スローイン', 'H_ドリブル', 'H_タックル', 'H_クリア', 'H_インターセプト', 'H_オフサイド', 'H_警告', 'H_退場', 'H_３０ｍライン進入', 'H_ペナルティエリア進入', 'H_攻撃回数', 'H_チャンス構築率', 'H_ボール支配率', 'H_パス成功率', 'H_クロス成功率', 'H_スローイン成功率', 'H_ドリブル成功率', 'H_タックル成功率', 'A_シュート', 'A_枠内シュート', 'A_PKによるシュート', 'A_パス', 'A_クロス', 'A_直接ＦＫ', 'A_間接ＦＫ', 'A_ＣＫ', 'A_スローイン', 'A_ドリブル', 'A_タックル', 'A_クリア', 'A_インターセプト', 'A_オフサイド', 'A_警告', 'A_退場', 'A_３０ｍライン進入', 'A_ペナルティエリア進入', 'A_攻撃回数', 'A_チャンス構築率', 'A_ボール支配率', 'A_パス成功率', 'A_クロス成功率', 'A_スローイン成功率', 'A_ドリブル成功率', 'A_タックル成功率', 'H_ポジション1', 'H_選手1', 'H_ポジション2', 'H_選手2', 'H_ポジション3', 'H_選手3', 'H_ポジション4', 'H_選手4', 'H_ポジション5', 'H_選手5', 'H_ポジション6', 'H_選手6', 'H_ポジション7', 'H_選手7', 'H_ポジション8', 'H_選手8', 'H_ポジション9', 'H_選手9', 'H_ポジション10', 'H_選手10', 'H_ポジション11', 'H_選手11', 'A_ポジション1', 'A_選手1', 'A_ポジション2', 'A_選手2', 'A_ポジション3', 'A_選手3', 'A_ポジション4', 'A_選手4', 'A_ポジション5', 'A_選手5', 'A_ポジション6', 'A_選手6', 'A_ポジション7', 'A_選手7', 'A_ポジション8', 'A_選手8', 'A_ポジション9', 'A_選手9', 'A_ポジション10', 'A_選手10', 'A_ポジション11', 'A_選手11', 'H_goal', 'A_goal', 'goal_difference', 'H_result']
    df_marge = df_marge.reindex(columns=columns)
    
    # インデックスの振り直し
    df_marge.reset_index(drop = True)
    
    # csv出力
    df_marge.to_csv("data/marge/marge.csv")

def _df_rename_team(df, tar_col):
    df = df.reset_index(drop = True).copy()
    new_name_list = []
    
    for i, row in df.iterrows():
        count_change = 0
        
        if row[tar_col] is np.nan:
            new_name_list += ['-']
            count_change += 1
        else:
            for i, team_list in enumerate(M_TEAM_NAMES):
                if row[tar_col] in team_list:
                    new_name_list += [team_list[0]]
                    count_change += 1

        if count_change == 1:
            pass
        elif count_change == 0:
            new_name_list += [row[tar_col]]
            print(f"TEAM_NAMES.csvに記載なし：{row[tar_col]}")
        else:
            print(f"TEAM_NAMES.csvを修正してください：{row[tar_col]}")
            
    df.drop(columns = [tar_col], inplace = True)

    df_tmp = pd.DataFrame(new_name_list, columns = [tar_col])
        
    df = pd.concat([df, df_tmp],axis=1)
    return df

def make_player_list_csv():
    # 読み込み
    df_player_list = pd.read_csv('data/j_league_data_site/j_player_list_cleaned.csv', index_col=0).reset_index(drop = True).copy()
    df_player_list2 = pd.read_csv('data/j_league_data_site/j_player_list2_cleaned.csv', index_col=0).reset_index(drop = True).copy()
    
    df_player_list = _df_rename_team(df_player_list,'最終所属')
    df_player_list2 = _df_rename_team(df_player_list2,'所属チーム')
    for i in range(1, 22):
        df_player_list2 = _df_rename_team(df_player_list2,'前所属チーム' + str(i))
        
    year_list = []
    for i, row in df_player_list.iterrows():
        year_list += [int(row['生年月日'][:4])]

    df_tmp = pd.DataFrame(year_list, columns = ['year'])
    df_player_list = pd.concat([df_player_list, df_tmp],axis=1)

    df_player_list = df_player_list[df_player_list['year']>1966]
    df_player_list = df_player_list.reset_index(drop = True)

    key_list = []
    for i, row in df_player_list.iterrows():
        if row['選手名（英語）'] == 'Kazuki IWAMOTO':
            key_list += [(row['選手名（英語）'] + row['生年月日'] + row['最終所属']).replace(' ','')]
        else:
            key_list += [(row['選手名（英語）'] + row['生年月日']).replace(' ','')]

    df_tmp = pd.DataFrame(key_list, columns = ['key'])
    df_player_list = pd.concat([df_player_list, df_tmp],axis=1)

    key_list = []
    for i, row in df_player_list2.iterrows():
        if row['選手名（英字）'] == 'Kazuki IWAMOTO':
            key_list += [(row['選手名（英字）'] + row['生年月日'] + row['所属チーム']).replace(' ','')]
        else:
            key_list += [(row['選手名（英字）'] + row['生年月日']).replace(' ','')]

    df_tmp = pd.DataFrame(key_list, columns = ['key'])
    df_player_list2 = pd.concat([df_player_list2, df_tmp],axis=1)

    hight_list = []
    weight_list = []
    for i, row in df_player_list.iterrows():
        hight, weight = row['身長/体重'].split('/')
        hight_list += [hight]
        weight_list += [weight]

    df_tmp = pd.DataFrame(hight_list, columns = ['身長'])
    df_tmp２ = pd.DataFrame(weight_list, columns = ['体重'])
    df_player_list = pd.concat([df_player_list, df_tmp, df_tmp2],axis=1)

    df_marge = pd.merge(df_player_list, df_player_list2, 
                 on=['key'], how='left')

    df_marge.rename(columns={'選手名_x': '選手名', '生年月日_x': '生年月日'}, inplace=True)
    df_marge.drop(columns=['選手名_y', '生年月日_y', 'url', 'year', '選手名（英字）', '最終所属', 'key', '身長/体重'], inplace=True)
    
    # インデックスの振り直し
    df_marge.reset_index(drop = True)
    
    # csv出力
    df_marge.to_csv("data/marge/player_list.csv")
    
def make_toto_info_csv():
    df = pd.read_csv('data/toto/toto_info_cleaned.csv', index_col=0).reset_index(drop = True).copy()
    df = _df_rename_team(df, 'ホーム')
    df = _df_rename_team(df, 'アウェイ')
    
    drop_n_list = []
    drop_kind_list = []
    for i, row in df.iterrows():
        has_h = False
        has_a = False
        for i, team_list in enumerate(M_TEAM_NAMES):
            if row['ホーム'] in team_list:
                has_h = True
            if row['アウェイ'] in team_list:
                has_a = True
        if has_a and has_h:
            pass
        else:
            drop_n_list += [row['第n回']]
            drop_kind_list += [row['種別']]
    for i in range(len(drop_n_list)):
        df = df[(df['第n回'] != drop_n_list[i]) | (df['種別'] != drop_kind_list[i])].copy()
    
    df = df.reset_index(drop = True)
    df.to_csv("data/marge/toto_info.csv")