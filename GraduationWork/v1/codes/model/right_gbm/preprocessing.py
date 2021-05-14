import numpy as np
import pandas as pd
import datetime
from sklearn import preprocessing as pp

def preprocessing(toto_n, toto_kind):
    df = pd.read_csv('data/marge/marge.csv', index_col=0).reset_index(drop = True)
    M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()
    M_COACH_LIST = pd.read_csv('data/other/COACH_LIST.csv').columns.tolist()
    
    #     df = df[df['年月日'] < yyyyMMdd]
    df = df.dropna().reset_index(drop = True)
    
    df = get_train_test(toto_n, toto_kind, df)
    
    # ○○、○○成功率　をまとめる
    h_a = ['H_', 'A_']
    par_calumns = ['パス', 'クロス', 'スローイン', 'ドリブル', 'タックル']
    for head in h_a:
        for col in par_calumns:
            df[head+'成功した'+col] = df[head + col] * df[head + col + '成功率']/100
            df[head+'失敗した'+col] = df[head + col] - df[head+'成功した'+col]
            df.drop(columns = [head + col], inplace = True)
            df.drop(columns = [head + col + '成功率'], inplace = True)
    
    hour_list = []
    for i, row in df.iterrows():
        hour_list += [row['キックオフ時刻'][:2]]
    df_tmp = pd.DataFrame(hour_list, columns = ['キックオフ時'])
    df = pd.concat([df, df_tmp],axis=1)
    df.drop(columns = ['キックオフ時刻'], inplace = True)
    
    hare_list, ame_list, kumori_list, okunai_list = [], [], [], []
    j1_list, j2_list, j3_list = [], [], []
    h_df_list, h_mf_list, h_fw_list = [], [], []
    a_df_list, a_mf_list, a_fw_list = [], [], []
    h_rank_list, a_rank_list = [], []
    for i, row in df.iterrows():
        whether = row['天候']
        category = row['カテゴリ']

        H_positions = ''
        A_positions = ''
        for i in range(1, 12):
            H_positions += row['H_ポジション' + str(i)]
            A_positions += row['A_ポジション' + str(i)]

        h_df_list += [H_positions.count('DF')]
        h_mf_list += [H_positions.count('MF')]
        h_fw_list += [H_positions.count('FW')]
        a_df_list += [A_positions.count('DF')]
        a_mf_list += [A_positions.count('MF')]
        a_fw_list += [A_positions.count('FW')]
        
        h_rank_list += [str(row['H_順位']).replace('※', '')]
        a_rank_list += [str(row['A_順位']).replace('※', '')]
        
        if category == 'J1':
            j1_list += [1]
            j2_list += [0]
            j3_list += [0]
        elif category == 'J2':
            j1_list += [0]
            j2_list += [1]
            j3_list += [0]
        else:
            j1_list += [0]
            j2_list += [0]
            j3_list += [1]

        if 0 < whether.count('晴'):
            hare_list += [1]
        else:
            hare_list += [0]
        if 0 < whether.count('雨'):
            ame_list += [1]
        else:
            ame_list += [0]
        if 0 < whether.count('曇'):
            kumori_list += [1]
        else:
            kumori_list += [0]
        if 0 < whether.count('室内'):
            okunai_list += [1]
        else:
            okunai_list += [0]

    df_tmp1 = pd.DataFrame(hare_list, columns = ['晴_flg'])
    df_tmp2 = pd.DataFrame(ame_list, columns = ['雨_flg'])
    df_tmp3 = pd.DataFrame(kumori_list, columns = ['曇_flg'])
    df_tmp4 = pd.DataFrame(okunai_list, columns = ['室内_flg'])
    df_tmp5 = pd.DataFrame(j1_list, columns = ['J1_flg'])
    df_tmp6 = pd.DataFrame(j2_list, columns = ['J2_flg'])
    df_tmp7 = pd.DataFrame(j3_list, columns = ['J3_flg'])
    df_tmp8 = pd.DataFrame(h_df_list, columns = ['H_DF'])
    df_tmp9 = pd.DataFrame(h_mf_list, columns = ['H_MF'])
    df_tmp10 = pd.DataFrame(h_fw_list, columns = ['H_FW'])
    df_tmp11 = pd.DataFrame(a_df_list, columns = ['A_DF'])
    df_tmp12 = pd.DataFrame(a_mf_list, columns = ['A_MF'])
    df_tmp13 = pd.DataFrame(a_fw_list, columns = ['A_FW'])
    df_tmp14 = pd.DataFrame(h_rank_list, columns = ['H_順位'])
    df_tmp15 = pd.DataFrame(a_rank_list, columns = ['A_順位'])
    
    df = pd.concat([df, df_tmp1, df_tmp2, df_tmp3, df_tmp4, df_tmp5, df_tmp6, df_tmp7, df_tmp8, df_tmp9, df_tmp10, df_tmp11, df_tmp12, df_tmp13, df_tmp14, df_tmp15],axis=1)

    drop_colmuns = []
    for i in range(1, 12):
        drop_colmuns += ['H_ポジション' + str(i)]
        drop_colmuns += ['A_ポジション' + str(i)]
        drop_colmuns += ['H_選手' + str(i)]
        drop_colmuns += ['A_選手' + str(i)]
        
    df = team_to_index(df, 'H_Team')
    df = team_to_index(df, 'A_Team')
    df = coach_to_index(df)
    
    df.drop(columns = ['天候', 'カテゴリ', 'H_順位', 'A_順位'] + drop_colmuns, inplace = True)
    df.drop(columns = ['スタジアム', '入場者数', '気温', '湿度', '晴_flg', '雨_flg', '曇_flg', '室内_flg', 'キックオフ時'], inplace = True)
    
    df1 = df['train_test']
    df.drop(columns = ['train_test'], inplace = True)
    df = df.astype('float64')
    df = pd.concat([df, df1], axis = 1)
    
    category_columns = ['H_Team', 'A_Team', 'H_監督', 'A_監督']
    for column in category_columns:
        df[column] = pd.Series(df[column]).astype('category')
        
    df.to_csv("data/model/preprocessing.csv")
    
    return df

