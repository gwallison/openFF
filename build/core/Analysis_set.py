# -*- coding: utf-8 -*-
"""
Created on Wed May  5 14:22:20 2021

@author: Gary

"""
# import openFF.build.core.Table_manager as c_tab
import pandas as pd
import os
from openFF.common.file_handlers import save_df, get_df

def make_full_set_file(sources,outdir):
    descfn = os.path.join(sources,'pickles','disclosures.parquet')
    recsfn = os.path.join(sources,'pickles','chemrecs.parquet')
    casfn = os.path.join(sources,'pickles','bgCAS.parquet')
    outfn = os.path.join(outdir,'full_df.parquet')
    
    df = pd.merge(get_df(descfn),get_df(recsfn),on='UploadKey',how='inner')
    df = pd.merge(df,get_df(casfn),on='bgCAS',how='left')
    
    df['in_std_filtered'] = ~(df.is_duplicate)&~(df.dup_rec)

    save_df(df,outfn)
    return df

def make_full_set_file_join(sources,outdir):
    descfn = os.path.join(sources,'pickles','disclosures.parquet')
    recsfn = os.path.join(sources,'pickles','chemrecs.parquet')
    casfn = os.path.join(sources,'pickles','bgCAS.parquet')
    outfn = os.path.join(outdir,'full_df.parquet')
    
    df = get_df(descfn).set_index('UploadKey')
    df = df.join(get_df(recsfn).set_index('UploadKey'),how='inner')
    df = df.set_index('bgCAS')
    df = df.join(get_df(casfn).set_index('bgCAS'),how='left')
    df = df.reset_index()
    
    df['in_std_filtered'] = ~(df.is_duplicate)&~(df.dup_rec)

    save_df(df,outfn)
    return df
