from codes.scraping import scraping_all
from codes.marge import marge
from codes.model import my_model_for_toto as my_model
from codes.simulation_toto import toto_simulator
from IPython.display import clear_output
import pandas as pd
import time
import os
from IPython.display import display

def clear():
    # os.system('cls')
    for i in range(100):
        print('')

def display_df(df):
    df = df.copy()
    df = df.round(2)
    df_columns = df.columns
    for col in df_columns:
        max_len = 0
        val_list = []
        for i, row in df.iterrows():
            if max_len < len(str(row[col])):
                max_len = len(str(row[col]))
        for i, row in df.iterrows():
            add_n = max_len - len(str(row[col]))
            add_s = ''
            for j in range(add_n):
                add_s += '　'
            val = str(row[col]) + add_s
            val_list += [val]
        df[col] =  val_list
    print(df)
                
while True:
    clear()
    print('1 : totoシミュレータ ')
    print('2 : データを更新する')
    key = input('')

    if key == '2':
        clear()
        sa = scraping_all.scraping_all()
        sa.scraping_and_clean(True)
        marge.marge_csv()
    elif key == '1':
        clear()
        df_toto = pd.read_csv('data/marge/toto_info.csv', index_col=0).reset_index(drop = True)
        df_toto = df_toto[['第n回', '種別']].drop_duplicates().sort_values(['第n回','種別'] , ascending=False).reset_index(drop = True)
        display_df(df_toto[:10])
        print('')
        print('n と 種別を入力')
        toto_n = input('n : ')
        toto_kind = input('種別 : ')
        try:
            toto_n = int(toto_n)
        except:
            toto_n = 0
        if df_toto[(df_toto['第n回'] == toto_n) & (df_toto['種別'] == toto_kind)].shape[0] == 1:
            clear()
            toto_sim = toto_simulator.get_toto_sim(toto_n, toto_kind)
            clear()
            display_df(toto_sim.show_df())
            print('')
            fands = input('軍資金 : ')
            try:
                fands = int(fands)
            except:
                fands = 100
            clear()
            display_df(toto_sim.get_result(fands))
            input('')
        else:
            pass
    else:
        pass