import pandas as pd
import numpy as np
import requests
import urllib
import os

#################### general utilities  ########################
def is_remote():
    # check if we are not working on a known local machine
    import platform
    locals = ['Dell_2023_Gary']
    if platform.node() in locals:
        return False
    return True


#####################  Interacting with files, remote and local ##############
def make_sandbox(name='sandbox'):
    # make output location
    tmp_dir = name
    try:
        os.mkdir(name)
    except:
        print(f'{name} already exists')
        
def get_size_of_url_file(url):
    response = requests.head(url,allow_redirects=True)
    return int(response.headers['Content-Length'])

def fetch_file(url,fn):
    # get file from url, save it at fn
    sz = get_size_of_url_file(url)
    if sz>100000000:
        print('Fetching file, please be patient...')
    urllib.request.urlretrieve(url,fn)

def get_df_from_file(df_url,df_fn,force_freshen=False,inp_format='parquet'):
    # get file from url, checking first it it already exists, then convert to dataframe
    if force_freshen:
        fetch_file(df_url,df_fn);
    else:
        if os.path.isfile(df_fn):
            print('File already downloaded')
        else:    
            fetch_file(df_url,df_fn);
            
    print('Creating full dataframe...')
    assert inp_format=='parquet'
    return pd.read_parquet(df_fn)

def show_done(txt='Completed'):
    print(txt)
