import numpy as np
import pandas as pd
import datetime
import time
from codes.scraping.football_lab import footballlab_stats

class football_lab():
    
    def __init__(self):
        self.footBallLabStats = footballlab_stats.footballlab_stats()
    
    def  scraping(self, only_new_data_flg):
        # footballlab_stats.csv
        self.footBallLabStats.scraping(only_new_data_flg)
    
    def  clean(self):
        # footballlab_stats.csv
        self.footBallLabStats.clean()
    
    def  scraping_and_clean(self, only_new_data_flg):
        # footballlab_stats.csv
        self.scraping(only_new_data_flg)
        self.clean()