
import os
import numpy as np
import pandas as pd
import shutil
import re
import subprocess
from datetime import datetime
from openFF.common.file_handlers import get_table
# from openFF.common.text_handlers import round_sig
from openFF.common.handles import repo_name, repo_dir, data_source, browser_nb_dir, sandbox_dir, local_includes
from openFF.common.handles import browser_out_dir, browser_inc_dir, cat_creation_date
from openFF.common.nb_helper import make_sandbox, compile_std_page, compile_nb_page, get_common_header

from openFF.common.display_tables import make_html_for_chem_table, make_chem_single_disclosure, make_html_of_disclosure_meta


today = datetime.today()

class Disc_gen():
    
    def __init__(self,#repo_name = repo_name, # use common.handles version if not supplied
                  ):
        self.repo_name = repo_name # pulls from handles
        self.repo_dir = repo_dir
        self.data_source = data_source # just from common.handles
        self.disc_index_fn = os.path.join(browser_nb_dir,'Disclosure_Index.ipynb')
        self.disc_dictionary_fn = os.path.join(browser_nb_dir,'disclosure_include.ipynb')
        self.local_includes = local_includes
        # print(' -- fetching chemrecs', end=' ')

        self.allrec = get_table(repo_dir=self.repo_dir,
                                tname='chemrecs',
                                cols = ['TradeName','Purpose','Supplier','bgSupplier',
                                        'CASNumber','bgCAS','IngredientName',
                                        'PercentHighAdditive','PercentHFJob','calcMass','MassIngredient',
                                        'is_water_carrier','dup_rec',
                                        'UploadKey','ingKeyPresent']) 
        
        # identify disclosures without chemicals
        gb = self.allrec[['UploadKey','ingKeyPresent']]\
            .groupby('UploadKey',as_index=False)['ingKeyPresent'].any()\
            .rename({'ingKeyPresent':'has_ingredients'},axis=1)
        
        # print(' -- fetching discloures')
        self.alldisc = get_table(repo_dir=self.repo_dir,
                                tname='disclosures')
        ##!! TESTING: FILTER
        self.alldisc = self.alldisc[(self.alldisc.bgStateName=='pennsylvania')&
                                    (self.alldisc.bgCountyName.isin(['jefferson']))]
        self.alldisc = pd.merge(self.alldisc,gb,on='UploadKey',how='left')     
        # print(self.alldisc.columns)   
        self.alldisc['st_cnty'] = self.alldisc.api10.str[:5]

        self.allCAS = get_table(repo_dir=self.repo_dir,tname='bgCAS',
                                cols=['bgCAS','epa_pref_name','bgIngredientName','DTXSID',
                                      'is_on_AQ_CWA','is_on_CWA','is_on_DWSHA','is_on_HH_CWA',
                                      'is_on_IRIS','is_on_NPDWR', 'is_on_PFAS_list',
                                      'is_on_TEDX','is_on_UVCB','is_on_diesel','is_on_prop65'])
        self.out_dir = os.path.join(browser_out_dir,'disclosures')
        make_sandbox(sandbox_dir)
        self.tmp = sandbox_dir
        self.disclosure_fn = r"C:\MyDocs\integrated\openFF\browser\notebooks\disclosure_report.html"
        self.make_api_list()
        self.make_outdirs()
        self.move_css_and_script_files()
        self.make_all_files()
        self.make_disc_index_page()
        # self.move_include_files()


    # def move_include_files(self):
    #     lst = os.listdir(local_includes)
    #     print(lst)
    #     for f in lst:
    #         shutil.copyfile(os.path.join(local_includes,f),
    #                         os.path.join(browser_inc_dir,f))
    
    def make_api_list(self):
        self.apis = self.alldisc.api10.unique().tolist()    
        #print(f'APIS: {self.apis}')    

    def make_outdirs(self):
        print('making output directory structure')
        dirs = [browser_out_dir,browser_inc_dir,self.out_dir]
        for d in dirs:
            try:
                os.mkdir(d)
            except:
                print(f'  - {d} already exists')
        st_cnties = self.alldisc.st_cnty.unique().tolist()
        nocnt = 0
        for st_cnty in st_cnties:
            dir_name = os.path.join(self.out_dir,st_cnty)
            try:
                os.mkdir(dir_name)
            except:
                print(dir_name)
                nocnt +=1
        print(f'State_county directory already exists for {nocnt} items.')

    def move_css_and_script_files(self):
        fns = ['disclosures.css','collapsible.js']
        for fn in fns:
            shutil.copyfile(os.path.join(self.local_includes,fn),
                            os.path.join(self.out_dir,fn))        



    # def make_disclosure_output(self):
    #     """Make a barebones html file of the jupyter notebook"""
    #     print('in make_disclosure_output')
    #     s= 'jupyter nbconvert --no-input --template basic --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute browser/notebooks/disclosure_report.ipynb --to=html '
    #     subprocess.run(s)


    def move_and_rename(self,apicode,uploadKey):
        shutil.copyfile(self.disclosure_fn,
                        os.path.join(self.out_dir,
                                     apicode,
                                     uploadKey+'.html'))

    def get_time_left(self,start,total,current):
        now = datetime.now()
        worked = now-start
        frac = current/total
        rate = worked/(current+1)
        remaining_work = total-current
        remaining_time = remaining_work*rate
        return remaining_time


    def make_all_files(self):
        self.allCAS.to_parquet(os.path.join(self.tmp,'cas.parquet'))
        starttime = datetime.now()
        for j,api in enumerate(self.apis):
            if j%100==1:
                time_left = self.get_time_left(starttime,len(self.apis),j)
                print(f'{j}/{len(self.apis)}, minutes left: {round(time_left.total_seconds()/60,1)} : API {api}')
            apicode = api[:5]
            metas = self.alldisc[self.alldisc.api10==api].copy()
            upks = metas.UploadKey.unique().tolist()
            gb = metas.groupby('UploadKey',as_index=False)[['date','OperatorName',
                                                            'is_duplicate','has_ingredients']]\
                                                            .first()
            gb.to_parquet(os.path.join(self.tmp,'all_disc.parquet'))
            for i,upk in enumerate(upks):
                meta = metas[metas.UploadKey==upk]
                meta_html = make_html_of_disclosure_meta(meta)
                chem = self.allrec[self.allrec.UploadKey==upk]
                self.chem_disc = make_chem_single_disclosure(chem,self.allCAS) # save df in self for later use
                chemout = make_html_for_chem_table(self.chem_disc)
                disc_title = api+'-disclosure_'+str(i+1)
                header = get_common_header(title=f'{api[:2]}-{api[2:5]}-{api[5:]}',
                                           #subtitle=f'FracFocus ID: {upk}',
                                           repo_name=repo_name,cat_creation_date=cat_creation_date,
                                           link_up_level=2)
                compile_std_page(fn=self.disclosure_fn,
                                nb_title=disc_title,
                                headtext=['<link rel="stylesheet" href="../disclosures.css">',header],
                                bodytext=[meta_html,chemout,
                                          '\n <script src="../collapsible.js"></script>'])
                self.move_and_rename(apicode,upk)
        self.make_disc_include_page()
 
    def make_disc_include_page(self):
        # make the disclosure 'include' file for the end of each disclosure:
        self.chem_disc.to_parquet(os.path.join(self.tmp,'chem_disc.parquet'))
        name = self.disc_dictionary_fn[:-6] + '.html'
        outfn = os.path.join(browser_out_dir,os.path.basename(name))
        s= f'jupyter nbconvert --no-input --template=basic --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute {self.disc_dictionary_fn} --to=html --output-dir={self.out_dir}'
        subprocess.run(s)
 
    def make_disc_index_page(self):
        name = self.disc_index_fn[:-6] + '.html'
        outfn = os.path.join(browser_out_dir,os.path.basename(name))
        s= f'jupyter nbconvert --no-input --template=basic --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute {self.disc_index_fn} --to=html --output-dir={browser_out_dir}'
        subprocess.run(s)
        compile_nb_page(fn=outfn,
                        header = get_common_header(title='Open-FF Disclosure Index',repo_name=repo_name,
                                                   cat_creation_date=cat_creation_date),
                        nb_title='Disclosure Index of Open-FF')
 
