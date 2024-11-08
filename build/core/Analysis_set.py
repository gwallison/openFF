# -*- coding: utf-8 -*-
"""
@author: Gary

"""
import pandas as pd
import os
import openFF.common.file_handlers as fh
import openFF.common.handles as hndl



def make_full_set_file(sources,outdir):
    descfn = os.path.join(sources,'pickles','disclosures.parquet')
    recsfn = os.path.join(sources,'pickles','chemrecs.parquet')
    casfn = os.path.join(sources,'pickles','bgCAS.parquet')
    wsfn =  os.path.join(sources,'pickles','water_source.parquet')
    outfn = os.path.join(outdir,'full_df.parquet')
    workingfn = os.path.join(outdir,'working_df.parquet')

    df = pd.merge(fh.get_df(descfn),fh.get_df(recsfn),on='DisclosureId',how='inner')
    # df = pd.merge(df,fh.get_df(wsfn),on='DisclosureId',how='left',validate='m:1')
    df = pd.merge(df,fh.get_df(casfn),on='bgCAS',how='left',validate='m:1')
    
    df['in_std_filtered'] = ~(df.is_duplicate)&~(df.dup_rec)
    df = df.set_index('reckey',drop=False,verify_integrity=True) # added to make pulling out subsets more robust (Nov 2024)
    fh.save_df(df,outfn)

    wdf = df[hndl.working_df_cols].copy()
    fh.save_df(wdf,workingfn)
    
    return df

