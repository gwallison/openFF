# -*- coding: utf-8 -*-
"""

Adpated Company list to make the bgPurpose generator
Nov 2024

@author: Gary
"""

import os
import shutil
import pandas as pd
import numpy as np
# import intg_support.common
from  openFF.common.file_handlers import store_df_as_csv, get_csv, save_df, get_df
from  openFF.common.text_handlers import sort_id, xlate_to_str

def get_old_xlate_df(ref_dir):
    try:
        old = get_df(os.path.join(ref_dir,'curation_files','purpose_xlate.parquet'))
    except:
        print('NOT FOUND: Reference file of Purposes.')
    return old

def get_new_xlate_df(ref_dir):
    try:
        fn = os.path.join(ref_dir,'purpose_xlate_modified.csv')
        # new = get_csv(fn)
        new = pd.read_csv(fn,keep_default_na=False)
    except:
        print('NOT FOUND: Modified file of Purpose values.')
    return new

def make_xlate_df(raw_df):
    gb = raw_df.groupby(['Purpose','DisclosureId'],as_index=False)['CASNumber'].count()
    gbo = gb.groupby('Purpose',as_index=False)['DisclosureId'].count().\
        rename({'DisclosureId':'PurpCount'},axis=1)
    gbyo = raw_df.groupby(['Purpose'])['year'].apply(set).reset_index()
    gbyo.year = gbyo.year.map(lambda x: sort_id(x))
    gbyo.year = gbyo.year.map(lambda x: xlate_to_str(x,'; ',trunc=False))
    gbyo.rename({'year':'PurpYears'},axis=1,inplace=True)
    oout = pd.merge(gbo,gbyo,on='Purpose',how='left')
    oout['rawName'] = oout.Purpose

    # gbs = raw_df.groupby(['Supplier'],as_index=False)['CASNumber'].count().\
    #     rename({'CASNumber':'SupCount'},axis=1)
    # gbys = raw_df.groupby(['Supplier'])['year'].apply(set).reset_index()
    # gbys.year = gbys.year.map(lambda x: sort_id(x))
    # gbys.year = gbys.year.map(lambda x: xlate_to_str(x,'; ',trunc=False))
    # gbys.rename({'year':'SupplierYears'},axis=1,inplace=True)
    # sout = pd.merge(gbs,gbys,on='Supplier',how='left')
    # sout['rawName'] = sout.Supplier
    
    # out = pd.merge(oout,sout,on='rawName',how='outer')
    # out.OpCount = out.OpCount.fillna(0)
    # out.SupCount = out.SupCount.fillna(0)
    # out.OperatorYears = out.OperatorYears.fillna('')
    # out.SupplierYears = out.SupplierYears.fillna('')
    oout.PurpCount = oout.PurpCount.fillna(0)
    oout.PurpYears = oout.PurpYears.fillna('-')
    # oout.rawName = oout.rawName.fillna('MISSING')
    return oout[['rawName','PurpCount','PurpYears']]
    
# def add_new_to_Xlate(rawdf,ref_dir,out_dir):
#     old = get_old_xlate_df(ref_dir)
#     #old['cleanName'] = old.rawName.str.lower()
#     oldlst = old.rawName.unique().tolist()
    
#     newdf = make_xlate_df(rawdf)
#     mg = pd.merge(old[['rawName','xlateName','status','first_date',
#                        'change_date','change_comment']],
#                   newdf,on='rawName',how='outer')
#     mg['is_new'] = np.where(mg.rawName.isin(oldlst),'NO','YES')
#     mg['cleanName'] = mg.rawName.str.lower()
#     mg = mg.sort_values('is_new',ascending=False)

#     print(f'\nNumber of new Purpose lines to curate: {len(mg[mg.is_new=="YES"])}')
#     if len(mg[mg.is_new=="YES"])==0:
#         print('Transferring original purpose list to working directory')
#         shutil.copy(os.path.join(ref_dir,'curation_files','purpose_xlate.parquet'),
#                     os.path.join(out_dir))        
#     else:
#         mg['str_len'] = mg.rawName.str.len()
#         mg = mg[['rawName', 'cleanName','xlateName','str_len','is_new',
#             'PurpCount', 'PurpYears', #'SupCount','SupplierYears', 
#             'status', 'first_date', 'change_date',
#             'change_comment']]
#         store_df_as_csv(mg,os.path.join(out_dir,'purpose_xlateNEW.csv'))
#     return mg


# Function to strip leading single and double quotes
def strip_leading_quotes(text):
    return text.lstrip("\"'")

# # Apply the function to the string_field column
# df['stripped_field'] = df['string_field'].apply(strip_leading_quotes)

# # Print the updated DataFrame
# print(df)

def add_new_to_Xlate(rawdf,ref_dir,out_dir):
    old = get_old_xlate_df(ref_dir)
    #old['cleanName'] = old.rawName.str.lower()
    oldlst = old.rawName.unique().tolist()
    
    newdf = make_xlate_df(rawdf)
    mg = pd.merge(old[['rawName','xlateName','status','first_date',
                       'change_date','change_comment']],
                  newdf,on='rawName',how='outer')
    mg['is_new'] = np.where(mg.rawName.isin(oldlst),'NO','YES')
    mg['cleanName'] = mg.rawName.apply(strip_leading_quotes)
    # have to do it twice because of some very messy entries
    mg['cleanName'] = mg.cleanName.apply(strip_leading_quotes)
    mg['cleanName'] = mg.cleanName.str.strip().str.lower()
    mg = mg.sort_values('is_new',ascending=False)

    print(f'\nNumber of new Purpose lines to curate: {len(mg[mg.is_new=="YES"])}')
    if len(mg[mg.is_new=="YES"])==0:
        print('Transferring original purpose list to working directory')
        shutil.copy(os.path.join(ref_dir,'curation_files','purpose_xlate.parquet'),
                    os.path.join(out_dir))        
    else:
        mg['str_len'] = mg.rawName.str.len()
        mg = mg[['rawName', 'cleanName','xlateName','str_len','is_new',
            'PurpCount', 'PurpYears', #'SupCount','SupplierYears', 
            'status', 'first_date', 'change_date',
            'change_comment']]
        store_df_as_csv(mg,os.path.join(out_dir,'purpose_xlateNEW.csv'))
    return mg

def is_purpose_complete(work_dir):
    try:
        purposes = get_new_xlate_df(work_dir)
        print(len(purposes))
        c1 = purposes.xlateName.isna().sum()==0
        c2 = purposes.status.isna().sum()==0
        c3 = purposes.first_date.isna().sum()==0
        save_df(purposes,os.path.join(work_dir,'purpose_xlate.parquet'))
        print(c1, c2, c3)
        if ~(c1&c2&c3):
            print(purposes[c1|c2|c3])
            print('Apparent incomplete purpose_xlate_modified.csv file!')
        return (c1&c2&c3)    
    except:
        print('Something wrong with the purpose_xlate_modified file')
        return False
 