import numpy as np
import pandas as pd
import datetime

M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()

def marge_csv():
    
    print('marge.csv作成')
    make_marge_csv()
    print('toto_info.csv作成')
    make_toto_info_csv()

def make_marge_csv():
    # 読み込み
    df_starting_member = pd.read_csv('data/j_league_data_site/j_starting_member_cleaned.csv', index_col=0)
    df_rank_table = pd.read_csv('data/j_league_data_site/j_rank_table_cleaned.csv', index_col=0)
    df_schedule = pd.read_csv('data/j_league_data_site/j_match_schedule_cleaned.csv', index_col=0)

    # 2012年〜現在のデータを抽出
    df_starting_member = df_starting_member[df_starting_member['年月日']>20120000]
    df_schedule = df_schedule[df_schedule['年月日'] != '未定'].astype({'年月日': int})
    df_schedule = df_schedule[df_schedule['年月日']>20120000]

    # チーム名を統一
    df_starting_member = _df_rename_team(df_starting_member, 'H_team')
    df_starting_member = _df_rename_team(df_starting_member, 'A_team')
    df_rank_table = _df_rename_team(df_rank_table, 'チーム')
    df_schedule = _df_rename_team(df_schedule, 'H_Team')
    df_schedule = _df_rename_team(df_schedule, 'A_Team')

    df_schedule = df_schedule[df_schedule['スコア'] != '中止']
    df_schedule = df_schedule.sort_values('年月日', ascending= False).reset_index(drop = True)

    H_A_rest_days = []
    for head in ['H_', 'A_']:
        rest_days = []
        for i, row in df_schedule.iterrows():
            team = row[head + 'Team']
            match_day = row['年月日']
            try:
                past_match_day = df_schedule[((df_schedule['H_Team']==team)|(df_schedule['A_Team']==team)) &(df_schedule['年月日']<match_day) ].iloc[:1]['年月日'].values[0]
                past_match_day = str(past_match_day)
                match_day = str(match_day)

                dt1 = datetime.datetime(year=int(match_day[:4]), month=int(match_day[4:6]), day=int(match_day[6:8]))
                dt2 = datetime.datetime(year=int(past_match_day[:4]), month=int(past_match_day[4:6]), day=int(past_match_day[6:8]))
                dt = dt1 - dt2
                rest_days += [dt.days]
            except IndexError:
                rest_days += [5]
        H_A_rest_days += [rest_days]
    df_schedule = df_schedule.assign(H_rest_days = H_A_rest_days[0], A_rest_days = H_A_rest_days[1] )

    # df_scheduleからJリーグの試合だけ抽出
    category_list = ['Ｊ１','Ｊ１ １ｓｔ', 'Ｊ１ ２ｎｄ', 'Ｊ２', 'Ｊ３']
    df_schedule = df_schedule[df_schedule['大会'].isin(category_list)]
    J1 = 'Ｊ１'
    df_schedule['大会'] = df_schedule['大会'].apply(lambda x : x.replace('Ｊ１ １ｓｔ', J1).replace('Ｊ１ ２ｎｄ',J1))

    df_schedule_future = df_schedule[df_schedule['スコア'] == 'vs'].reset_index(drop = True)
    df_schedule_past = df_schedule[df_schedule['スコア'] != 'vs'].reset_index(drop = True)
    
    h_goals, a_goals, goal_deffs = [], [], []
    for i, row in df_schedule_past.iterrows():
        h_goal = row['スコア'].split('-')[0]
        a_goal = row['スコア'].split('-')[1]
        h_goals += [h_goal]
        a_goals += [a_goal]
        goal_deffs += [int(h_goal) - int(a_goal)]
    df_tmp1 = pd.DataFrame(h_goals, columns = ['y_H_goal'])
    df_tmp2 = pd.DataFrame(a_goals, columns = ['y_A_goal'])
    df_tmp3 = pd.DataFrame(goal_deffs, columns = ['y_goal_deff'])
    df_schedule_past = pd.concat([df_schedule_past, df_tmp1, df_tmp2, df_tmp3],axis=1)

    df_schedule_past.loc[df_schedule_past['y_H_goal'] == df_schedule_past['y_A_goal'], 'y_even_flg'] = 1
    df_schedule_past.loc[df_schedule_past['y_H_goal'] != df_schedule_past['y_A_goal'], 'y_even_flg'] = 0
    df_schedule_past.loc[df_schedule_past['y_H_goal'] == df_schedule_past['y_A_goal'], 'y_H_result'] = 0
    df_schedule_past.loc[df_schedule_past['y_H_goal'] > df_schedule_past['y_A_goal'], 'y_H_result'] = 1
    df_schedule_past.loc[df_schedule_past['y_H_goal'] < df_schedule_past['y_A_goal'], 'y_H_result'] = 2
    
    df_schedule = pd.concat([df_schedule_past, df_schedule_future]).reset_index(drop = True)
    df_schedule.drop(columns = ['スコア'], inplace = True)

    # df_scheduleとdf_starting_memberをマージ
    df_marge = pd.merge(df_schedule, df_starting_member, 
             left_on=['年月日', 'H_Team', 'A_Team'],
             right_on=['年月日', 'H_team', 'A_team'], how='left')

    # df_marge にyearを追加
    year_list = []
    for i, row in df_marge.iterrows():
        year = str(row["年月日"])[:4]
        year_list += [int(year)]
    df_marge = df_marge.assign(year = year_list)
    df_marge['節'] = df_marge['節'].astype(int)

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
             right_on=['H_year', 'H_節', 'H_チーム'], how='left').drop(columns=['H_year', 'H_節', 'H_チーム'])

    # df_margeとdf_rank_table_Aをマージ
    df_marge = pd.merge(df_marge, df_rank_table_A, 
             left_on=['year', '節', 'A_Team'],
             right_on=['A_year', 'A_節', 'A_チーム'], how='left').drop(columns=['A_year', 'A_節', 'A_チーム'])

    df_marge.rename(columns={'スタジアム_x': 'スタジアム', '大会': 'カテゴリ'}, inplace=True)
    df_marge.drop(columns=['スタジアム_y', 'url', 'H_team', 'A_team', 'A_カテゴリ', 'year', 'H_カテゴリ'], inplace=True)

    columns = ['年月日', 'カテゴリ', '節', 'H_Team', 'A_Team', 'スタジアム', 'キックオフ時刻', '入場者数', '天候', '気温', '湿度', 'H_順位', 'H_勝点', 'H_試合', 'H_勝', 'H_分', 'H_敗', 'H_得点', 'H_失点', 'H_得失点差', 'H_rest_days', 'A_順位', 'A_勝点', 'A_試合', 'A_勝', 'A_分', 'A_敗', 'A_得点', 'A_失点', 'A_得失点差', 'A_rest_days', 'H_監督', 'A_監督', 'H_ポジション1', 'H_選手1', 'H_ポジション2', 'H_選手2', 'H_ポジション3', 'H_選手3', 'H_ポジション4', 'H_選手4', 'H_ポジション5', 'H_選手5', 'H_ポジション6', 'H_選手6', 'H_ポジション7', 'H_選手7', 'H_ポジション8', 'H_選手8', 'H_ポジション9', 'H_選手9', 'H_ポジション10', 'H_選手10', 'H_ポジション11', 'H_選手11', 'A_ポジション1', 'A_選手1', 'A_ポジション2', 'A_選手2', 'A_ポジション3', 'A_選手3', 'A_ポジション4', 'A_選手4', 'A_ポジション5', 'A_選手5', 'A_ポジション6', 'A_選手6', 'A_ポジション7', 'A_選手7', 'A_ポジション8', 'A_選手8', 'A_ポジション9', 'A_選手9', 'A_ポジション10', 'A_選手10', 'A_ポジション11', 'A_選手11', 'y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']
    df_marge = df_marge.reindex(columns=columns)

    # インデックスの振り直し
    df_marge.reset_index(drop = True)
    
    # バグ対、応急処置
    df_marge['カテゴリ'] = df_marge['カテゴリ'].apply(lambda x : x.replace('Ｊ１', 'J1'))
    df_marge['カテゴリ'] = df_marge['カテゴリ'].apply(lambda x : x.replace('Ｊ２', 'J2'))
    df_marge['カテゴリ'] = df_marge['カテゴリ'].apply(lambda x : x.replace('Ｊ３', 'J3'))
    
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