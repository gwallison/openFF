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
import requests
import urllib
import openFF.common.handles as hndl

# this is the list of FF fields that should be treated as text columns in CSV file
lst_str_cols = ['APINumber','bgCAS','api10','IngredientName','CASNumber','test',
                'Supplier','OperatorName','TradeName','Purpose',
                'rawName','cleanName','xlateName',  # for companyXlate...
                'curatedCAS', # in CAS and casing curation files
                ]


#### Interacting with files in local situations

def store_df_as_csv(df,fn,encoding='utf-8',str_lst = lst_str_cols):
    # saves files in standard encoding, and single quote added in front of every value in 
    # columns in str_lst, to make them be interpreted as strings by excel (a "literal" value)
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
    elif tup[1]=='.csv':
        store_df_as_csv(df,fn)
    elif tup[1]=='.parquet':
        df.to_parquet(fn)
    else:
        print(f'{fn}: Extention <{tup[1]}> not valid for "save_df"')
        assert 1==0
    
def get_df(fn,cols=None):
    tup = os.path.splitext(fn)
    if tup[1]=='': # files without ext are read as parquet
        return pd.read_parquet(fn+'.parquet',columns=cols)
    elif tup[1]=='.csv':
        return get_csv(fn)
    elif tup[1]=='.parquet':
        return pd.read_parquet(fn,columns=cols)
    else:
        print(f'{fn}: Extention <{tup[1]}> not valid for "get_df"')
        assert 1==0

def get_table(repo_dir=hndl.repo_dir, repo_name=hndl.repo_name,tname='disclosures',cols=None):
    """ Used to pull in repo's pickled tables; works with local only!"""
    return pd.read_parquet(os.path.join(repo_dir,repo_name,'pickles',tname+'.parquet'),
                           columns=cols)

def get_repo_tables(pkl_dir=hndl.curr_repo_pkl_dir):
    tables = {}
    print(f'Pulling repo tables from: {pkl_dir}')
    flst = os.listdir(pkl_dir)
    for fn in flst:
        if fn[-8:] == '.parquet':
            name = fn[:-8]
            tables[name] = pd.read_parquet(os.path.join(pkl_dir,fn))
    return tables
    
#####################  Interacting with remote files ##############

def get_size_of_url_file(url):
    response = requests.head(url,allow_redirects=True)
    return int(response.headers['Content-Length'])

def fetch_file_from_url(url,fn):
    # get file from url, save it at fn
    sz = get_size_of_url_file(url)
    if sz>100000000: # alert that a large file download is in progress
        print('Fetching file, please be patient...')
    urllib.request.urlretrieve(url,fn)

def get_df_from_url(df_url,df_fn,force_freshen=False,inp_format='parquet'):
    # get file from url, checking first it it already exists, then convert to dataframe
    if force_freshen:
        fetch_file_from_url(df_url,df_fn);
    else:
        if os.path.isfile(df_fn):
            print('File already downloaded')
        else:    
            fetch_file_from_url(df_url,df_fn);
            
    print('Creating full dataframe...')
    assert inp_format=='parquet'
    return pd.read_parquet(df_fn)

#### get specific data sets

def get_cas_list():
    """returns list of all bgCAS numbers in current repository"""
    # repoloc = r"C:\MyDocs\OpenFF\data\repos/"+repo_name
    pkl = pd.read_parquet(os.path.join(hndl.curr_repo_pkl_dir,'bgCAS.parquet'))
    #pkl.to_csv('./tmp/bgCAS.csv')
    lst = pkl.bgCAS.str.strip().unique().tolist()
    for cas in lst:
        if (cas[-1]==' ')|(cas[0]==' '):
            print(f'CAS list error: <<{cas}>>')
    return lst


def get_comptox_df():
    """returns df of bgCAS with DTXSID ids as well as bgCAS"""
    # repoloc = r"C:\MyDocs\OpenFF\data\repos/"+repo_name
    pkl = pd.read_parquet(os.path.join(hndl.curr_repo_pkl_dir,'bgCAS.parquet'))
    # pkl = pd.read_parquet(os.path.join(repoloc,'pickles/bgCAS.parquet'))
    #print(f'Len dtxsid: {pkl.DTXSID.notna().sum()}, {len(pkl)}')
    #print(f'{pkl[["bgCAS","DTXSID"]].head(10)}')
    print('CAS without DTXSID:')
    print(pkl[pkl.DTXSID.isna()].bgCAS.tolist())
    return pkl[pkl.DTXSID.notna()][['bgCAS','DTXSID']]

##### external file dictionary handler
def get_ext_master_dic(url="https://storage.googleapis.com/open-ff-common/ext_data/ext_data_master_list.csv"):
    # pulling from main cloud source
    df = get_df(url)
    out = {}
    for i,row in df[df.inc_remote=='Yes'].iterrows():
        out[row.ref_handle] = row.filename
        
    return out

def ext_fn(ext_dir="https://storage.googleapis.com/open-ff-common/ext_data/",
           handle='state_latlon'):
    masterfn = 'ext_data_master_list.csv'
    if ext_dir[:4] == 'http': # through urls
        ext_dict = get_ext_master_dic(ext_dir+masterfn)
        return ext_dir+ext_dict[handle]
    # through files
    ext_dict = get_ext_master_dic(os.path.join(ext_dir,masterfn))
    return os.path.join(ext_dir,ext_dict[handle])