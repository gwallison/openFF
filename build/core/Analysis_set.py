# -*- coding: utf-8 -*-
"""
@author: Gary

"""
import pandas as pd
import os
import openFF.common.file_handlers as fh

def make_full_set_file(sources,outdir):
    descfn = os.path.join(sources,'pickles','disclosures.parquet')
    recsfn = os.path.join(sources,'pickles','chemrecs.parquet')
    casfn = os.path.join(sources,'pickles','bgCAS.parquet')
    wsfn =  os.path.join(sources,'pickles','water_source.parquet')
    outfn = os.path.join(outdir,'full_df.parquet')
    
    df = pd.merge(fh.get_df(descfn),get_df(recsfn),on='DisclosureId',how='inner')
    df = pd.merge(fh.df,get_df(wsfn),on='DisclosureId',how='left',validate='m:1')
    df = pd.merge(fh.df,get_df(casfn),on='bgCAS',how='left',validate='m:1')
    
    df['in_std_filtered'] = ~(df.is_duplicate)&~(df.dup_rec)

    fh.save_df(df,outfn)
    return df

# def make_full_set_file_join(sources,outdir):
#     descfn = os.path.join(sources,'pickles','disclosures.parquet')
#     recsfn = os.path.join(sources,'pickles','chemrecs.parquet')
#     casfn = os.path.join(sources,'pickles','bgCAS.parquet')
#     outfn = os.path.join(outdir,'full_df.parquet')
    
#     df = get_df(descfn).set_index('DisclosureId')
#     df = df.join(get_df(recsfn).set_index('DisclosureId'),how='inner')
#     df = df.set_index('bgCAS')
#     df = df.join(get_df(casfn).set_index('bgCAS'),how='left')
#     df = df.reset_index()
    
#     df['in_std_filtered'] = ~(df.is_duplicate)&~(df.dup_rec)

#     save_df(df,outfn)
#     return df
