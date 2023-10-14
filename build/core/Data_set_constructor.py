# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 10:34:50 2019

@author: GAllison

This script performs the overall task of creating a FracFocus database from
the raw excel collection and creating the output data sets.

This version created from openFF-build in Jan 2023    
"""
import os
import openFF.build.core.Table_manager as c_tab


class Data_set_constructor():
    def __init__(self,rawdf,ref_dir,out_dir,extdir):
        self.ref_dir = ref_dir
        self.out_dir = out_dir
        self.pickledir = os.path.join(self.out_dir,'pickles')
        self.raw_df = rawdf
        #self.ext_dir = r"C:\MyDocs\OpenFF\data\external_refs"
        self.ext_dir = extdir
                           
    def _banner(self,text):
        print()
        print('*'*50)
        space = ' '*int((50 - len(text))/2)
        print(space,text,space)
        print('*'*50)
        
    def create_full_set(self):
        tab_const = c_tab.Table_constructor(pkldir=self.pickledir,
                                            outdir = self.out_dir,
                                            sources = self.ref_dir,
                                            extdir = self.ext_dir)
        self._banner('Table_manager')
        mark_missing = ['CASNumber','IngredientName','Supplier','OperatorName']
        for col in mark_missing:
            self.raw_df[col].fillna('MISSING',inplace=True)
        tab_const.assemble_all_tables(self.raw_df)
        print(f'  -- Number disclosure in table manager: {len(tab_const.tables["disclosures"])}')     
        
        return tab_const

