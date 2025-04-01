"""Code used to assemble "FF_issues" portion of the Data Browser, including the 
FF_Flaws Index and the detailed flaw reports."""


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

import FF_issues.process_master_files as pmf

class FF_flaws_gen():

    def __init__(self, workingdf,arc_diff={},use_archive_diff=False,
                 testing_mode=False
    ):
        print(f'Starting Flaws Browser: using repository: {hndl.curr_data}')
        self.allrec = workingdf

        pobj = pmf.Process_Master_Files()
        self.flaws_master = pobj.process_obj()

        rfn = os.path.join(hndl.curr_repo_dir,'record_issues.parquet')
        self.rec_df = fh.get_df(rfn)
        # print(self.rec_df.columns)
        dfn = os.path.join(hndl.curr_repo_dir,'disclosure_issues.parquet')
        self.disc_df = fh.get_df(dfn)
        # print(self.disc_df.columns)

        self.make_all_files()
    
    def make_all_files(self):
        for i,row in self.flaws_master.iterrows():
            print(f'Working on {row.Flag_id}')
            id = row.Flag_id
            if id[0] == 'r':
                reckeys = self.rec_df[self.rec_df[row.Flag_id]].reckey.tolist()
                #print(f'{row.Flag_id}: {len(reckeys)}')       
                fh.save_df(self.allrec[self.allrec.reckey.isin(reckeys)],
                           os.path.join(hndl.sandbox_dir,'flaws.parquet'))
            elif id[0] == 'd':
                DiDs = self.disc_df[self.disc_df[id]].DisclosureId.tolist()
                gb = self.allrec[self.allrec.DisclosureId.isin(DiDs)].groupby('DisclosureId',as_index=False)\
                        [['APINumber','bgStateName','bgCountyName','bgLatitude','bgLongitude',
                          'OperatorName','bgOperatorName','date']].first()
                fh.save_df(gb,os.path.join(hndl.sandbox_dir,'flaws.parquet'))
            t = row.to_frame().T
            fh.save_df(t.reset_index(),
                       os.path.join(hndl.sandbox_dir,'flaws_meta.parquet'))

            iss_fn = f'Issue_{id}.html'
            fulloutfn = os.path.join(hndl.browser_flaws_dir,iss_fn)
            nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'flaw_report.ipynb'),
                                        output_fn=fulloutfn)
        nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'FF_flaws_index.ipynb'),
                                 output_fn = os.path.join(hndl.browser_out_dir,'FF_issues_index.html'))



    # def fix_operator_title(self,fn,operator):
    #     # also adds favicon to browser tab
    #     with open(fn,'r',encoding='utf-8') as f:
    #         alltext = f.read()
    #     alltext  = alltext.replace('<title>operator_report</title>',
    #                                f'<title>{operator}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
    #     with open(fn,'w',encoding='utf-8') as f:
    #         f.write(alltext)

    # def count_all_trues(self,df):
    #     cols = df.columns.tolist()
    #     cols.remove('DisclosureId')
    #     # the following code is needed because there will sometimes be "None" in the boolean
    #     # which can clobber the "sum" function
    #     t = df.groupby('DisclosureId',as_index=False)[cols].apply(lambda x: x[x==True].sum())

    #     # we still must correct for the disclosures that are only one record long.
    #     t = t.replace({True:1,False:0})
    #     return t
    
    # def make_all_files(self):
    #     t = self.allrec[(self.allrec.in_std_filtered)\
    #                     &(self.allrec.bgOperatorName.notna())]
    #     gb = t.groupby(['bgOperatorName','DisclosureId'],as_index=False).size()
    #     gb = gb.groupby('bgOperatorName',as_index=False).size().rename({'size':'num_disc'},axis=1)
        
    #     oplst = gb.bgOperatorName.unique().tolist()


    #     print(f'Number of operators to be processed: {len(oplst)}')
    #     for op in oplst:
    #         workdf = t[t.bgOperatorName==op].copy()
    #         workdf['location_error'] = workdf.loc_name_mismatch|\
    #                                    (workdf.loc_within_county=='NO')|\
    #                                    (workdf.loc_within_state=='NO')|\
    #                                    workdf.latlon_too_coarse
            

    #         gb = workdf.groupby('DisclosureId',as_index=False)[['date','APINumber','TotalBaseWaterVolume',
    #                                                          'bgCountyName','bgStateName','bgOperatorName',
    #                                                          'bgLatitude','bgLongitude','location_error',
    #                                                          'OperatorName','no_chem_recs','WellName',
    #                                                          'perc_proprietary']].first()
    #         gb1 = self.count_all_trues(workdf[['DisclosureId','is_on_DWSHA','is_on_CWA','is_on_prop65',
    #                                             'is_on_UVCB','is_on_diesel','is_on_PFAS_list',
    #                                             'is_proprietary']])
    #         # print(gb1.head())
    #         # gb1 = workdf.groupby('DisclosureId',as_index=False)[['is_on_DWSHA','is_on_CWA','is_on_prop65',
    #         #                                                      'is_on_UVCB','is_on_diesel','is_on_PFAS_list',
    #         #                                                      'is_proprietary']].count()
    #         gb=pd.merge(gb,gb1,on='DisclosureId',how='left')
    #         # print(gb.columns)
    #         gb.to_parquet(os.path.join(hndl.sandbox_dir,'operator.parquet'),index=False)
    #         #workdf.to_parquet(os.path.join(hndl.sandbox_dir,'operator.parquet'),index=False)
    #         print(f'** {op:<40} **  n recs: {len(workdf):>10,}')
    #         oneword = op.replace(' ','_')
    #         fulloutfn = os.path.join(hndl.browser_out_dir,'operators',f'{oneword}.html')
    #         nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'operator_report.ipynb'),
    #                                 output_fn=fulloutfn)
    #         self.fix_operator_title(fulloutfn,op)
    #     # make the Operator Index
    #     fulloutfn = os.path.join(hndl.browser_out_dir,'Open-FF_Operator_Index.html')
    #     nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'Open-FF_Operator_Index.ipynb'),
    #                             output_fn=fulloutfn)
    #     nbh.fix_nb_title(fulloutfn,'Operator Index')
        
