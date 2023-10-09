# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 14:31:11 2023

@author: garya

This set of routines is used as a standard way to interact with files in 
Open-FF.  

Dataframes will typically be stored and read as parquet.
default_file_type = 'parquet'

When dataframes need to be shared, such as when they need to be hand curated
in a spreadsheet, CSV can be generated and read with these routines

"""
import pandas as pd
import os


# this is the list of FF fields that should be treated as text columns in CSV file
lst_str_cols = ['APINumber','bgCAS','api10','IngredientName','CASNumber','test',
                'Supplier','OperatorName','TradeName','Purpose',
                'rawName','cleanName','xlateName',  # for companyXlate...
                ]

def store_df_as_csv(df,fn,encoding='utf-8',str_lst = lst_str_cols):
    # saves files in standard encoding, and adds single quote in first position
    # to columns in str_lst, to make them be interpreted as strings by excel, etc
    t = df.copy()
    for col in str_lst:
        if col in t.columns:
            # print(col)
            t[col] = "'"+t[col]
    t.to_csv(fn,encoding=encoding)
    
def get_csv(fn,check_zero=True,encoding='utf-8',sep=',',quotechar='"',
            str_cols = lst_str_cols):
    # check_zero: make sure str fields don't have an abundance of  "'" in zero position
    dict_dtypes = {x : 'str'  for x in str_cols}
    t = pd.read_csv(fn,encoding=encoding, low_memory=False, sep=sep,
                    quotechar=quotechar, dtype=dict_dtypes)
    if check_zero:
        for col in str_cols:
            if col in t.columns:
                #print(col)
                test = t[col].str[0]== "'"                
                assert test.sum()<int(len(t)/2), f'Initial single quote detected in more than half of col: {col}\nUsually means file destined for spreadsheet, not pandas.'
    return t

def save_df(df,fn):
    tup = os.path.splitext(fn)
    if tup[1]=='':
        df.to_parquet(fn+'.parquet')
    elif tup[1]=='csv':
        store_df_as_csv(df,fn)
    elif tup[1]=='parquet':
        df.to_parquet(fn)
    else:
        assert 1==0, f'File extension <{tup[1]}> not valid for "save_df"'
    
def get_df(fn,cols=None):
    tup = os.path.splitext(fn)
    if tup[1]=='':
        return pd.read_parquet(fn+'.parquet',columns=cols)
    elif tup[1]=='csv':
        return get_csv(fn)
    elif tup[1]=='parquet':
        return pd.read_parquet(fn,columns=cols)
    else:
        assert 1==0, f'File extension <{tup[1]}> not valid for "save_df"'
