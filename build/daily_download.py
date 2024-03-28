
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:43:54 2019

@author: Gary

This script is used to download a new raw set, and save it. Not much else.

This script runs independently of the main build_database set.  It is designed 
to run autonomously, can be executed from a crontab command.  This version is for
a Linux machine.

  
"""
#import pandas as pd
import requests
from datetime import datetime


today = datetime.today()
if today.weekday() in [1,3,5]: # Monday= 0, Sunday = 6
    archive_file=True
else:
    archive_file=False

# define    
data_dir = '/home/allisong/OpenFF/data/' 
archive = data_dir+'daily/'
afile = archive+f'ff_archive_{today.strftime("%Y-%m-%d")}.zip'

st = datetime.now() # start timer
    
# get and save files

# url = 'http://fracfocusdata.org/digitaldownload/fracfocuscsv.zip'  # old address
url = 'https://www.fracfocusdata.org/digitaldownload/FracFocusCSV.zip' # new as of 2/2024
print(f'Downloading data from {url}')
r = requests.get(url, allow_redirects=True,timeout=20.0)
open(afile, 'wb').write(r.content)
    
endit = datetime.now()
print(f'\nWhole process completed in {endit-st}')

