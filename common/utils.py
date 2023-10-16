# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 18:54:59 2023

@author: garya

Utilites to help in the maintenance of the system
"""

import sys
import os
import shutil
import pandas as pd
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

def make_upload_set_of_ext_data():
    from openFF.common.handles import ext_data, ext_data_master_list
    from openFF.common.nb_helper import make_sandbox
    from openFF.common.file_handlers import get_df
    
    make_sandbox('sandbox')
    outdir = os.path.join('sandbox','ext_file_xfer')
    if os.path.exists(outdir):
        # remove old version
        shutil.rmtree(outdir)
    try:
        os.mkdir(outdir)
    except:
        print('something wrong making the folder')
        assert 1==0
    
    df = get_df(ext_data_master_list)
    lst = df[df.inc_remote=='Yes'].filename.tolist()
    for fn in lst:
        assert fn.find(' ') == -1 ,'Filename should not have spaces!'
        shutil.copy(os.path.join(ext_data,fn),outdir)
        print(f'copying {fn}')
    
    
    
    
if __name__ == '__main__':
    make_upload_set_of_ext_data()