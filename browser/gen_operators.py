"""Code used to assemble the "operators" portion of the Data Browser, including the 
Operaotr Index and the detailed operator reports."""


import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import os, shutil
import pandas as pd
import numpy as np
import subprocess
from datetime import datetime
import openFF.common.handles as hndl 
import openFF.common.defaults as dflt
import openFF.common.file_handlers as fh
import openFF.common.text_handlers as th
import openFF.common.nb_helper as nbh

class Operator_gen():

    def __init__(self, workingdf,
                 testing_mode=False
    ):
        print(f'Starting Operator Browser: using repository: {hndl.curr_data}')
        self.allrec = workingdf
        self.workdf = self.allrec[(self.allrec.in_std_filtered)]
        self.make_all_files()
    
    def fix_operator_title(self,fn,operator):
        # also adds favicon to browser tab
        with open(fn,'r',encoding='utf-8') as f:
            alltext = f.read()
        alltext  = alltext.replace('<title>operator_report</title>',
                                   f'<title>{operator}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
        with open(fn,'w',encoding='utf-8') as f:
            f.write(alltext)

    def count_all_trues(self,df):
        cols = df.columns.tolist()
        cols.remove('DisclosureId')
        # the following code is needed because there will sometimes be "None" in the boolean
        # which can clobber the "sum" function
        t = df.groupby('DisclosureId',as_index=False)[cols].apply(lambda x: x[x==True].sum())

        # we still must correct for the disclosures that are only one record long.
        t = t.replace({True:1,False:0})
        return t
    
    def make_all_files(self):
        t = self.allrec[(self.allrec.in_std_filtered)\
                        &(self.allrec.bgOperatorName.notna())]
        gb = t.groupby(['bgOperatorName','DisclosureId'],as_index=False).size()
        gb = gb.groupby('bgOperatorName',as_index=False).size().rename({'size':'num_disc'},axis=1)
        
        oplst = gb.bgOperatorName.unique().tolist()


        print(f'Number of operators to be processed: {len(oplst)}')
        # oplst = ['ascent']
        for op in oplst:
            workdf = t[t.bgOperatorName==op].copy()
            workdf['location_error'] = workdf.loc_name_mismatch|\
                                       (workdf.loc_within_county=='NO')|\
                                       (workdf.loc_within_state=='NO')|\
                                       workdf.latlon_too_coarse
                                       
            # dupgb = workdf[workdf.dup_rec].groupby('DisclosureId',as_index=False).size().rename({'size':'num_dup_recs'},axis=1)
            
            

            gb = workdf.groupby('DisclosureId',as_index=False)[['date','APINumber','TotalBaseWaterVolume',
                                                             'bgCountyName','bgStateName','bgOperatorName',
                                                             'bgLatitude','bgLongitude','location_error',
                                                             'OperatorName','no_chem_recs','WellName',
                                                             'perc_proprietary']].first()
            gb1 = self.count_all_trues(workdf[['DisclosureId','is_on_DWSHA','is_on_CWA','is_on_prop65',
                                                'is_on_UVCB','is_on_diesel','is_on_PFAS_list',
                                                'is_proprietary']])
            # print(gb1.head())
            # gb1 = workdf.groupby('DisclosureId',as_index=False)[['is_on_DWSHA','is_on_CWA','is_on_prop65',
            #                                                      'is_on_UVCB','is_on_diesel','is_on_PFAS_list',
            #                                                      'is_proprietary']].count()
            gb=pd.merge(gb,gb1,on='DisclosureId',how='left')
            # gb = gb.merge(dupgb,on='DisclosureId',how='left')
            # print(gb.columns)
            gb.to_parquet(os.path.join(hndl.sandbox_dir,'operator.parquet'),index=False)
            # make unfiltered out file too
            dupdf = self.allrec[self.allrec.bgOperatorName==op][['bgOperatorName',
                                                                 'OperatorName','r_flags',
                                                                 'date','dup_rec',
                                                                 'mass','APINumber',
                                                                 'bgStateName','bgCountyName',
                                                                 'DisclosureId']].copy()
            dupdf.to_parquet(os.path.join(hndl.sandbox_dir,'operator_unfilt.parquet'),index=False)
            
            print(f'** {op:<40} **  n recs: {len(workdf):>10,}')
            oneword = op.replace(' ','_')
            fulloutfn = os.path.join(hndl.browser_out_dir,'operators',f'{oneword}.html')
            nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'operator_report.ipynb'),
                                    output_fn=fulloutfn)
            self.fix_operator_title(fulloutfn,op)
        # make the Operator Index
        fulloutfn = os.path.join(hndl.browser_out_dir,'Open-FF_Operator_Index.html')
        nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'Open-FF_Operator_Index.ipynb'),
                                output_fn=fulloutfn)
        nbh.fix_nb_title(fulloutfn,'Operator Index')
        
