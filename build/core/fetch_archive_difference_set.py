# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 08:40:36 2024

@author: garya

Used to create dictionaries that summarize the differences between
two archived FracFocus bulk downloads

"""
import pandas as pd
import numpy as np
import os

def get_difference_set(early_arch_fn,late_arch_fn,df_ver=4,verbose=True):
    """"""
    update_dict = {}
    if df_ver==4:
        cols_to_compare = ['DisclosureId','IngredientsId','APINumber','JobStartDate','JobEndDate',
                           'OperatorName','Supplier','WellName','TotalBaseWaterVolume','TotalBaseNonWaterVolume',
                           'TradeName','Purpose','CASNumber','IngredientName','PercentHighAdditive','PercentHFJob',
                           'MassIngredient']
    else:
        cols_to_compare = ['UploadKey','IngredientKey','APINumber','JobStartDate','JobEndDate',
                           'OperatorName','Supplier','WellName','TotalBaseWaterVolume','TotalBaseNonWaterVolume',
                           'TradeName','Purpose','CASNumber','IngredientName','PercentHighAdditive','PercentHFJob',
                           'MassIngredient']

    if verbose: print(f'fetching {early_arch_fn}')
    edf = pd.read_parquet(os.path.join(early_arch_fn))
    ecols = edf.columns.tolist()
    edf['df'] = 'old'
    if verbose: print(f'fetching {late_arch_fn}')
    ldf = pd.read_parquet(os.path.join(late_arch_fn))
    lcols = ldf.columns.tolist()
    ldf['df'] = 'new'
    # column check
    try:
        assert ecols.sort() == lcols.sort()
        update_dict['columns'] = 'Columns identical'
    except:
        update_dict['columns'] = 'COLUMNS differ between archives!'
        print('COLUMNS differ between archives!')
        print(f'Earlier: {ecols}\n')
        print(f'Later  : {lcols}\n')

    if verbose: print('concatenating')
    concatdf = pd.concat([edf,ldf])
    if verbose: print('finding differences...')
    diffdf = concatdf[~(concatdf[cols_to_compare].duplicated(keep=False))].copy()
    if verbose: print(f'number of differing records: {len(diffdf)}')
    update_dict['num_diff_records'] = len(diffdf)
    
    if df_ver==4:
        diffdf['discID'] = diffdf['DisclosureId']
    else:
        diffdf['discID'] = diffdf['UploadKey']

    # find removed Disclosures
    edisc = diffdf[diffdf.df=='old'].discID.unique().tolist()
    ldisc = diffdf[diffdf.df=='new'].discID.unique().tolist()
    onlyold = []
    for dic in edisc:
        if not dic in ldisc:
            onlyold.append(dic)
    if len(onlyold)>0:
        gb = diffdf[(diffdf.df=='old')&(diffdf.discID.isin(onlyold))]\
          .groupby('discID',as_index=False)[['APINumber','OperatorName','JobEndDate']].first()
        update_dict['removed_disc'] = gb
    else:
        update_dict['removed_disc'] = pd.DataFrame()

    # find new Disclosures - use for "recent disclosures"
    onlynew = []
    for dic in ldisc:
        if not dic in edisc:
            onlynew.append(dic)
    if len(onlynew)>0:
        gb = diffdf[(diffdf.df=='new')&(diffdf.discID.isin(onlynew))]\
          .groupby('discID',as_index=False)[['APINumber','OperatorName','JobEndDate']].first()
        update_dict['added_disc'] = gb
        # print(gb.head())
    else:
        update_dict['added_disc'] = pd.DataFrame()
    # update_dict[] = onlynew

    # add new or changed disclosureIds -  used for browser updates
    update_dict['new_or_changed_disc'] = ldisc

    # find changed disclosure - that is, in both lists
    inboth = []
    for dic in ldisc:
        if  dic in edisc:
            inboth.append(dic)
    if len(inboth)>0:
        gb = diffdf[(diffdf.df=='new')&(diffdf.discID.isin(inboth))]\
          .groupby('discID',as_index=False)[['APINumber','OperatorName','JobEndDate']].first()
        update_dict['changed_disc'] = gb
    else:
        update_dict['changed_disc'] = pd.DataFrame()
    # update_dict['changed_disc'] = inboth
    

    # CASing involved in changes
    t = diffdf[~diffdf[['CASNumber','IngredientName']].duplicated(keep='first')][['CASNumber','IngredientName']].copy()
    lst = [tuple(r) for r in t.to_numpy().tolist()]
    update_dict['casing'] = lst

    # Operators involved in changes
    update_dict['OperatorName'] = diffdf.OperatorName.unique().tolist()

    # State/county pairs in changes
    t = diffdf[~diffdf[['StateName','CountyName']].duplicated(keep='first')][['StateName','CountyName']].copy()
    lst = [tuple(r) for r in t.to_numpy().tolist()]
    update_dict['state_county'] = lst
    
    return update_dict

def scan_for_col_incompatibility(raw_dir):
    # using columns=None in read_parquet returns just the header
    change_dates = []
    files = os.listdir(raw_dir)
    files.sort() # put them in chronological order
    efn = files[0]
    edf = pd.read_parquet(os.path.join(raw_dir,efn),columns=None)
    ecols = edf.columns.tolist()
    ecols.sort()
    for lfn in files[1:]:
        print(lfn)
        ldf = pd.read_parquet(os.path.join(raw_dir,lfn),columns=None)
        lcols = ldf.columns.tolist()
        lcols.sort()
        if ecols!=lcols:
            change_dates.append(lfn)
            print(f'Column discontinuity! {efn}, {lfn}')
            print(f'Early list: {ecols}')
            print(f'Late list:  {lcols}')
        # prep for next file
        efn = lfn
        edf = ldf
        ecols = lcols
        
    print(f'Files where change is introduced: {change_dates}')
        
    

def make_multiple_sets(raw_dir,early_tup=(2024,3,1),late_tup=(),
                       out_dir='./tmp',df_ver=4,verbose=False):
    import datetime
    import pickle
    
    if len(early_tup)==3:
        edate = datetime.datetime(early_tup[0],early_tup[1],early_tup[2])
    else:
        edate = datetime.datetime(2024,3,1)

    if len(late_tup)==3:
        ldate = datetime.datetime(late_tup[0],late_tup[1],late_tup[2])
    else:
        ldate = datetime.today()
        
    # first make list of files to use
    lst = os.listdir(raw_dir)
    lst.sort()
    sel_fn = []
    print('Making file list')
    for fn in lst:
        tdate = datetime.datetime(int(fn[7:11]),int(fn[12:14]),int(fn[15:16]))
        if (tdate>=edate)&(tdate<=ldate):
            sel_fn.append(fn)

    efn = os.path.join(raw_dir,sel_fn[0])
    for fn in sel_fn[1:]:
        print(fn)
        lfn = os.path.join(raw_dir,fn)
        outdict = get_difference_set(efn,lfn,df_ver=df_ver)        
        outfn = os.path.join(out_dir,f'diff_dict_{fn[7:17]}.pkl')
        with open(outfn,'wb') as f:
            pickle.dump(outdict,f)
        efn = lfn
    
            
                                  


if __name__ == '__main__':
    # scan_for_col_incompatibility(raw_dir=r"D:\openFF_archive\raw_dataframes")
    make_multiple_sets(raw_dir=r"D:\openFF_archive\raw_dataframes",
                       early_tup=(2018,1,1),late_tup=(2023,12,2),
                       out_dir = r"D:\openFF_archive\diff_dicts",
                       df_ver=3)
    make_multiple_sets(raw_dir=r"D:\openFF_archive\raw_dataframes",
                       early_tup=(2023,12,3),late_tup=(),
                       out_dir = r"D:\openFF_archive\diff_dicts",
                       df_ver=4)