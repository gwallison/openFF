# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 19:40:01 2023

@author: garya

This is a collection of tools used to parse, summarize, store and display
the results from the ChemInformatics modules.
"""
import os
import pandas as pd
from openFF.common.file_handlers import save_df

class Process_SDF():
    def __init__(self,fn):
        self.fn = fn
        self.lines = []
        self.currline = 0
        self.allrecs = []

    def read_whole_sdf(self):
        #print('reading SDF')
        with open(self.fn, 'r') as f:
            self.lines = f.read().splitlines()
        
    def fetch_all_varnames(self):
        self.names = set()
        self.read_whole_sdf()
        for l in self.lines:
            #print(len(l),'|',l,'|')
            if (len(l)>0):
                if (l[0]=='>'):
                    self.names.add(l[3:-1])
        #print(self.names)
        
    def make_new_record(self):
        self.curr_rec = {}
        for v in self.names:
            self.curr_rec[v] = 'ND'
            
    def store_completed_record(self):
        self.allrecs.append(self.curr_rec)
        
    def process_all_lines(self):
        keep_long = ['CAS','Name','DTXSID']
        self.read_whole_sdf()
        self.fetch_all_varnames()
        self.make_new_record()
        while self.currline < len(self.lines)-1:
            self.currline += 1
            try:
                if self.lines[self.currline][0] == '>':
                    v = self.lines[self.currline][3:-1]
                    self.currline +=1 
                    value = self.lines[self.currline]
                    if not v in keep_long: # make authority values shorter
                        value = value[0]
                    self.curr_rec[v] = value
            except:
                pass
            if self.lines[self.currline] == '$$$$':
                self.store_completed_record()
                self.make_new_record()
                # print('end')
        print(f'Lines in ChemInformatics Hazard SDF file: {len(self.lines)}')
        print(f'Number of materials in chemInfo list: {len(self.allrecs)}')     
        self.df = pd.DataFrame(self.allrecs)
    

def sdf_extract(ci_source,out_dir):
    # pull scores and authority from the .sdf text files from the
    # Hazard module.  
    to_process = []
    lst = os.listdir(ci_source)
    for fn in lst:
        if fn[-4:] == '.sdf':
            if fn[:6]=='hazard':
                to_process.append(os.path.join(ci_source,fn))
    if len(to_process)!=1:
        print(to_process)
        assert 0==1,'Code only setup for exactly one file'
    pSDF = Process_SDF(to_process[0])
    pSDF.process_all_lines()
    save_df(pSDF.df,os.path.join(out_dir,'CI_sdf_summary.parquet'))
    
        
                
