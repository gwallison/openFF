import pandas as pd
import numpy as np
import os
import requests 
import urllib

out_dir = 'sandbox'

print('running Data_set_customizer_support')
import common.nb_opener as nbo

nbo.make_sandbox(out_dir)


df_url = "https://storage.googleapis.com/open-ff-common/repos/current_repo/full_df.parquet"
df_fn = os.path.join(out_dir,'full_df.parquet')

response = requests.head(df_url,  # Example file 
    allow_redirects=True
)
print(f"Full size on remote disk: {int(response.headers['Content-Length']):,} bytes") 

if os.path.isfile(df_fn):
    print('Open-FF file already downloaded')
else:    
    print('Fetching it now, please be patient...')
    urllib.request.urlretrieve(df_url,df_fn);

print('Creating full dataframe...')
df = pd.read_parquet(df_fn)
print(f'The full Open-FF data frame shape (rows,cols): {df.shape}')