def team_to_index(df, tar_col):
    
    M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()
    
    df = df.copy()
    m_team_list = []
    for i, team_list in enumerate(M_TEAM_NAMES):
        m_team_list += [team_list[0]]

    team_list = []
    for i, row in df.iterrows():
        team_list += [m_team_list.index(row[tar_col])]
    df_tmp = pd.DataFrame(team_list, columns = [tar_col])
    df.drop(columns = [tar_col], inplace=True)
    df = pd.concat([df, df_tmp], axis=1)
    
    return df

def coach_to_index(df):
    M_COACH_LIST = pd.read_csv('data/other/COACH_LIST.csv', index_col=0).reset_index(drop = True).T.values[0].tolist()
    
    for i, row in df.iterrows():
        try:
            M_COACH_LIST.index(row['H_監督'])
        except ValueError:
            M_COACH_LIST += [row['H_監督']]
        try:
            M_COACH_LIST.index(row['A_監督'])
        except ValueError:
            M_COACH_LIST += [row['A_監督']]
    df_corch = pd.DataFrame(M_COACH_LIST, columns = ['監督名'])
    df_corch.to_csv("data/other/COACH_LIST.csv")
    
    df = df.copy()
    h_coach_list = []
    a_coach_list = []
    for i, row in df.iterrows():
        h_coach_list += [M_COACH_LIST.index(row['H_監督'])]
        a_coach_list += [M_COACH_LIST.index(row['A_監督'])]
            
    df.drop(columns = ['H_監督', 'A_監督'], inplace=True)
    df_tmp1 = pd.DataFrame(h_coach_list, columns = ['H_監督'])
    df_tmp2 = pd.DataFrame(a_coach_list, columns = ['A_監督'])
    df = pd.concat([df, df_tmp1, df_tmp2], axis=1)
    
    return df

