# -*- coding: utf-8 -*-
"""
Created on Thu May 20 12:59:40 2021


Adapted in Jan 2023 for cloud use

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
        old = get_df(os.path.join(ref_dir,'curation_files','company_xlate.parquet'))
    except:
        print('NOT FOUND: Reference file of company names.')
    return old

def get_new_xlate_df(ref_dir):
    try:
        fn = os.path.join(ref_dir,'company_xlate_modified.csv')
        # new = get_csv(fn)
        new = pd.read_csv(fn,keep_default_na=False)
    except:
        print('NOT FOUND: Modified file of company names.')
    return new

def make_xlate_df(raw_df):
    gb = raw_df.groupby(['OperatorName','DisclosureId'],as_index=False)['CASNumber'].count()
    gbo = gb.groupby('OperatorName',as_index=False)['DisclosureId'].count().\
        rename({'DisclosureId':'OpCount'},axis=1)
    gbyo = raw_df.groupby(['OperatorName'])['year'].apply(set).reset_index()
    gbyo.year = gbyo.year.map(lambda x: sort_id(x))
    gbyo.year = gbyo.year.map(lambda x: xlate_to_str(x,'; ',trunc=False))
    gbyo.rename({'year':'OperatorYears'},axis=1,inplace=True)
    oout = pd.merge(gbo,gbyo,on='OperatorName',how='left')
    oout['rawName'] = oout.OperatorName

    gbs = raw_df.groupby(['Supplier'],as_index=False)['CASNumber'].count().\
        rename({'CASNumber':'SupCount'},axis=1)
    gbys = raw_df.groupby(['Supplier'])['year'].apply(set).reset_index()
    gbys.year = gbys.year.map(lambda x: sort_id(x))
    gbys.year = gbys.year.map(lambda x: xlate_to_str(x,'; ',trunc=False))
    gbys.rename({'year':'SupplierYears'},axis=1,inplace=True)
    sout = pd.merge(gbs,gbys,on='Supplier',how='left')
    sout['rawName'] = sout.Supplier
    
    out = pd.merge(oout,sout,on='rawName',how='outer')
    out.OpCount = out.OpCount.fillna(0)
    out.SupCount = out.SupCount.fillna(0)
    out.OperatorYears = out.OperatorYears.fillna('')
    out.SupplierYears = out.SupplierYears.fillna('')
    return out[['rawName','OpCount','OperatorYears','SupCount','SupplierYears']]
    
def add_new_to_Xlate(rawdf,ref_dir,out_dir):
    old = get_old_xlate_df(ref_dir)
    #old['cleanName'] = old.rawName.str.lower()
    oldlst = old.rawName.unique().tolist()
    
    newdf = make_xlate_df(rawdf)
    mg = pd.merge(old[['rawName','xlateName','status','first_date',
                       'change_date','change_comment']],
                  newdf,on='rawName',how='outer')
    mg['is_new'] = np.where(mg.rawName.isin(oldlst),'NO','YES')
    mg['cleanName'] = mg.rawName.str.lower()
    mg = mg.sort_values('is_new',ascending=False)

    print(f'\nNumber of new company lines to curate: {len(mg[mg.is_new=="YES"])}')
    if len(mg[mg.is_new=="YES"])==0:
        print('Transferring original company list to working directory')
        shutil.copy(os.path.join(ref_dir,'curation_files','company_xlate.parquet'),
                    os.path.join(out_dir))        
    else:
        mg = mg[['rawName', 'cleanName','xlateName','is_new', 
            'OpCount', 'OperatorYears', 'SupCount','SupplierYears', 
            'status', 'first_date', 'change_date',
            'change_comment']]
        store_df_as_csv(mg,os.path.join(out_dir,'company_xlateNEW.csv'))
    return mg

def is_company_complete(work_dir):
    try:
        companies = get_new_xlate_df(work_dir)
        print(len(companies))
        c1 = companies.xlateName.isna().sum()==0
        c2 = companies.status.isna().sum()==0
        c3 = companies.first_date.isna().sum()==0
        save_df(companies,os.path.join(work_dir,'company_xlate.parquet'))
        if ~(c1&c2&c3):
            print(companies[c1|c2|c3])
            print('Apparent incomplete companies_xlate_modified.csv file!')
        return (c1&c2&c3)    
    except:
        print('Something wrong with the company_xlate_modified file')
        return False
 