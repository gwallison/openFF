"""Code used to assemble the "states" portion of the Data Browser, including the 
State Index and the detailed county reports."""


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

class State_gen():

    def __init__(self, workingdf,
                 testing_mode=False
    ):
        print(f'Starting State Browser: using repository: {hndl.curr_data}')
        self.allrec = workingdf
        self.workdf = self.allrec[(self.allrec.in_std_filtered)\
                                   &(self.allrec.bgStateName.notna())\
                                   &(self.allrec.loc_within_state=='YES')]
        self.state_fn = './work/state_report.html'
        self.county_fn = './work/county_report.html'
        
        # make files that FracTracker will use to link to state and county pages
        self.state_FT_index_fn = os.path.join(hndl.browser_out_dir,'state_link_index.parquet')
        self.county_FT_index_fn = os.path.join(hndl.browser_out_dir,'county_link_index.parquet')


        # Next few lines are for testing mode; runs much faster!
        # if testing_mode:
        #     self.allrec[self.allrec.bgStateName.isin(['ohio'])].to_parquet('tmpdf.parquet')
        #     self.allrec = pd.read_parquet('tmpdf.parquet')

        self.make_all_files()
    
    def fix_state_title(self,fn,state):
        # also adds favicon to browser tab
        with open(fn,'r',encoding='utf-8') as f:
            alltext = f.read()
        alltext  = alltext.replace('<title>state_report</title>',
                                   f'<title>{state.title()}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
        with open(fn,'w',encoding='utf-8') as f:
            f.write(alltext)

    def fix_county_title(self,fn,cnty_state_name):
        # also adds favicon to browser tab
        with open(fn,'r',encoding='utf-8') as f:
            alltext = f.read()
        alltext  = alltext.replace('<title>county_report</title>',
                                   f'<title>{cnty_state_name}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
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
        statelst = self.workdf.bgStateName.unique().tolist()
        
        ##########
        # statelst = ['colorado']
        ##########
        
        # first create state dirs in "states" browser_out dir, if needed
        try:
            root = hndl.browser_states_dir
            for state in statelst:
                state_lab = state.replace(' ','_')
                os.mkdir(os.path.join(root,state_lab))
        except:
            print('Adding individual states to states dir not needed')
            
        stlst = []
        ctlst = []
        fnlst = []
        
        for state in statelst:
            print(f'----------{state}------------')
            workdf = self.workdf[self.workdf.bgStateName==state][['date','bgStateName','bgCountyName',
                                              'DisclosureId','OperatorName','WellName',
                                              'TotalBaseWaterVolume',
                                              'bgCAS', 'is_valid_cas','perc_proprietary',
                                              'APINumber', 'bgOperatorName',
                                              'bgLatitude','bgLongitude','no_chem_recs',
                                              'is_on_DWSHA','is_on_CWA',
                                              'is_on_PFAS_list',
                                              "loc_name_mismatch",
                                              "loc_within_county", 
                                              "loc_within_state",
                                              'latlon_too_coarse',
                                              'ws_perc_total',
                                              'perc_pw','perc_gw_high_TDS','perc_gw_low_TDS',
                                              'perc_sw_high_TDS','perc_sw_low_TDS',
                                              'perc_other_high_TDS','perc_other_low_TDS']].copy()
            workdf['location_error'] = workdf.loc_name_mismatch|\
                                       (workdf.loc_within_county=='NO')|\
                                       (workdf.loc_within_state=='NO')|\
                                       workdf.latlon_too_coarse
            #workdf['is_proprietary'] = workdf.bgCAS=='proprietary'
            gb = workdf.groupby('DisclosureId',as_index=False)[['date','APINumber','TotalBaseWaterVolume',
                                                                'bgCountyName','bgStateName','WellName',
                                                                'bgLatitude','bgLongitude','location_error',
                                                                'OperatorName','bgOperatorName',
                                                                'perc_proprietary',
                                                                'no_chem_recs',
                                                                'ws_perc_total',
                                                                'perc_pw','perc_gw_high_TDS','perc_gw_low_TDS',
                                                                'perc_sw_high_TDS','perc_sw_low_TDS',
                                                                'perc_other_high_TDS','perc_other_low_TDS']].first()
            gb1 = self.count_all_trues(workdf[['DisclosureId','is_on_DWSHA','is_on_CWA',
                                                              'is_on_PFAS_list']])
            # gb1 = workdf.groupby('DisclosureId',as_index=False)[['is_on_DWSHA','is_on_CWA',
            #                                                   'is_on_PFAS_list']].count()
            gb=pd.merge(gb,gb1,on='DisclosureId',how='left')
            # gb.to_csv('./tmp/gb.csv')
            #print(gb.columns)
            # tmpfn = './work/state.csv'
            # print(gb[gb.is_on_DWSHA==False][['APINumber','date','is_on_CWA']])
            gb.to_parquet(os.path.join(hndl.sandbox_dir,'state.parquet'),index=False)
            # fn = os.path.join(self.statesdir,state.replace(' ','_')+'_df.zip')
            # with zipfile.ZipFile(fn,'w') as z:
            #     z.write(tmpfn,compress_type=zipfile.ZIP_DEFLATED)

            # workdf.to_csv('work/state.csv',index=False)
            
            # make unfiltered out file too
            dupdf = self.allrec[self.allrec.bgStateName==state][['bgOperatorName',
                                                                 'OperatorName',
                                                                 'date','dup_rec',
                                                                 'mass','APINumber',
                                                                 'bgStateName','bgCountyName',
                                                                 'DisclosureId']].copy()
            dupdf.to_parquet(os.path.join(hndl.sandbox_dir,'state_unfilt.parquet'),index=False)
 
            # for county in workdf.bgCountyName.unique().tolist():
            #     print(f'  -{county}')
            #     cnty_state_name = county.lower().replace(' ','_')+'-'+state.lower().replace(' ','_')
            #     fn = os.path.join(hndl.browser_states_dir,cnty_state_name+'.html')
            #     gb = workdf[workdf.bgCountyName==county].groupby('DisclosureId',as_index=False)[['date','APINumber','TotalBaseWaterVolume',
            #                                                                                   'bgCountyName','bgStateName','WellName',
            #                                                                                   'bgLatitude','bgLongitude',
            #                                                                                   'OperatorName','no_chem_recs']].first()
            #     gb1 = self.count_all_trues(workdf[workdf.bgCountyName==county][['DisclosureId','is_on_DWSHA',
            #                                                                     'is_on_CWA','is_on_PFAS_list']])
            #     # gb1 = workdf[workdf.bgCountyName==county].groupby('DisclosureId',as_index=False)[['is_on_DWSHA','is_on_CWA',
            #     #                                                                                 'is_on_PFAS_list']].count()
            #     gb=pd.merge(gb,gb1,on='DisclosureId',how='left')
            #     gb['TBWV'] = gb.TotalBaseWaterVolume.map(lambda x: th.round_sig(x,3,guarantee_str='??')) + ' gallons'
            #     # gb.APINumber = gb.APINumber.map(lambda x: self.text_APINumber(x))
            #     gb['year'] = gb.date.astype('str')
            #     gb['has_chem'] = np.where(gb.no_chem_recs,'No','Yes')
                                                                                               
            #     stlst.append(state)
            #     ctlst.append(county)
            #     fnlst.append(cnty_state_name+'.html')  # used to make FT link table
            #     gb.to_parquet(os.path.join(hndl.sandbox_dir,'county.parquet'),index=False)
            #     # gb.to_csv('./work/county.csv')
            #     # self.make_county_output()

            #     nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'county_report.ipynb'),
            #                         output_fn=fn)
            #     self.fix_county_title(fn,cnty_state_name)

            #     # cn_fn = f'{cnty_state_name}.html'
            #     # shutil.copyfile(self.county_fn,
            #     #                 os.path.join(self.outdir,'states',cn_fn))
                
            print(f'** {state.title():<16} **  n recs: {len(workdf):>10,}')
            fulloutfn = os.path.join(hndl.browser_out_dir,'states',f'{state}.html')
            nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'state_report.ipynb'),
                                    output_fn=fulloutfn)
            self.fix_state_title(fulloutfn,state)
        #  pd.DataFrame({'state':stlst,'county':ctlst})\
        #      .to_csv(os.path.join(self.outdir,'states/state_county_df.csv'))

        # make the State Index
        fulloutfn = os.path.join(hndl.browser_out_dir,'Open-FF_States_and_Counties.html')
        nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'Open-FF_States_and_Counties.ipynb'),
                                output_fn=fulloutfn)
        nbh.fix_nb_title(fulloutfn,'State Index')
        
        # now make tables for FracTracker links
        # clinkdf = pd.DataFrame({'state':stlst, 'county':ctlst,'cntyfn':fnlst})
        # clinkdf['county_page_link'] = hndl.browser_root+'state/'+clinkdf.cntyfn
        # clinkdf.to_parquet(self.county_FT_index_fn)
        # stset = list(set(stlst))
        # slinkdf = pd.DataFrame({'state':stset})
        # # slinkdf['state_page_link'] = hndl.browser_root+'state/'+slinkdf.state+'.html'
        # slinkdf['statename'] = slinkdf.state.str.replace(' ','-')
        # slinkdf['state_page_link'] = f'https://open-ff.org/{slinkdf.statename}-fracfocus/'
        # slinkdf.to_parquet(self.state_FT_index_fn)
        
             