
import os
import numpy as np
import pandas as pd
import shutil
import subprocess
from datetime import datetime
from openFF.common.file_handlers import get_table
from openFF.common.text_handlers import round_sig
from openFF.common.handles import repo_name, repo_dir, data_source, browser_out_dir
from openFF.common.nb_helper import make_sandbox

today = datetime.today()

class Disc_gen():
    
    def __init__(self,#repo_name = repo_name, # use common.handles version if not supplied
                  ):
        self.repo_name = repo_name # pulls from handles
        self.repo_dir = repo_dir
        self.data_source = data_source # just from common.handles
        # print(' -- fetching chemrecs', end=' ')
        self.allrec = get_table(repo_dir=self.repo_dir,
                                tname='chemrecs')
        
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

        self.out_dir = os.path.join(browser_out_dir,'disclosures')
        self.tmp = 'tmp'
        self.disclosure_fn = r"C:\MyDocs\integrated\openFF\browser\notebooks\disclosure_report.html"
        self.make_api_list()
        self.make_outdirs()
        self.make_all_files()
        
    
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

    # def fix_disclosure_title(self,disc_title):
    #     # also adds favicon to browser tab
    #     with open(self.disclosure_fn,'r',encoding='utf-8') as f:
    #         alltext = f.read()
    #     alltext  = alltext.replace('<title>disclosure_report</title>',
    #                                f'<title>{disc_title}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
 
    #     # add bootstrap 5
    #     alltext = alltext.replace('<head>',
    #                               f'<head>\n<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">')
   
    #     with open(self.disclosure_fn,'w',encoding='utf-8') as f:
    #         f.write(alltext)

    def compile_page(self,disc_title='empty title'):
        # also adds favicon to browser tab
        with open(self.disclosure_fn,'r',encoding='utf-8') as f:
            alltext = f.read()

        s = f"""<!DOCTYPE html>
        <html lang="en">
            <head>
                <!-- Required meta tags -->
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">

                <!-- Bootstrap CSS -->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

                <title>{disc_title}: Open-FF report</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">
        </head>
        <body>
            {alltext}
        </body>
        </html>
        """
        with open(self.disclosure_fn,'w',encoding='utf-8') as f:
            f.write(s)
    

    def move_and_rename(self,apicode,uploadKey):
        shutil.copyfile(self.disclosure_fn,
                        os.path.join(self.out_dir,
                                     apicode,
                                     uploadKey+'.html'))


    def make_all_files(self):
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
                meta.to_parquet(os.path.join(self.tmp,'meta.parquet'))
                chem.to_parquet(os.path.join(self.tmp,'chem.parquet'))
                self.make_disclosure_output()
                disc_title = api+'-disclosure_'+str(i+1)
                self.compile_page(disc_title)
                self.move_and_rename(apicode,upk)
 
