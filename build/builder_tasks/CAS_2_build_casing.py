# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 13:09:22 2021

@author: Gary
"""

import os
import pandas as pd
from openFF.common.file_handlers import get_df

def is_casing_complete(df,work_dir): 
    casing = df.groupby(['CASNumber','IngredientName'],as_index=False).size()
    casing.columns = ['CASNumber','IngredientName','num_rec']
    #print(casing.head())
    master = get_df(os.path.join(work_dir,'casing_curated.parquet'))
    new = master[['CASNumber','IngredientName','bgCAS','first_date']]
    casing = pd.merge(casing,new,on=['CASNumber','IngredientName'],
                   how='outer',indicator=True)
    casing = casing[casing['_merge']=='left_only']
    print(f'Number of new CAS|ING pairs: {len(casing)}')
    if len(casing)>0:
        print(casing[casing['_merge']=='left_only'])

    flag1 = new.bgCAS.isna().sum()
    flag2 = new.first_date.isna().sum()
    flag3 = casing[['CASNumber','IngredientName']].duplicated().sum()
    if flag3>0:
        print('There appear to be duplicates of some CAS|ING pairs in the final')
    return (flag1+flag2+flag3)==0

def make_casing(df,ref_dir,work_dir): 
    casing = df.groupby(['CASNumber','IngredientName'],as_index=False).size()
    casing.columns = ['CASNumber','IngredientName','num_rec']
    master = get_df(os.path.join(ref_dir,'curation_files','casing_curated.parquet'))
    old = master[['CASNumber','IngredientName','bgCAS','first_date']]
    casing = pd.merge(casing,old,on=['CASNumber','IngredientName'],
                   how='outer',indicator=True)
    casing = casing[casing['_merge']=='left_only']
    
    print(f'Number of new CAS|ING pairs: {len(casing)}')

    CAS_cur = get_df(os.path.join(work_dir,'CAS_curated.parquet'))
    print(CAS_cur[CAS_cur.CASNumber.duplicated()])
    mg = pd.merge(casing,CAS_cur[['CASNumber','curatedCAS','categoryCAS']],
                  on='CASNumber',how='left',validate='m:1')
    return mg.drop(['_merge'],axis=1)

