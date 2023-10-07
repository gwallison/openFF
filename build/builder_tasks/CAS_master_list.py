# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 09:00:34 2021

@author: Gary

This creates the initial data frame of the CAS master list.  

The CASNumber and IngredientName values are unmodified. They may contain
new line characters, etc.
"""
import pandas as pd
import numpy as np
import os
import shutil
import core.cas_tools as ct
from core.file_handlers import store_df_as_csv, get_csv, save_df, get_df
import sys
        

# def get_CAS_ref_df(work_dir='./work_dir/'):
#     return get_df(os.path.join(work_dir,'CAS_ref_and_names.parquet'))

def get_CAS_ref_df(ref_dir='orig_dir'):
    return get_df(os.path.join(ref_dir,'curation_files','master_cas_number_list.parquet'))

def get_CAS_deprecated(ref_dir='orig_dir'):
    return get_df(os.path.join(ref_dir,'curation_files','CAS_deprecated.parquet'))

def get_orig_curated_CAS_list(orig_dir='./orig_dir/'):
    return get_df(os.path.join(orig_dir,'curation_files','CAS_curated.parquet'))

def get_new_curated_CAS_list(work_dir='./work_dir/'):
    return get_csv(os.path.join(work_dir,'CAS_curated_modified.csv'))

def save_comptox_search_list(work_dir = './work_dir/'):
    df = get_new_curated_CAS_list(work_dir)
    gb = df.groupby('curatedCAS',as_index=False).size()
    store_df_as_csv(gb,os.path.join(work_dir,'comptox_search_list.csv'))

def is_new_complete(work_dir='/work_dir/'):
    try:    
        df = get_new_curated_CAS_list()
        f1 = df.first_date.isna().sum()
        f2 = df.curatedCAS.isna().sum()
        if f1+f2==0:
            save_df(df,os.path.join(work_dir,'CAS_curated.parquet'))
            save_comptox_search_list(work_dir)
        return (f1+f2)==0
    except:
        print('No file named "CAS_curate_modified.cas" found.  Assuming you want to proceed...')
        return True
    
def get_new_CAS_list(rawdf):
    return rawdf.groupby(['CASNumber'],as_index=False).size()

def copy_CAS_curated(source,dest):
    shutil.copy(os.path.join(source,'curation_files','CAS_curated.parquet'),dest)


def get_new_tentative_CAS_list(rawdf,orig_dir='./orig_dir/',work_dir='./work_dir/'):
    """Answers the question: are there new tentative CASNumbers that need to be
    added to the CAS SciFinder reference?"""
    old = get_orig_curated_CAS_list(orig_dir)
    new = get_new_CAS_list(rawdf)
    mg = pd.merge(new,old,on=['CASNumber'],
                  how = 'outer',indicator=True)

    new = mg[mg['_merge']=='left_only'].copy() # only want new stuff
    new = new[['CASNumber']]    
    new['clean_wo_work'] = new.CASNumber.map(lambda x: ct.is_valid_CAS_code(x))
    
    new['tent_CAS'] = new.CASNumber.map(lambda x:ct.cleanup_cas(x))
    new['valid_after_cleaning'] = new.tent_CAS.map(lambda x: ct.is_valid_CAS_code(x))

    new['auto_status'] = np.where(new.clean_wo_work,'perfect','unk')
    new.auto_status = np.where((new.auto_status=='unk')&(new.valid_after_cleaning),
                               'cleaned',new.auto_status)
    # get CAS_ref_list
    # CAS_ref = get_CAS_ref_df(work_dir)
    CAS_ref = get_CAS_ref_df(orig_dir)
    casreflist = CAS_ref.cas_number.tolist()
    new['tent_is_in_ref'] = new.tent_CAS.isin(casreflist)

    # check against deprecated
    deprecated = get_CAS_deprecated(orig_dir)
    deprecated.rename({'deprecated':'tent_CAS',
                       'cas_replacement':'deprecated_replacement'},axis=1,inplace=True)
    new = pd.merge(new,deprecated,on='tent_CAS',how='left')

    if len(new)==0:
        # No curation necessary; copy original CAS_curated to the working dir.
        copy_CAS_curated(orig_dir, work_dir)
        
    return new
    
###  OLD VERSION    
# def first_pass_CAS_master_list(rawdf,orig_dir='./orig_dir/',work_dir='./out/'): # rawdf
#     """this function is used on the first pass for the CAS master list. """
    
#     old = pd.read_csv(os.path.join(orig_dir,'curation_files','CAS_curated.csv'),
#                       quotechar='$',
#                       encoding='utf-8')
#     old = old[['CASNumber']]
#     ct.na_check(old,txt='CAS_1 for old')
#     new = rawdf.groupby(['CASNumber'],as_index=False).size()

#     # check if there are non-printable characters in CASNumbers
#     new.CASNumber.map(lambda x: ct.has_non_printable(x))

#     mg = pd.merge(new,old,on=['CASNumber'],
#                   how = 'outer',indicator=True)
#     ct.na_check(mg,txt='CAS_1 for mg')

#     new = mg[mg['_merge']=='left_only'].copy() # only want new stuff
#     new = new[['CASNumber']]    
#     new['clean_wo_work'] = new.CASNumber.map(lambda x: ct.is_valid_CAS_code(x))
    
#     new['tent_CAS'] = new.CASNumber.map(lambda x:ct.cleanup_cas(x))
#     new['valid_after_cleaning'] = new.tent_CAS.map(lambda x: ct.is_valid_CAS_code(x))
#     ct.na_check(new,txt='CAS_1 for new')   
#     new['auto_status'] = np.where(new.clean_wo_work,'perfect','unk')
#     new.auto_status = np.where((new.auto_status=='unk')&(new.valid_after_cleaning),
#                                'cleaned',new.auto_status)
#     # get CAS_ref_list
#     CAS_ref = pd.read_csv(os.path.join(work_dir,'CAS_ref_and_names.csv'),
#                           quotechar='$',
#                           encoding='utf-8')
#     casreflist = CAS_ref.cas_number.tolist()
#     new['tent_is_in_ref'] = new.tent_CAS.isin(casreflist)

#     # check against deprecated
#     deprecated = pd.read_csv(os.path.join(work_dir,'CAS_deprecated.csv'),
#                           quotechar='$',
#                           encoding='utf-8')
#     deprecated.rename({'deprecated':'tent_CAS',
#                        'cas_replacement':'deprecated_replacement'},axis=1,inplace=True)
#     # print(deprecated.head())
#     new = pd.merge(new,deprecated,on='tent_CAS',how='left')

#     return new

def make_CAS_to_curate_file(df,ref_dir='/old_dir/',work_dir = './work_dir/'):
    # df is the new cas values with cas_tool fields included
    # fetch the reference dataframes

    # ref = pd.read_csv(os.path.join(work_dir,'CAS_ref_and_names.csv'),
    #                   encoding='utf-8',quotechar='$')
    # dep = pd.read_csv(os.path.join(work_dir,'CAS_deprecated.csv'),encoding='utf-8',quotechar='$')
    ref = get_df(os.path.join(work_dir,'master_cas_number_list.parquet'))
    dep = get_df(os.path.join(work_dir,'CAS_deprecated.parquet'))
    
    # get the matches with reference numbers
    test = pd.merge(df, #[['CASNumber','tent_CAS','valid_after_cleaning']],
                    ref[['cas_number']],
                    left_on='tent_CAS',right_on='cas_number',how='left',
                    indicator=True)
    test['on_ref_list'] = np.where(test['_merge']=='both',
                                    'verified;normal','unk') 
    test['CAS_prospect'] = np.where(test['_merge']=='both',
                              test.cas_number, # if in both, save the CAS
                              '') # otherwise leave it empty
    test = test.drop('_merge',axis=1) # clean up before next merge

    # now find the deprecated CAS numbers
    test = pd.merge(test,dep,
                    left_on='tent_CAS',right_on='deprecated',how='left',
                    indicator=True)
    # A potential error is if we get an authoritative match AND a deprecated
    #   match.  Scan for that situation, alert the user, and exit
    cond1 = ~test.cas_number.isna()
    cond2 = test['_merge']=='both'
    if (cond1&cond2).sum()>0:
        print('DEPRECATED DETECTED ON AN VERIFIED CAS')
        print(test[cond1&cond2])
        sys.exit(1)
        
    # mark the deprecated and take the valid CAS as bgCAS
    test['on_ref_list'] = np.where(test['_merge']=='both',
                              'verified;from deprecated',test.on_ref_list) 
    test['CAS_prospect'] = np.where(test['_merge']=='both',
                              test.cas_replacement,test.CAS_prospect)
    test = test.drop(['_merge','cas_number'],axis=1) # clean up before next merge
    
    # mark the CAS numbers that are formally valid but without authoritative cas in ref.
    #  these may be good targets for later curating
    cond1 = test.valid_after_cleaning
    cond2 = test.on_ref_list=='unk'
    test['CAS_prospect'] = np.where(cond1&cond2,'valid_but_empty',test.tent_CAS)
    test['on_ref_list'] = np.where(cond1&cond2,'valid_but_empty',test.on_ref_list)
    test = test.drop(['deprecated',
                      'cas_replacement','tent_CAS',
                      #'ing_name',
                      'valid_after_cleaning'],axis=1) # clean up before next merge
    print(f'\nNumber of new CAS lines to curate: {len(test)}\n')
    
    # If no new lines, copy orig CAS_curated to work_dir
    if len(test)==0:
        shutil.copy(os.path.join(ref_dir,'curation_files','CAS_curated.parquet'),
                    work_dir)
    else:
        # make curation file
        # old = pd.read_csv(os.path.join(ref_dir,'curation_files','CAS_curated.csv'),quotechar='$',
        #                         encoding='utf-8')
        old = get_df(os.path.join(ref_dir,'curation_files','CAS_curated.parquet'))
        # old = old[['CASNumber','bgCAS','category',
                    # 'close_syn','comment','first_date','change_date','change_comment']]
        old['is_new'] = False    
        test['is_new'] = True
        # Now concat with the old data (DONT MERGE - otherwise old gets clobbered!)
        out = pd.concat([test,old],sort=True)
        
        # return out, len(test)   
        store_df_as_csv(out[['CASNumber','CAS_prospect','auto_status','on_ref_list',
                             'curatedCAS','categoryCAS','is_new',
                             'comment','first_date',
                             'change_date','change_comment']],
                        os.path.join(work_dir,'CAS_curated_TO_EDIT.csv'))

