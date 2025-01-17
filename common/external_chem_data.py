# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 15:46:25 2024

@author: Gary
"""
import os
import pandas as pd
import ntpath

class Functional_Groups():
    """pulls the functional group info from chapGPT analysis into a 
    dataset for further processing."""
    
    def __init__(self):
        # self.indir = r"C:\Users\Gary\My Drive\webshare\scrape_data\chatGPT_functional_groups"
        self.indir = r"G:\My Drive\webshare\scrape_data\chatGPT_functional_groups"

        
    def get_fg(self,fn):
        cas = ntpath.basename(fn).split('_')[0]
        with open(fn,'r',encoding='utf-8') as f:
            alltext = f.readlines()
        fg = alltext[0].replace('**FG**','').strip().lower()
        return cas,fg
    
    def get_all(self):
        cas = []
        fg = []
        lst = os.listdir(self.indir)
        for fn in lst:
            if 'model_01-mini_funct_groups.txt' in fn:
                tup = self.get_fg(os.path.join(self.indir,fn))
                cas.append(tup[0])
                fg.append(tup[1])
        return pd.DataFrame({'bgCAS':cas,'funct_groups':fg})
    
    def get_fg_dict(self,df):
        dct = {}
        for i,row in df.iterrows():
            fglst = row.funct_groups.split(';')
            for fg in fglst:
                fg = fg.replace(':','').strip()
                if fg in dct.keys():
                    dct[fg].append(row.bgCAS)
                else:
                    dct[fg] = [row.bgCAS]
        return dct    