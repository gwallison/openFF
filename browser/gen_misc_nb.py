
import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import os, shutil
import pandas as pd
import numpy as np
# import subprocess
from datetime import datetime
import openFF.common.handles as hndl 
import openFF.common.defaults as dflt
import openFF.common.file_handlers as fh
import openFF.common.text_handlers as th
import openFF.common.nb_helper as nbh


today = datetime.today()


class MiscNbGen():

    def __init__(self, 
                 nblist=[], # for testing; if not [], will only work on notebooks in list)
    ):
        print(f'Compiling Misc Notebooks using repository: {hndl.curr_data}')
        self.fulllist = ['Open-FF_Scope_and_Aggregate_Stats']
        self.caslist = caslist
        self.html_fn = os.path.join(hndl.browser_nb_dir,'chemical_report.html')
        self.no_data_html_fn = os.path.join(hndl.browser_nb_dir,'chemical_report_no_data.html')
        self.allrec = fh.get_df(hndl.curr_data,cols=dflt.filt_cols)
