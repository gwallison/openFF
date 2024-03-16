# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 22:05:13 2021

@author: Gary
"""
import subprocess
import shutil
import datetime
import pandas as pd
import numpy as np

import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

from openFF.common.nb_helper import add_favicon

# update_fn = 'c:/MyDocs/OpenFF/data/transformed/upload_dates.csv'

today_str = '2024-03-16' # used as file name when finalizing and uploading
make_final = True
today = datetime.date.today()
nb_fn = 'browser/notebooks/Recent_Disclosures.ipynb'
nb_html = f'{nb_fn[:-5]}html'

# def add_favicon(fn):
#     # also adds favicon to browser tab
#     with open(fn,'r',encoding='utf-8') as f:
#         alltext = f.read()
#     alltext  = alltext.replace('</title>',
#                                '</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
#     with open(fn,'w',encoding='utf-8') as f:
#         f.write(alltext)


s= f"jupyter nbconvert --no-input --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute {nb_fn} --to=html "
print(subprocess.run(s,capture_output=False))
add_favicon(fn=nb_html)

if make_final:
    print(f'Ready to make a final upload using <{today_str}> as file name.')
    c = input('ARE YOU SURE YOU WANT TO GENERATE A WEEKLY FINAL UPLOAD? [y/N] > ')
    if c == 'y':
        print('copying result to Google Drive webshare')
        shutil.copyfile(nb_html,
                        f'g:/My Drive/webshare/weekly_reports/{today_str}.html')
        
    
        # print('updating date file')    
        # updates = pd.read_csv(update_fn)
        # updates.weekly_report = np.where(updates.weekly_report.isna(),
        #                                  today,
        #                                  updates.weekly_report)
        # updates.to_csv(update_fn,index=False)
    else:
        print('... not continuing with FINAL')