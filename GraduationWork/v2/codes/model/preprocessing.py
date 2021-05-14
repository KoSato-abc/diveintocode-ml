import numpy as np
import pandas as pd
import datetime
from sklearn import preprocessing as pp

def preprocessing(toto_n, toto_kind, pred_par_day = False):
    
    M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()
    M_COACH_LIST = pd.read_csv('data/other/COACH_LIST.csv').columns.tolist()
    
    df = get_train_test(toto_n, toto_kind, pred_par_day)
    
    j1_list, j2_list, j3_list = [], [], []
    h_df_list, h_mf_list, h_fw_list = [], [], []
    a_df_list, a_mf_list, a_fw_list = [], [], []
    h_rank_list, a_rank_list = [], []
    for i, row in df.iterrows():
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
    
    drop_colmuns =['天候', 'カテゴリ', '気温', '湿度', 'キックオフ時刻', '入場者数', 'H_順位', 'A_順位']
    for i in range(1, 12):
        drop_colmuns += ['H_ポジション' + str(i)]
        drop_colmuns += ['A_ポジション' + str(i)]
        drop_colmuns += ['H_選手' + str(i)]
        drop_colmuns += ['A_選手' + str(i)]
    
    df.drop(columns = drop_colmuns, inplace = True)
    df = pd.concat([df, df_tmp5, df_tmp6, df_tmp7, df_tmp8, df_tmp9, df_tmp10, df_tmp11, df_tmp12, df_tmp13, df_tmp14, df_tmp15],axis=1)

    df = team_to_index(df, 'H_Team')
    df = team_to_index(df, 'A_Team')

    df1 = df['train_test']
    df.drop(columns = ['train_test'], inplace = True)
    
    for col in ['スタジアム', 'H_監督', 'A_監督']:
        target_column = df[col]
        le = pp.LabelEncoder()
        le.fit(target_column)
        label_encoded_column = le.transform(target_column)
        df[col] = pd.Series(label_encoded_column).astype('category')
    
    df = df.astype('float64')
    df = pd.concat([df, df1], axis = 1)
    
    category_columns = ['H_Team', 'A_Team', 'H_監督', 'A_監督', 'スタジアム']
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

def index_to_team(df, tar_col):
    df = df.copy()
    M_TEAM_NAMES = pd.read_csv('data/other/TEAM_NAMES.csv').values.tolist()

    team_list = []
    for i, row in df.iterrows():
        team_list += [M_TEAM_NAMES[int(row[tar_col])][0]]
    df_tmp = pd.DataFrame(team_list, columns = [tar_col])
    df.drop(columns = [tar_col], inplace=True)
    df = pd.concat([df, df_tmp], axis=1)
    return df

