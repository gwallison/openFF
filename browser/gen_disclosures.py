
import os
import numpy as np
import pandas as pd
import shutil
import re
import subprocess
from datetime import datetime
from openFF.common.file_handlers import get_table
# from openFF.common.text_handlers import round_sig
from openFF.common.handles import repo_name, repo_dir, data_source, browser_out_dir, browser_nb_dir
from openFF.common.nb_helper import make_sandbox, compile_nb_page


today = datetime.today()

class Disc_gen():
    
    def __init__(self,#repo_name = repo_name, # use common.handles version if not supplied
                  ):
        self.repo_name = repo_name # pulls from handles
        self.repo_dir = repo_dir
        self.data_source = data_source # just from common.handles
        self.disc_index_fn = os.path.join(browser_nb_dir,'Disclosure_Index.ipynb')
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
                                cols=['bgCAS','epa_pref_name','bgIngredientName',
                                      'is_on_AQ_CWA','is_on_CWA','is_on_DWSHA','is_on_HH_CWA',
                                      'is_on_IRIS','is_on_NPDWR', 'is_on_PFAS_list',
                                      'is_on_TEDX','is_on_UVCB','is_on_diesel','is_on_prop65'])
        self.out_dir = os.path.join(browser_out_dir,'disclosures')
        self.tmp = 'tmp'
        self.disclosure_fn = r"C:\MyDocs\integrated\openFF\browser\notebooks\disclosure_report.html"
        self.make_api_list()
        self.make_outdirs()
        self.make_all_files()
        self.make_disc_index_page()
        
    
    def make_api_list(self):
        self.apis = self.alldisc.api10.unique().tolist()    
        #print(f'APIS: {self.apis}')    

    def make_outdirs(self):
        print('making directory structure')
        try:
            os.mkdir(self.tmp)
        except:
            pass

        try:
            os.mkdir(self.out_dir)
        except:
            print('  - output folder already exists')
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

    def make_disclosure_output(self):
        """Make a barebones html file of the jupyter notebook"""
        print('in make_disclosure_output')
        s= 'jupyter nbconvert --no-input --template basic --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute browser/notebooks/disclosure_report.ipynb --to=html '
        subprocess.run(s)


    def move_and_rename(self,apicode,uploadKey):
        shutil.copyfile(self.disclosure_fn,
                        os.path.join(self.out_dir,
                                     apicode,
                                     uploadKey+'.html'))


    # def replacenth(self, string, sub, wanted, n):
    #     """From https://stackoverflow.com/questions/35091557/replace-nth-occurrence-of-substring-in-string"""

    #     where = [m.start() for m in re.finditer(sub, string)][n-1]
    #     print(where)
    #     before = string[:where]
    #     after = string[where:]
    #     after = after.replace(sub, wanted, 1)
    #     return before + after

    # def add_DataTable_fixedHeader(self,fn,table=2):
    #     # adds the fixed header feature to the datatable (indexed by 'table') by inserting code into html
    #     find1 = "import 'https://code.jquery.com/jquery-3.6.0.min.js';"
    #     ins1  = "import 'https://code.jquery.com/jquery-3.6.0.min.js';\n    import 'https://cdn.datatables.net/fixedheader/3.4.0/js/dataTables.fixedHeader.min.js';" 

    #     find2 = 'dt_args["data"] = data;'
    #     ins2 = 'dt_args["data"] = data;\n    dt_args["fixedHeader"] = true;'

    #     with open(fn,'r') as f:
    #         txt = f.read()
        
    #     print(txt.find(find1))
    #     print(txt.find(find2))
    #     txt = txt.replace(find1,ins1)        
    #     txt = txt.replace(find2,ins2)        
    #     # txt = self.replacenth(txt,find1,ins1,table)
    #     # txt = self.replacenth(txt,find2,ins2,table)

    #     with open(fn,'w') as f:
    #         f.write(txt)

    def make_all_files(self):
        self.allCAS.to_parquet(os.path.join(self.tmp,'cas.parquet'))
        for api in self.apis[:2]:
            apicode = api[:5]
            metas = self.alldisc[self.alldisc.api10==api].copy()
            upks = metas.UploadKey.unique().tolist()
            gb = metas.groupby('UploadKey',as_index=False)[['date','OperatorName',
                                                            'is_duplicate','has_ingredients']]\
                                                            .first()
            gb.to_parquet(os.path.join(self.tmp,'all_disc.parquet'))
            for i,upk in enumerate(upks):
                meta = metas[metas.UploadKey==upk]
                chem = self.allrec[self.allrec.UploadKey==upk]
                # chem = pd.merge(chem,self.allCAS,on='bgCAS',how='left')
                meta.to_parquet(os.path.join(self.tmp,'meta.parquet'))
                chem.to_parquet(os.path.join(self.tmp,'chem.parquet'))
                self.make_disclosure_output()
                # self.add_DataTable_fixedHeader(self.disclosure_fn)
                disc_title = api+'-disclosure_'+str(i+1)
                compile_nb_page(fn=self.disclosure_fn,
                                nb_title=disc_title)
                self.move_and_rename(apicode,upk)
 

    def make_disc_index_page(self):
        name = self.disc_index_fn[:-6] + '.html'
        outfn = os.path.join(browser_out_dir,os.path.basename(name))
        s= f'jupyter nbconvert --no-input --template=basic --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute {self.disc_index_fn} --to=html --output-dir={browser_out_dir}'
        subprocess.run(s)
        compile_nb_page(fn=outfn,nb_title='Open-FF Disclosure Index')
        # self.add_DataTable_fixedHeader(outfn)

