
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

    def __init__(self,workingdf):
        self.df = workingdf
        print(f'Compiling Misc Notebooks using repository: {hndl.curr_data}')
        # the following list is in tuples of (file basenane,page title)
        self.fulllist = [('Open-FF_Catalog','Data Browser'),
                        ('Open-FF_Scope_and_Aggregate_Stats','Big Picture Analysis'),
                        ('Ohio_Drilling_Chemicals','Ohio Drilling Chemicals'),
                        #('Open-FF_Auxillary_Data','Auxillary Data'),
                        ('Open-FF_CASNumber_and_IngredientName','CASRN & IngredientName pairs'),
                        ('Open-FF_Company_Names','Company Name Table'),
                        ('Open-FF_Data_Dictionary','Data Dictionary'),
                        ('Open-FF_Synonyms','Chemical Name Synonyms'),
                        ('Open-FF_TradeNames','Trade Names and Composition Data'),
                        ('Short_description_of_Open-FF','Short description of Open-FF'),
                        #('FracFocus_Holes','Holes in FracFocus'),
                        ('Make_blog_images','Make data-dependent images'),
                        ('sand_dominance_summary','Sand dominance summary'),
                        ('Open-FF_Op_Parents','Parents of operators'),
                        # ('Colorado_disclosures','CO-ECMC disclosures')
                        ]
        self.make_all_nb()

    def make_all_nb(self):
        for tup in self.fulllist:
            print(f'Compiling notebook: {tup[0]}')
            nb_fn = os.path.join(hndl.browser_nb_dir,tup[0]+'.ipynb')
            outfn = os.path.join(hndl.browser_out_dir,tup[0]+'.html')
            nbh.make_notebook_output(nb_fn=nb_fn,output_fn=outfn)
            nbh.fix_nb_title(outfn,tup[1])

    
