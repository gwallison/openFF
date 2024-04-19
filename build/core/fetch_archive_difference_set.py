# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 08:40:36 2024

@author: garya

Used to create dictionaries that summarize the differences between
two archived FracFocus bulk downloads

"""
import pandas as pd
import os

def get_difference_set_FFV4(early_arch_fn,late_arch_fn,verbose=True):
    """"""
    update_dict = {}
    cols_to_compare = ['DisclosureId','IngredientsId','APINumber','JobStartDate','JobEndDate',
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
    diffdf = concatdf[~(concatdf[cols_to_compare].duplicated(keep=False))]
    if verbose: print(f'number of differing records: {len(diffdf)}')
    update_dict['num_diff_records'] = len(diffdf)

    # find removed Disclosures
    edisc = diffdf[diffdf.df=='old'].DisclosureId.unique().tolist()
    ldisc = diffdf[diffdf.df=='new'].DisclosureId.unique().tolist()
    onlyold = []
    for dic in edisc:
        if not dic in ldisc:
            onlyold.append(dic)
    if len(onlyold)>0:
        gb = diffdf[(diffdf.df=='old')&(diffdf.DisclosureId.isin(onlyold))]\
          .groupby('DisclosureId',as_index=False)[['APINumber','OperatorName','JobEndDate']].first()
        update_dict['removed_disc'] = gb
    else:
        update_dict['removed_disc'] = pd.DataFrame()

    # find new Disclosures - use for "recent disclosures"
    onlynew = []
    for dic in ldisc:
        if not dic in edisc:
            onlynew.append(dic)
    update_dict['added_disc'] = onlynew

    # add new or changed disclosureIds -  used for browser updates
    update_dict['new_or_changed_disc'] = ldisc

    # find changed disclosure - that is, in both lists
    inboth = []
    for dic in ldisc:
        if  dic in edisc:
            inboth.append(dic)
    update_dict['changed_disc'] = inboth
    

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


if __name__ == '__main__':
    out = get_difference_set_FFV4(r"D:\archives\raw_df_archive\ff_archive_meta_2024-03-16.parquet",
                                  r"D:\archives\raw_df_archive\ff_archive_meta_2024-03-18.parquet")
    for k in out.keys():
        print(f'{k}: {len(out[k])}')