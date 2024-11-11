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
                 use_remote=False,
                 #do_not_list= ['ambiguousID','sysAppMeta'] # leave out of reports
                 ):
        self.df = df
        self.summarize_by_chem = summarize_by_chem
        self.ignore_duplicates = ignore_duplicates
        self.use_remote = use_remote
        self.do_not_list = {'chem_index': ['non_chem_report'],
                            'colab_v1' : ['ambiguousID','non_chem_report'],
                            'summary_file' : [],
                            'single_disc': [],
                            'pdf_report1': ['ambiguousID','non_chem_report']}
        # sets of fields to include under different circumstances
        self.colsets = {'chem_index': ['composite_id','refs','img','tot_records','num_w_mass',
                                       'mass_median','mass_90_perc',
                                       'rq_lbs','func_groups',
                                       'fingerprint','extrnl','earliest_date'],
                        'colab_v1':   ['composite_id','refs','img','tot_records','num_w_mass',
                                       'tot_mass',
                                       'rq_lbs','fingerprint','extrnl'],
                        'summary_file':['bgCAS','epa_pref_name','ingredCommonName',
                                        'tot_records','num_w_mass',
                                        'tot_mass','mass_median','rq_lbs'],
                        'single_disc': ['TradeName','Supplier','Purpose','CASNumber',
                                        'bgCAS','IngredientName','bgIngredientName',
                                        'epa_pref_name','PercentHighAdditive','PercentHFJob',
                                        'mass','massSource',
                                        'MassIngredient','calcMass','extrnl','fingerprint',
                                        'refs','is_water_carrier','dup_rec','ingKeyPresent','r_flags',
                                        'max_r_warning'],
                        'pdf_report1': ['bgCAS','epa_pref_name','ingredCommonName',
                                        'refs','img','tot_records','num_w_mass','tot_mass',
                                       'mass_median','mass_90_perc','coc_lists',
                                       'rq_lbs','fingerprint','extrnl','earliest_date'],
                        }
        
        self.assemble_cas_df(use_remote=self.use_remote)
        
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
        chem_df.extrnl = np.where(~(chem_df.is_on_TSCA),chem_df.extrnl+'non-TSCA<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_diesel,chem_df.extrnl+'diesel<br>',chem_df.extrnl)
        chem_df.extrnl = np.where(chem_df.is_on_IRIS,chem_df.extrnl+'IRIS    ',chem_df.extrnl)
        chem_df['coc_lists'] = chem_df.extrnl.copy()
        chem_df.coc_lists = chem_df.coc_lists.str.replace('<br>','<br/>')
        chem_df.extrnl = '<p style="color:green;font-size:105%;text-align:center;background-color:lightgrey;">'+chem_df.extrnl.str[:-4]+'</p>'
        return chem_df


    def assemble_cas_df(self,use_remote=True): 
        if hndl.curr_platform=='remote':
            print(f'fetching from {hndl.repo_pickles_url}')
            casdf = fh.get_df_from_url(hndl.repo_pickles_url+'bgCAS.parquet','bgCAS.parquet')
            casingdf = fh.get_df_from_url(hndl.repo_pickles_url+'cas_ing.parquet','cas_ing.parquet')
        else:
            casdf = fh.get_df(os.path.join(hndl.curr_repo_pkl_dir,'bgCAS.parquet'))
            casingdf = fh.get_df(os.path.join(hndl.curr_repo_pkl_dir,'cas_ing.parquet'))

        gb = casingdf.groupby('bgCAS',as_index=False)['ingredCommonName'].first()
        casdf = casdf.merge(gb,on='bgCAS',how='left',validate='1:1')

        c1 = np.where(self.ignore_duplicates,self.df.in_std_filtered,True)

        caslst = self.df[c1].bgCAS.unique().tolist()
        cdf = casdf[casdf.bgCAS.isin(caslst)].copy()
        cdf['fingerprint'] = cdf.bgCAS.map(lambda x: th.getFingerprintImg(x))
        cdf['img'] = cdf.bgCAS.map(lambda x: th.getMoleculeImg(x,size=175,use_remote=use_remote))
        cdf['chem_detail'] = cdf.bgCAS.map(lambda x: th.getCatLink(x,x,use_remote=use_remote))
        cdf['PubChem'] = cdf.bgCAS.map(lambda x: th.getPubChemLink(x)) 
        cdf['EPA_ref'] = cdf.DTXSID.map(lambda x: th.getCompToxRef(x))
        cdf['refs'] = cdf.PubChem+'<br>'+cdf.EPA_ref
        cdf.epa_pref_name = np.where(cdf.epa_pref_name.isna(),' -- ',cdf.epa_pref_name)
        cdf['names'] = cdf.epa_pref_name +'<br>----------<br>' + cdf.ingredCommonName
        cdf['composite_id'] = '<center><h3>'+cdf.chem_detail+'</h3>'+cdf.names+'</center>'
        cdf['func_groups'] = '<center>'+cdf.eh_Class_L1 +'<br>----------<br>' +cdf.eh_Class_L2 + '</center>'
        cdf = self.make_extrnl_column(cdf)

        if self.summarize_by_chem:
            tmp = self.df[c1].groupby('bgCAS',as_index=False).size()
            tmp = tmp.rename({'size':'tot_records'},axis=1)
            cdf = cdf.merge(tmp,on='bgCAS',how='left')
            
            tmp = self.df[c1&(self.df.mass>0)].groupby('bgCAS',as_index=False).size().rename({'size':'num_w_mass'},axis=1)
            # print(tmp[tmp.num_w_mass.isna()].head())
            # print(tmp.head())
            cdf = cdf.merge(tmp,on='bgCAS',how='left')
            cdf.num_w_mass = cdf.num_w_mass.fillna(0)
            # print(cdf.columns)
            
            # Number_records is a string and therefore not numerically sortable.
            cdf['Number_records'] = cdf.tot_records.astype('str') + '<br>(' + cdf.num_w_mass.astype('str') + ')'

            tmp = self.df[c1].groupby('bgCAS',as_index=False)['date'].min().rename({'date':'earliest_date'},axis=1)
            cdf = cdf.merge(tmp,on='bgCAS',how='left')

            tmp = self.df[c1].groupby('bgCAS',as_index=False)['mass'].sum().rename({'mass':'tot_mass'},axis=1)
            tmp.tot_mass = tmp.tot_mass.map(lambda x: th.round_sig(x,3))
            cdf = cdf.merge(tmp,on='bgCAS',how='left')

            tmp = self.df[c1&(self.df.mass>0)].groupby('bgCAS',as_index=False)['mass'].apply(np.percentile,90).rename({'mass':'mass_90_perc'},axis=1)
            # tmp.mass_90_perc = tmp.mass_90_perc.map(lambda x: th.round_sig(x,3))
            cdf = cdf.merge(tmp,on='bgCAS',how='left')

            tmp = self.df[c1&(self.df.mass>0)].groupby('bgCAS',as_index=False)['mass'].median().rename({'mass':'mass_median'},axis=1)
            # tmp.mass_median = tmp.mass_median.map(lambda x: th.round_sig(x,3))
            cdf = cdf.merge(tmp,on='bgCAS',how='left')

            # cdf.fillna('',inplace=True)
        else:
            cols_to_add = self.df.columns.difference(cdf.columns).tolist()
            cols_to_add.append('bgCAS')
            # print(cols_to_add)
            cdf = pd.merge(self.df[c1][cols_to_add],cdf, on='bgCAS',how='left',validate='m:1')
            # print(cdf.columns.tolist())

        self.chem_df = cdf

    def get_storable_table(self,colset='summary_file',sortby='bgCAS'):
        assert colset in self.colsets, 'Column set not recognized'
        assert colset in self.do_not_list, 'Column set not recognized'
        if sortby in self.colsets[colset]:
            self.chem_df = self.chem_df.sort_values(sortby)
        return self.chem_df[self.colsets[colset]]

    def prep_chem_table(self,colset,sortby):
        assert colset in self.colsets, 'Column set not recognized'
        if sortby in self.colsets[colset]:
            self.chem_df = self.chem_df.sort_values(sortby)


    def get_display_table(self,colset='chem_index',sortby='composite_id'):
        self.prep_chem_table(colset,sortby)
        tmp = self.chem_df[~self.chem_df.bgCAS.isin(self.do_not_list[colset])].copy()
        return tmp[self.colsets[colset]]

    def get_html_table(self,colset='chem_index',sortby='composite_id'):
        self.prep_chem_table(colset,sortby)
        return self.chem_df[self.colsets[colset]].to_html()


    def get_pdf_table(self,colset='colab_v1'):
        pass

    def get_disclosure_table(self,colset="disc_table"):
        pass