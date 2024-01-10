"""Used to produce a chemical summary list in a variety of formats for use across Open-FF.  
It is meant to be the single place where lists are created to make changes and standarization simpler """

import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import os
import pandas as pd
import numpy as np
import openFF.common.file_handlers as fh
import openFF.common.text_handlers as th
import openFF.common.handles as hndl

class ChemListSummary():
    def __init__(self,df,
                 summarize_by_chem=True, # False: show all records
                 ignore_duplicates=True, # just the std_filtered data
                 ):
        self.df = df
        self.summarize_by_chem = summarize_by_chem
        self.colsets = {'chem_index': ['composite_id','ref','img','num_rec','num_mass','perc_mass',
                                       'rq','fingerprint','cc_lsts','earliest']}
        casdf = fh.get_df(os.path.join(hndl.curr_repo_pkl_dir,'bgCAS.parquet'))
        # print(self.casdf.columns)                              
        c1 = True
        if ignore_duplicates: c1 = df.in_std_filtered

        caslst = df[c1].bgCAS.unique().tolist()
        cdf = casdf[casdf.bgCAS.isin(caslst)].copy()
        cdf['fingerprint'] = cdf.bgCAS.map(lambda x: th.getFingerprintImg(x))
        cdf['img'] = cdf.bgCAS.map(lambda x: th.getMoleculeImg(x))
        cdf['History'] = cdf.bgCAS.map(lambda x: th.getCatLink(x,x))
        cdf['PubChem'] = cdf.bgCAS.map(lambda x: th.getPubChemLink(x)) 
        cdf['EPA_ref'] = cdf.DTXSID.map(lambda x: th.getCompToxRef(x))
        cdf = self.make_extrnl_column(cdf)

        if self.summarize_by_chem:
            tmp = self.df[c1].groupby('bgCAS',as_index=False).size()
            tmp = tmp.rename({'size':'tot_records'},axis=1)
            cdf = cdf.merge(tmp,on='bgCAS',how='left')
            
            tmp = df[c1&(df.mass>0)].groupby('bgCAS',as_index=False).size().rename({'size':'num_w_mass'},axis=1)
            tmp.num_w_mass.fillna(0)
            cdf = cdf.merge(tmp,on='bgCAS',how='left')
        else:
            cdf = pd.merge(df[c1],cdf, on='bgCAS',how='left',validate='m:1')

        self.chem_df = cdf

    def make_extrnl_column(self,chem_df):
        chem_df['extrnl'] = np.where(chem_df.is_on_CWA,'CWA<br>','    ')
        chem_df.extrnl = np.where(chem_df.is_on_AQ_CWA,chem_df.extrnl+'AQ_CWA<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_HH_CWA,chem_df.extrnl+'HH_CWA<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_NPDWR,chem_df.extrnl+'NPDWR<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_DWSHA,chem_df.extrnl+'DWSHA<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_TEDX,chem_df.extrnl+'TEDX<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_prop65,chem_df.extrnl+'prop65<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_PFAS_list,chem_df.extrnl+'EPA_PFAS<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_UVCB,chem_df.extrnl+'UVCB<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_diesel,chem_df.extrnl+'diesel<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_IRIS,chem_df.extrnl+'IRIS    ',chem_df.extrnl)
        chem_df.extrnl = '<p style="color:green;font-size:105%;text-align:center;background-color:lightgrey;">'+chem_df.extrnl.str[:-4]+'</p>'
        return chem_df


    
    def display_table(self,colset='chem_index'):
        pass

    def get_html_table(self,colset='chem_index'):
        pass

    def get_pdf_table(self,colset='chem_index'):
        pass

    def get_disclosure_table(self,colset="disc_table"):
        pass