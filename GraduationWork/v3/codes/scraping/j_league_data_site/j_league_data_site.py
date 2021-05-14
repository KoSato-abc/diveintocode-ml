import numpy as np
import pandas as pd
import time
import datetime
import urllib.parse
from urllib.error import HTTPError

from codes.scraping.j_league_data_site import j_match_schedule, j_rank_table, j_starting_member

class j_league_data_site():
    
    def __init__(self):
        self.jMatchSchedule = j_match_schedule.j_match_schedule()
        self.jRankTable = j_rank_table.j_rank_table()
        self.jStartingMember = j_starting_member.j_starting_member()
    
    def  scraping(self, only_new_data_flg):
        
        self.jMatchSchedule.scraping(only_new_data_flg)
        self.jRankTable.scraping(only_new_data_flg)
        self.jStartingMember.scraping(only_new_data_flg)
    
    def  clean(self):
        
        self.jMatchSchedule.clean()
        self.jRankTable.clean()
        self.jStartingMember.clean()
    
    def  scraping_and_clean(self, only_new_data_flg):
        
        self.scraping(only_new_data_flg)
        self.clean()