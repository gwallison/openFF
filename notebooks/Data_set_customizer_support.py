import pandas as pd
import numpy as np
import os
import requests 
import urllib

# handles to use in notebook
out_dir = 'sandbox'
df_url = "https://storage.googleapis.com/open-ff-common/repos/current_repo/full_df.parquet"
df_fn = os.path.join(out_dir,'full_df.parquet')

from openFF.common.nb_helper import make_sandbox, get_df_from_file, show_done

make_sandbox(out_dir)
df = get_df_from_file(df_url,df_fn)
show_done()

# if os.path.isfile(df_fn):
#     print('Open-FF file already downloaded')
# else:    
#     print('Fetching it now, please be patient...')
#     urllib.request.urlretrieve(df_url,df_fn);

# print('Creating full dataframe...')
# df = pd.read_parquet(df_fn)
# print(f'The full Open-FF data frame shape (rows,cols): {df.shape}')

# states
import ipywidgets as widgets
def prep_states():
    st_lst = df.bgStateName.unique().tolist()
    st_lst.sort()
    st_lst.insert(0,'All states')
    states = widgets.SelectMultiple(
                    options=st_lst,
                    value=['All states'],
                    #rows=10,
                    description='Select State(s)',
                    disabled=False
                )
    show_done()
    return states

def show_inc_chem_checkbox():
    include_chem = widgets.Checkbox(
                        value=True,
                        description='Include chemical data',
                        disabled=False,
                        indent=True
                    )
    show_done()
    return include_chem