def get_train_test(toto_n, toto_kind, pred_par_day):

    df = pd.read_csv('data/marge/marge.csv', index_col=0).reset_index(drop = True)
    df_bk = df.copy()
    df = df.dropna().reset_index(drop = True)

    df_toto = pd.read_csv("data/marge/toto_info.csv", index_col=0).reset_index(drop = True)
    df_toto = df_toto[(df_toto['第n回'] == toto_n) & (df_toto['種別'] == toto_kind)][['開催日', 'ホーム', 'アウェイ']].reset_index(drop = True)

    df['train_test'] = 'train'
    df.loc[df['年月日'] >= df_toto.min(axis=0)['開催日'],  'train_test'] = 'test'
    for i, row in df_toto.iterrows():
        df.loc[(df['年月日'] == row['開催日']) & (df['H_Team'] == row['ホーム']) , 'train_test'] = 'toto'
    df = df[df['train_test'] != 'toto']
    df = df.sort_values('年月日', ascending = False).reset_index(drop = True)

    common_columns = ['年月日', 'カテゴリ', '節', 'スタジアム', 'キックオフ時刻', '入場者数', '天候', '気温', '湿度']
    h_columns = ['H_監督', 'H_ポジション1', 'H_選手1', 'H_ポジション2', 'H_選手2', 'H_ポジション3', 'H_選手3', 'H_ポジション4', 'H_選手4', 'H_ポジション5', 'H_選手5', 'H_ポジション6', 'H_選手6', 'H_ポジション7', 'H_選手7', 'H_ポジション8', 'H_選手8', 'H_ポジション9', 'H_選手9', 'H_ポジション10', 'H_選手10', 'H_ポジション11', 'H_選手11']
    a_columns = ['A_監督', 'A_ポジション1', 'A_選手1', 'A_ポジション2', 'A_選手2', 'A_ポジション3', 'A_選手3', 'A_ポジション4', 'A_選手4', 'A_ポジション5', 'A_選手5', 'A_ポジション6', 'A_選手6', 'A_ポジション7', 'A_選手7', 'A_ポジション8', 'A_選手8', 'A_ポジション9', 'A_選手9', 'A_ポジション10', 'A_選手10', 'A_ポジション11', 'A_選手11']
    tmp_columns = ['監督', 'ポジション1', '選手1', 'ポジション2', '選手2', 'ポジション3', '選手3', 'ポジション4', '選手4', 'ポジション5', '選手5', 'ポジション6', '選手6', 'ポジション7', '選手7', 'ポジション8', '選手8', 'ポジション9', '選手9', 'ポジション10', '選手10', 'ポジション11', '選手11']

    ini_columns = ['キックオフ時刻', '入場者数', '天候', '気温', '湿度', 'y_H_goal', 'y_A_goal', 'y_goal_deff', 'y_even_flg', 'y_H_result']

    x_toto = None
    for i, row in df_toto.iterrows():
        toto_row = df_bk[(df_bk['H_Team'] == row['ホーム'])&(df_bk['A_Team'] == row['アウェイ'])&(df_bk['年月日'] == row['開催日'])].copy()
        if toto_row.shape[0] == 0: # 過去の中止になった試合を予測したい時はデータを仮で作成
            toto_row = df_bk[(df_bk['H_Team'] == row['ホーム'])&(df_bk['A_Team'] == row['アウェイ'])&(df_bk['年月日'] < row['開催日'])][:1].copy()
            toto_row['年月日'] =row['開催日']

        toto_row[ini_columns] = None
        toto_row['train_test'] = 'toto'
        # ホーム
        past_row_h = df[((df['H_Team'] == row['ホーム']) | (df['A_Team'] == row['ホーム']))& (df['年月日'] < row['開催日'])].iloc[:1]
        if past_row_h['H_Team'].values[0] == row['ホーム']:
            past_row = past_row_h[ h_columns ].copy()
        else:
            past_row = past_row_h[a_columns].copy()
        past_row.columns = tmp_columns
        for col in tmp_columns:
            toto_row['H_' + col] = past_row[col].values[0]
        # アウェイ
        past_row_a = df[((df['H_Team'] == row['アウェイ']) | (df['A_Team'] == row['アウェイ']))& (df['年月日'] < row['開催日'])].iloc[:1]
        if past_row_a['H_Team'].values[0] == row['アウェイ']:
            past_row = past_row_a[ h_columns ].copy()
        else:
            past_row = past_row_a[a_columns].copy()
        past_row.columns = tmp_columns
        for col in tmp_columns:
            toto_row['A_' + col] = past_row[col].values[0]

        x_toto = pd.concat([x_toto, toto_row])

    df = pd.concat([df, x_toto])
    
    if pred_par_day:
        pass
    else:
        yyyyMMdd = str(df_toto.min(axis=0)['開催日'])
        drop_yyyyMMdd = int(yyyyMMdd[:4] + '0000')
        df.loc[(df['train_test'] != 'toto') & (df['年月日'] > drop_yyyyMMdd) & (df['年月日'] < drop_yyyyMMdd + 10000),  'train_test'] = 'drop'
        df = df[df['train_test'] != 'drop']
    df= df.reset_index(drop = True)
    return df