def get_train_test(toto_n, toto_kind, df):
    train_columns = ['年月日', '節', 'H_勝点', 'H_試合', 'H_勝', 'H_分', 'H_敗', 'H_得点', 'H_失点', 'H_得失点差', 'H_rest_days', 'A_勝点', 'A_試合', 'A_勝', 'A_分', 'A_敗', 'A_得点', 'A_失点', 'A_得失点差', 'A_rest_days', 'J1_flg', 'J2_flg', 'J3_flg', 'H_DF', 'H_MF', 'H_FW', 'A_DF', 'A_MF', 'A_FW', 'H_Team', 'A_Team', 'H_監督', 'A_監督']

    df_toto = pd.read_csv("data/marge/toto_info.csv", index_col=0).reset_index(drop = True)
    df_toto = df_toto[(df_toto['第n回'] == toto_n) & (df_toto['種別'] == toto_kind)][['開催日', 'ホーム', 'アウェイ']].reset_index(drop = True)
    df = df.copy()

    df['train_test'] = 'train'
    df.loc[df['年月日'] >= df_toto.min(axis=0)['開催日'],  'train_test'] = 'test'
    for i, row in df_toto.iterrows():
        df.loc[(df['年月日'] == row['開催日']) & (df['H_Team'] == row['ホーム']) , 'train_test'] = 'toto'
    df = df[df['train_test'] != 'toto']

    common_columns = ['年月日', 'カテゴリ', '節', '天候', 'キックオフ時刻']
    h_a_columns = ['Team' , '監督' ,'順位' ,'勝点' ,'試合' ,'勝' ,'分' ,'敗' ,'得点' ,'失点' ,'得失点差' ,'rest_days' ,'ポジション1' ,'選手1' ,'ポジション2' ,'選手2' ,'ポジション3' ,'選手3' ,'ポジション4' ,'選手4' ,'ポジション5' ,'選手5' ,'ポジション6' ,'選手6' ,'ポジション7' ,'選手7' ,'ポジション8' ,'選手8' ,'ポジション9' ,'選手9' ,'ポジション10' ,'選手10' ,'ポジション11' ,'選手11' ,'goal']
    h_columns = []
    a_columns = []
    for col in h_a_columns:
        h_columns += ['H_' + col]
        a_columns += ['A_' + col]

    df_tmp1 = df[common_columns + h_columns + ['A_goal']]
    df_tmp1.columns = common_columns +h_a_columns + ['lost']
    df_tmp2 = df[common_columns + a_columns + ['H_goal']]
    df_tmp2.columns = common_columns +h_a_columns + ['lost']
    df_tmp = pd.concat([df_tmp1, df_tmp2])
    df_tmp = df_tmp.sort_values('年月日', ascending = False).copy()
    df_tmp.loc[df_tmp['goal'] == df_tmp['lost'], 'result'] = 0
    df_tmp.loc[df_tmp['goal'] < df_tmp['lost'], 'result'] = 2
    df_tmp.loc[df_tmp['goal'] > df_tmp['lost'], 'result'] = 1

    ini_val = [None for i in range(len(df.columns))]
    x_test = None
    for i, row in df_toto.iterrows():
        train_row = pd.DataFrame([ini_val], columns = df.columns)
        past_row_h = df_tmp[(df_tmp['Team'] == row['ホーム']) & (df_tmp['年月日'] < row['開催日'])].iloc[:1]
        past_row_a = df_tmp[(df_tmp['Team'] == row['アウェイ']) & (df_tmp['年月日'] < row['開催日'])].iloc[:1]

        train_row['年月日'] = row['開催日']
        dt_str = str(row['開催日'])
        dt1 = datetime.datetime(year=int(dt_str[:4]), month=int(dt_str[4:6]), day=int(dt_str[6:8]))
        train_row['H_Team'] = row['ホーム']
        train_row['A_Team'] = row['アウェイ']
        train_row['カテゴリ'] = past_row_h['カテゴリ'].values[0]
        train_row['節'] = int(past_row_h['節'].values[0]) + 1
        train_row['train_test'] = 'toto'
        
        # ここだけ仮
        train_row['キックオフ時刻'] = past_row_h['キックオフ時刻'].values[0]
        train_row['天候'] = past_row_h['天候'].values[0]

        for head in ['H_', 'A_']:
            if head == 'H_':
                past_row = past_row_h
            else:
                past_row = past_row_a

            train_row[head + '監督'] = past_row['監督'].values[0]
            train_row[head + '順位'] = past_row['順位'].values[0]
            train_row[head + '試合'] = int(past_row['試合'].values[0]) + 1
            train_row[head + '得点'] = int(past_row['得点'].values[0]) + (past_row['goal'].values[0])
            train_row[head + '失点'] = int(past_row['失点'].values[0]) + (past_row['lost'].values[0])
            train_row[head + '得失点差'] = int(train_row[head + '得点']) - int(train_row[head + '失点'])
            train_row[head + 'ポジション1'] = past_row['ポジション1'].values[0]
            train_row[head + '選手1'] = past_row['選手1'].values[0]
            train_row[head + 'ポジション2'] = past_row['ポジション2'].values[0]
            train_row[head + '選手2'] = past_row['選手2'].values[0]
            train_row[head + 'ポジション3'] = past_row['ポジション3'].values[0]
            train_row[head + '選手3'] = past_row['選手3'].values[0]
            train_row[head + 'ポジション4'] = past_row['ポジション4'].values[0]
            train_row[head + '選手4'] = past_row['選手4'].values[0]
            train_row[head + 'ポジション5'] = past_row['ポジション5'].values[0]
            train_row[head + '選手5'] = past_row['選手5'].values[0]
            train_row[head + 'ポジション6'] = past_row['ポジション6'].values[0]
            train_row[head + '選手6'] = past_row['選手6'].values[0]
            train_row[head + 'ポジション7'] = past_row['ポジション7'].values[0]
            train_row[head + '選手7'] = past_row['選手7'].values[0]
            train_row[head + 'ポジション8'] = past_row['ポジション8'].values[0]
            train_row[head + '選手8'] = past_row['選手8'].values[0]
            train_row[head + 'ポジション9'] = past_row['ポジション9'].values[0]
            train_row[head + '選手9'] = past_row['選手9'].values[0]
            train_row[head + 'ポジション10'] = past_row['ポジション10'].values[0]
            train_row[head + '選手10'] = past_row['選手10'].values[0]
            train_row[head + 'ポジション11'] = past_row['ポジション11'].values[0]
            train_row[head + '選手11'] = past_row['選手11'].values[0]
            train_row[head + '勝'] = past_row['勝'].values[0]
            train_row[head + '分'] = past_row['分'].values[0]
            train_row[head + '敗'] = past_row['敗'].values[0]

            reult = past_row['result'].values[0]
            if reult == 1:
                train_row[head + '勝'] = int(train_row[head + '勝']) + 1
                train_row[head + '勝点'] = int(past_row['勝点'].values[0]) + 3
            elif reult == 2:
                train_row[head + '敗'] = int(train_row[head + '敗']) + 1
                train_row[head + '勝点'] = int(past_row['勝点'].values[0]) + 0
            else:
                train_row[head + '分'] = int(train_row[head + '分']) + 1
                train_row[head + '勝点'] = int(past_row['勝点'].values[0]) + 1
            dt2_str = str(past_row['年月日'].values[0])
            dt2 = datetime.datetime(year=int(dt2_str[:4]), month=int(dt2_str[4:6]), day=int(dt2_str[6:8]))
            dt = dt1 - dt2
            train_row[head + 'rest_days'] = dt.days
        x_test = pd.concat([x_test, train_row])
    df = pd.concat([df, x_test])
    df= df.reset_index(drop = True)
    return df