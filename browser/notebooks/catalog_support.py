"""catalog_support.py

routines used throughout creating the catalog, but specific to just the catalog.
In general, it is loaded and executed in every catalog notebook
"""
import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import pandas as pd
import numpy as np
import datetime
import time
import sys
import os
from IPython.display import Markdown as md
from IPython.display import display, HTML

# many of the notebooks use itables for user interaction
from itables import init_notebook_mode
init_notebook_mode(all_interactive=True)
from itables import show as iShow
import itables.options as opt
opt.classes="display compact cell-border"
opt.maxBytes = 0


import openFF.common.nb_helper as nbh
import openFF.common.handles as hndl
import openFF.common.file_handlers as fh
import openFF.common.text_handlers as th
import openFF.common.mapping as mapping

import warnings
warnings.filterwarnings('ignore')

# bulkdata_date = 'December 19, 2023'
# repo_name = 'openFF_data_2023_12_19'

# data_source = 'bulk'  # can be 'bulk', 'FFV1_scrape' or 'SkyTruth'
#                                     # or 'NM_scrape_2022_05'

# cat_creation_date = datetime.datetime.now()
# extData_loc = 'c:/MyDocs/OpenFF/data/external_refs/'
# transformed_loc = 'c:/MyDocs/OpenFF/data/transformed/'
# pic_dir = r"C:\MyDocs\OpenFF\src\openFF-catalog\pic_dir"

def showHeader(name,line2='',subt='',imglnk='',use_remote=False):
    display(HTML(nbh.get_common_header(name,line2=line2,subtitle=subt,imagelink=imglnk,
                                   repo_name=hndl.repo_name,cat_creation_date=hndl.cat_creation_date,
                                           link_up_level=2,use_remote=use_remote)))
