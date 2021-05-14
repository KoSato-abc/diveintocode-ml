from codes.scraping.j_league_data_site import j_league_data_site
from codes.scraping.toto import toto

class  scraping_all():
    
    def __init__(self):
        self.jlds = j_league_data_site.j_league_data_site()
        self.toto = toto.toto()
        
    def scraping_and_clean(self, only_new_data_flg):
        
        self.jlds.scraping_and_clean(only_new_data_flg)
        self.toto.scraping_and_clean(only_new_data_flg)