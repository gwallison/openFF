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

    def __init__(self, 
                 caslist=[], # for testing; if not [], will only work on cas in list)
    ):
        print(f'Starting Chem Browser: using repository: {hndl.curr_data}')
        self.caslist = caslist
        self.html_fn = os.path.join(hndl.browser_nb_dir,'chemical_report.html')
        self.no_data_html_fn = os.path.join(hndl.browser_nb_dir,'chemical_report_no_data.html')
        self.allrec = fh.get_df(hndl.curr_data,cols=dflt.filt_cols)
        # self.allrec[self.allrec.bgCAS.isin(['50-00-0'])].to_parquet('tmpdf.parquet')
        # self.allrec = pd.read_parquet('tmpdf.parquet')
        self.allrec['TradeName_trunc'] = np.where(self.allrec.TradeName.str.len()>30,
                                                  self.allrec.TradeName.str[:30]+'...',
                                                  self.allrec.TradeName)
        self.allrec['Purp_trunc'] = np.where(self.allrec.Purpose.str.len()>30,
                                                  self.allrec.Purpose.str[:30]+'...',
                                                  self.allrec.Purpose)
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
    # def make_chem_report_output(self,nb_fn,output_fn, basic_output=False):
    #     res = os.path.split(output_fn)
    #     out_dir = res[0]
    #     out_fn = res[1] 
    #     assert out_fn[-5:]=='.html', f'Expecting .html ext on {output_fn}'
    #     b_text = ''
    #     if basic_output:
    #         b_text = ' --template=basic '
    #     s= f'jupyter nbconvert --no-input {b_text}--ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute {nb_fn} --to=html --output={out_fn[:-5]} --output-dir={out_dir}'
    #     subprocess.run(s)
    #     nbh.hide_map_warning(output_fn)

    # def make_no_data_output(self,subfn=''):
    #     s= 'jupyter nbconvert --no-input --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute chemical_report_no_data.ipynb --to=html '
    #     subprocess.run(s)
    #     nbh.hide_map_warning(self.no_data_html_fn)

    # def compile_chem_informatics(self):
    #     cit.sdf_extract()
    def make_chem_list(self):
        import math
        t = self.allrec # just a handle
        if self.caslist != []: # then do all
            t = t[t.bgCAS.isin(self.caslist)]
        gb = t.groupby('bgCAS',as_index=False)[['bgIngredientName','epa_pref_name',
                                                'IngredientName','iupac_name']].first()
        # self.make_bgCAS_name_df(gb)
        gb = gb[:4]  #limit length for development
        lst = gb.bgCAS.unique().tolist()
        lst.sort()
        # self.make_dir_structure(lst)
        
        for (i, row) in gb.iterrows():
            #if i>15:  # control the overall list
            #    continue # skip the rest
            chem = row.bgCAS
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
            # tt = tt.filter(self.filtered_fields,axis=1).copy()
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
                # shutil.copyfile(self.no_data_fn,
                #                 os.path.join(hndl.browser_out_dir,chem,an_fn))
                print(f'{i}: ** {chem:>13} **  n recs: {len(tt):>7,};  max mass: {mx:>10,} - NO FILTERED DATA')
                continue             
            # report with data
            print(f'{i}: ** {chem:>13} **  n recs: {len(tt):>7,};  max mass: {mx:>10,}')               
            if len(tt)>0:
                tt['map_link'] = tt.apply(lambda x: th.getMapLink(x),axis=1)
            else:
                tt['map_link'] = ''
            # if len(tt)>5: # don't map the very small chemicals
                # self.sitemap_txt += f'\t<url>\n\t\t<loc>{chem}/analysis_{chem}.html</loc>\n\t</url>\n'
            # save data to file for later notebook access
            tt.to_parquet(os.path.join(hndl.sandbox_dir,'data.parquet'),index=False)
            # tt.to_csv(os.path.join(self.outdir,chem,'data.zip'),index=False,
            #         compression={'method': 'zip', 'archive_name': 'data.csv'})
            
            nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'chemical_report.ipynb'),
                                    output_fn=fulloutfn)
            self.fix_chem_html(chem,ing,tt.in_std_filtered.sum(),mx,fulloutfn)
            # an_fn = f'analysis_{chem}.html'
            # shutil.copyfile(self.jupyter_fn,
                            # os.path.join(self.outdir,chem,an_fn))

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
            
    def fix_no_data_html(self,cas,ing,num_recs,mxmass):
        # also adds favicon to browser tab
        with open(self.no_data_fn,'r',encoding='utf-8') as f:
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
        with open(self.jupyter_fn,'w',encoding='utf-8') as f:
            f.write(alltext)

    # def __init__(self,repo_name = 'unknown',data_date='UNKNOWN',caslist = [],
    #              outdir='./out/website/',data_source='bulk'):
    #     self.repo_name = repo_name
    #     self.data_date = data_date
    #     self.outdir = outdir
    #     self.data_source = data_source
    #     self.scopedir = os.path.join(self.outdir,'scope/')
    #     self.colabdir = os.path.join(self.outdir,'colab/')
    #     self.statesdir = os.path.join(self.outdir,'states/')
    #     self.operatordir = os.path.join(self.outdir,'operators/')
    #     self.images = os.path.join(self.outdir,'images/')
    #     self.sitemap_txt = """<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n"""
    #     print('Output directories:')
    #     print(f'  {self.outdir}')
    #     print(f'  {self.scopedir}')
    #     print(f'  {self.statesdir}')
    #     print(f'  {self.operatordir}')
    #     print(f'  {self.colabdir}')
    #     print(f'  {self.images}')
    #     self.css_fn = './work/style.css'
    #     #self.default_empty_fn = './website_gen/default_empty.html'
    #     self.jupyter_fn = './work/chemical_report.html'
    #     self.no_data_fn = './work/chemical_report_no_data.html'
    #     self.state_fn = './work/state_report.html'
    #     self.county_fn = './work/county_report.html'
    #     self.operator_fn = './work/operator_report.html'
    #     self.ref_fn = './work/ref.csv'
    #     self.filtered_fields = ['PercentHFJob', 
    #                             'calcMass', 'DisclosureId', 'OperatorName',
    #                             'bgOperatorName',
    #                             'APINumber', 'TotalBaseWaterVolume',
    #                             'TotalBaseNonWaterVolume', 'FFVersion', 
    #                             'TVD', 'StateName', 'StateNumber', 'CountyName', 
    #                             'CountyNumber', 'TradeName',
    #                             'Latitude', 'Longitude', 'Projection',
    #                             'data_source', 'bgStateName', 'bgCountyName', 
    #                             'bgLatitude', 'bgLongitude', 'date',
    #                             'IngredientName', 'Supplier', 'bgSupplier', 
    #                             'Purpose', 'CASNumber', 'bgCAS','primarySupplier',
    #                             'epa_pref_name','iupac_name',
    #                             'bgIngredientName','in_std_filtered',
    #                             'TradeName_trunc','Purp_trunc','has_TBWV',
    #                             'within_total_tolerance','has_water_carrier',
    #                             'carrier_status','massComp','massCompFlag',
    #                             'cleanMI','loc_within_state',
    #                             'loc_within_county','rq_lbs','bgLocationSource'] 
    #     self.caslist = caslist
    #     self.allrec = ana_set.Full_set(repo = hndl.repo_name,
    #                                       force_new_creation=True,
    #                                       outdir=work_pickles).get_set()
    #     #!!! FILTER FOR TESTING
    #     # print('WARNING: FILTER FOR TESTING IS ENABLED!')
    #     # self.allrec = self.allrec[self.allrec.bgStateName=='nevada']
    #     # ##
        
    #     #print(f'allrec len {len(self.allrec)}')
    #     w_chem = ~(self.allrec.no_chem_recs)
    #     filtered = self.allrec.in_std_filtered
    #     self.num_events = len(self.allrec.DisclosureId.unique())
    #     self.num_events_wo_FFV1 = len(self.allrec[w_chem].DisclosureId.unique())
    #     self.num_events_fil = len(self.allrec[filtered].DisclosureId.unique())
    #     self.num_events_fil_wo_FFV1 = len(self.allrec[filtered & w_chem].DisclosureId.unique())
        
    #     self.get_chem_infom_dataset()
