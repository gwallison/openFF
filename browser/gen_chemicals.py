"""Code used to assemble the chemicals portion of the Data Browser, including the 
Chemical Index and the detailed chemical reports."""


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
# import openFF.common.chem_info_tools as cit


today = datetime.today()


class Chem_gen():

    def __init__(self, workingdf,arc_diff=None,use_archive_diff=False,
                 caslist=[], # for testing; if not [], will only work on cas in list)
                 #testing_mode=False
    ):
        print(f'Starting Chem Browser: using repository: {hndl.curr_data}')

        self.caslist = caslist
        self.html_fn = os.path.join(hndl.browser_nb_dir,'chemical_report.html')
        self.no_data_html_fn = os.path.join(hndl.browser_nb_dir,'chemical_report_no_data.html')
        self.allrec = workingdf

        # # Next few lines are for testing mode; runs much faster!
        # if testing_mode:
        #     self.allrec[self.allrec.bgCAS.isin(['50-00-0'])].to_parquet('tmpdf.parquet')
        #     self.allrec = pd.read_parquet('tmpdf.parquet')

        self.allrec['TradeName_trunc'] = np.where(self.allrec.TradeName.str.len()>30,
                                                  self.allrec.TradeName.str[:30]+'...',
                                                  self.allrec.TradeName)
        self.allrec['Purp_trunc'] = np.where(self.allrec.Purpose.str.len()>30,
                                                  self.allrec.Purpose.str[:30]+'...',
                                                  self.allrec.Purpose)

        # if using archive_diff, filter self.allrec, self.alldisc
        if use_archive_diff:
            if not arc_diff:
                arc_diff = hndl.archive_diff_pkl
            import pickle
            with open(arc_diff,'rb') as f:
                arc_diff_dict = pickle.load(f)
            self.allrec['casing'] = list(zip(self.allrec['CASNumber'],
                                             self.allrec['IngredientName']))
            self.update_bgCAS_list = self.allrec[self.allrec.casing.isin(arc_diff_dict['casing'])].bgCAS.unique().tolist()
        else:
            self.update_bgCAS_list = self.allrec.bgCAS.unique().tolist()


        # some global stats for chem_reports
        w_chem = ~(self.allrec.no_chem_recs)
        filtered = self.allrec.in_std_filtered
        self.num_events = len(self.allrec.DisclosureId.unique())
        self.num_events_wo_FFV1 = len(self.allrec[w_chem].DisclosureId.unique())
        self.num_events_fil = len(self.allrec[filtered].DisclosureId.unique())
        self.num_events_fil_wo_FFV1 = len(self.allrec[filtered & w_chem].DisclosureId.unique())
        # self.chem_report_fn = os.path.join(browser_nb_dir,'chemical_report.ipynb')
        # self.chem_index_fn = os.path.join(browser_nb_dir,'Chemical_Index.ipynb')
        self.make_chem_list()

    def save_page(self,webtxt='', fn='index.html'):
        with open(os.path.join(self.outdir,fn),'w') as f:
            f.write(webtxt)

    def save_global_vals(self,num_UploadKey=None,cas='?',
                        IngredientName='?',eh_IngredientName='?'):
        """put numbers used by all analyses into a file for access
        within Jupyter scripts."""
        vname = ['tot_num_disc','tot_num_disc_less_FFV1',
                'tot_num_disc_fil','tot_num_disc_fil_less_FFV1',
                'data_date','today','target_cas']
        vals = [self.num_events,self.num_events_wo_FFV1,
                self.num_events_fil,self.num_events_fil_wo_FFV1,
                hndl.bulkdata_date,today,cas]
        pd.DataFrame({'varname':vname,'value':vals}).to_csv(hndl.ref_fn,
                                                            index=False)
    def make_chem_list(self):
        import math
        t = self.allrec # just a handle
        if self.caslist != []: # then do all
            t = t[t.bgCAS.isin(self.caslist)]
        #print(len(t),self.caslist)
        gb = t.groupby('bgCAS',as_index=False)[['bgIngredientName','epa_pref_name',
                                                'IngredientName','iupac_name']].first()
        # self.make_bgCAS_name_df(gb)
        # gb = gb[:4]  #limit length for development
        lst = gb.bgCAS.unique().tolist()
        lst.sort()
        # self.make_dir_structure(lst)
        
        for i, row in gb.iterrows():
            #if i>15:  # control the overall list
            #    continue # skip the rest
            chem = row.bgCAS
            if not chem in self.update_bgCAS_list:
                print(f'{i}: ** {chem:>13} **  not updated')
                continue
            ing = row.epa_pref_name
            if ing == '':
                ing= row.bgIngredientName
            chemdir = os.path.join(hndl.browser_out_dir,chem)
            shutil.rmtree(chemdir,ignore_errors=True)
            os.mkdir(chemdir)

            # self.initialize_dir(os.path.join(self.outdir,chem))

            #ingred = row.bgIngredientName
            self.save_global_vals(self.num_events,chem,
                                row.bgIngredientName)
            
            tt = self.allrec[self.allrec.bgCAS==chem].copy()
            mx = tt.mass.max()
            an_fn = f'analysis_{chem}.html'
            fulloutfn = os.path.join(hndl.browser_out_dir,chem,an_fn)
            
            # NO DATA IN FILTERED SET - Reroute
            if tt.in_std_filtered.sum()==0:
                tt.to_parquet(os.path.join(hndl.sandbox_dir,'data.parquet'),index=False)
                # tt.to_csv('work/data.csv',index=False)
                # tt.to_csv(os.path.join(self.outdir,chem,'data.zip'),index=False,
                        # compression={'method': 'zip', 'archive_name': 'data.csv'})
                # self.make_no_data_output()
                nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'chemical_report_no_data.ipynb'),
                                    output_fn=fulloutfn)
                self.fix_no_data_html(chem,ing,0,mx,fulloutfn)
                print(f'{i}: ** {chem:>13} **  n recs: {len(tt):>7,};  max mass: {mx:>10,} - NO FILTERED DATA')
                continue             
            # report with data
            print(f'{i}: ** {chem:>13} **  n recs: {len(tt):>7,};  max mass: {mx:>10,}')               
            # if len(tt)>0:
            tt['map_link'] = tt.apply(lambda x: th.getMapLink(x),axis=1)

            # save data to file for later notebook access
            tt.to_parquet(os.path.join(hndl.sandbox_dir,'data.parquet'),index=False)
            
            nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'chemical_report.ipynb'),
                                    output_fn=fulloutfn)
            self.fix_chem_html(chem,ing,tt.in_std_filtered.sum(),mx,fulloutfn)

        fulloutfn = os.path.join(hndl.browser_out_dir,'Open-FF_Chemicals.html')
        nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'Open-FF_Chemicals.ipynb'),
                                output_fn=fulloutfn)
        nbh.fix_nb_title(fulloutfn,'Chemical Index')

    def fix_chem_html(self,cas,ing,num_recs,mxmass,fn):
        # also adds favicon to browser tab
        with open(fn,'r',encoding='utf-8') as f:
            alltext = f.read()
        alltext  = alltext.replace('<title>chemical_report</title>',
                                f'<title>{cas}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
        des = f"""{ing} (CASRN {cas}): Analysis of FracFocus records of this material including mass, when
calculable, locations, and companies and trade-named products involved when provided."""
        if num_recs>0:
            des += f" Currently {num_recs:,} record(s) have been reported."""
        else:
            des += "  While some records exist for this chemical, no records are available for this chemical in the standard filtered set."
        if mxmass>0:
            des += f""" The maximum calculated mass reported in a single fracking event is approx. {mxmass:,} pounds."""
        if not cas[0].isnumeric():
            des = f"""Analysis of FracFocus records classified as <{cas}> (not resolvable to a specific CASRN)."""
        des += " The analyses in this script-generated report are performed by the independent project, Open-FF."
        
        alltext = alltext.replace('<head>',
                                f'<head>\n<meta name="description" content="{des}">\n')
        with open(fn,'w',encoding='utf-8') as f:
            f.write(alltext)
            
    def fix_no_data_html(self,cas,ing,num_recs,mxmass,fn):
        # also adds favicon to browser tab
        with open(fn,'r',encoding='utf-8') as f:
            alltext = f.read()
        alltext  = alltext.replace('<title>chemical_report</title>',
                                f'<title>{cas}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
        des = f"""{ing} (CASRN {cas}): Analysis of FracFocus records of this material including mass, when
calculable, locations, and companies and trade-named products involved when provided."""
        if num_recs>0:
            des += f" Currently {num_recs:,} record(s) have been reported."""
        else:
            des += "  While some records exist for this chemical, no records are available for this chemical in the standard filtered set."
        if mxmass>0:
            des += f""" The maximum calculated mass reported in a single fracking event is approx. {mxmass:,} pounds."""
        if not cas[0].isnumeric():
            des = f"""Analysis of FracFocus records classified as <{cas}> (not resolvable to a specific CASRN)."""
        des += " The analyses in this script-generated report are performed by the independent project, Open-FF."
        
        alltext = alltext.replace('<head>',
                                f'<head>\n<meta name="description" content="{des}">\n')
        with open(fn,'w',encoding='utf-8') as f:
            f.write(alltext)

 