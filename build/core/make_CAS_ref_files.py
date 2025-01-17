# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 19:41:04 2019

@author: GAllison

This set of routines is used to translate the ref files created with SciFinder
(online) to a reference dictionary used to validate the CASNumbers and 
find accepted synonyms for IngredientNames in the FracFocus dataset.

The ref files that are used as INPUT to this routine are created by 
searching manually for a given CAS number (the 
SciFinder website has heavy restrictions on automated searches) and then saving
the SciFinder results to a text file.  The routines below parse those 
text files for the infomation used later when comparing to CASNumber codes in 
FracFocus.  Each ref file may contain several CAS-registry records; that is an
artifact of how we performed the manual searches, and is handled by the code.

Note that 'primary name' is the name used by CAS as the main name for
a material; it is the first entry in the list of synonyms.


This version is modified for cloud usage from the original Open-FF v15,
and includes storing the products in parquet format, instead of csv.

"""
import pandas as pd
import numpy as np
import shutil
import os
#import csv
import io
from openFF.common.file_handlers import save_df, get_df
import openFF.common.handles as hndl
import scrape.SciFinder.SciFinder_support as sfs
import warnings # to suppress annoying openpyxl warnings

CT_bat_fn = 'comptox_batch_results.xlsx'
CT_broad_fn = 'comptox_batch_results_broad.xlsx'
CT_meta_fn = 'comptox-chemical-lists-meta.xlsx'

encod = 'utf-8'

class CAS_list_maker():
    
    def __init__(self,orig_dir,work_dir):
        self.orig_dir = orig_dir # where repo-derived files reside
        self.work_dir = work_dir # where new files and generated files go
        self.SF_ref_dict = {}
        self.CT_ref_dict = {}
# ---------------------------------------------------------------
#  SciFinder lists        
# ---------------------------------------------------------------

## incorporating 2024 SciFinder scrape into these procedures

    def make_SciFinder_index(self):
        lst = os.listdir(hndl.sci_finder_scrape_dir)
        caslst = []
        fnlst = []
        for fn in lst:
            cas = sfs.get_cas_from_filename(fn)
            if cas:
                caslst.append(cas)
                fnlst.append(fn)
        return pd.DataFrame({'CASRN':caslst,'filename':fnlst})
    
    def process_SF_scrape_record(self,html_fn):
        """return tuple of (cas#,[syn],[dep])"""
        cas = sfs.get_cas_from_filename(html_fn)
        soup = sfs.get_soup(os.path.join(hndl.sci_finder_scrape_dir,html_fn))
        lst = sfs.get_synonyms(soup)
        dellst = sfs.get_deleted_registry_numbers(soup)
        ingname = sfs.get_substance_name(soup)
        return (cas,lst,dellst,ingname)
        
    def process_all_SF(self):
        casdf = self.make_SciFinder_index()
        ingname = []
        ingcas = []
        syncas = []
        synname = []
        delcas = []
        delrepl = []
        print(f'processing {len(casdf)} SciFinder files: ',end=' ')
        for i,row in casdf.iterrows():
            if i%100==0: print(i,end=' ')
            res = self.process_SF_scrape_record(os.path.join(hndl.sci_finder_scrape_dir,
                                                             row.filename))
            # first the synonyms
            for syn in res[1]:
                syncas.append(row.CASRN)
                synname.append(syn.lower())
            # now deprecated:
            for dep in res[2]:
                delcas.append(dep)
                delrepl.append(row.CASRN)
            # finally the ingredient name
            ingcas.append(row.CASRN)
            ingname.append(res[3])
        
        self.SFname = pd.DataFrame({'cas_number':ingcas,'ing_name':ingname})
        self.SFsyn = pd.DataFrame({'cas_number':syncas,'synonym':synname})
        self.SFsyn = self.SFsyn[~self.SFsyn.duplicated()]
        # print(self.SFsyn[self.SFsyn[['cas_number','synonym']].duplicated()])
        self.SFsyn['source'] = 'SciFinder' 
        self.SFdeprecated = pd.DataFrame({'deprecated':delcas,'cas_replacement':delrepl})

## ORIGINAL scifinder code

    # def process_SF_record(self,rec):
    #     """return tuple of (cas#,[syn],[dep])"""
    #     cas = 'Nope'
    #     prime = 'empty'
    #     lst = [] # for synonyms
    #     dellst = [] # for deprecated cas numbers
    #     fields = rec.split('FIELD ')
    #     for fld in fields:
    #         if 'Registry Number:' in fld:
    #             start = fld.find(':')+1
    #             end = fld.find('\n')
    #             cas = fld[start:end]
    #         if 'CA Index Name:' in fld:
    #             start = fld.find(':')+1
    #             end = fld.find('\n')
    #             prime = fld[start:end].lower()
    #         if 'Other Names:' in fld:
    #             start = fld.find(':')+1
    #             lst = fld[start:].split(';')
    #         if 'Deleted Registry Number(s):' in fld:
    #             start = fld.find(':')+1
    #             dellst = fld[start:].split(',')
    #     olst = [prime]
    #     for syn in lst:
    #         syn = syn.strip().lower()
    #         if len(syn)>0: 
    #             if syn not in olst:
    #                 olst.append(syn)                 
    #     return (cas,olst,dellst)

    # def process_SF_file(self,fn,ref_dict):
    #     """process individual SF file"""
    #     with io.open(fn,'r',encoding=encod) as f:
    #         whole = f.read()
    #     # make sure it looks like the correct format
    #     if whole[:12] != 'START_RECORD':
    #         print(f'Looks like file: {fn} may not be "tagged" format!')
    #         print(whole[:15])
    #         print('ignored...')
    #         return ref_dict
    #     records = whole.split('END_RECORD')
    #     for rec in records:
    #         tup = self.process_SF_record(rec)
    #         ref_dict[tup[0]] = [tup[1],tup[2]]   
    #     return ref_dict

    # def make_SF_name_list(self):
    #     inputdir = os.path.join(self.orig_dir,'CAS_ref_files')
    #     self.SF_ref_dict = {}
    #     fnlst = os.listdir(inputdir)
    #     for fn in fnlst:
    #         self.SF_ref_dict = self.process_SF_file(os.path.join(inputdir,fn),
    #                                    self.SF_ref_dict)
    #     # are there new entries?
    #     try:
    #         newdir = os.path.join(self.work_dir,'new_CAS_REF')
    #         fnlst = os.listdir(newdir)
    #         print(f'     -- including added files: {fnlst}')
    #         for fn in fnlst:
    #             self.SF_ref_dict = self.process_SF_file(os.path.join(newdir,fn),
    #                                        self.SF_ref_dict)        
    #     except:
    #         print(f'No new files found in {newdir}')
            
    #     casl = list(self.SF_ref_dict.keys())
        
    #     # first produce the cas# : ingredName file
    #     namel = []
    #     for cas in casl:
    #         namel.append(self.SF_ref_dict[cas][0][0])  # take first name as primary
    #     self.SFname = pd.DataFrame({'cas_number':casl,'ing_name':namel})
    
    
    # def make_SF_syn_list(self):
    #     casl = self.SFname.cas_number.tolist()
    #     synl = []
    #     cas_for_syn = []
    #     for cas in casl:
    #         for syn in self.SF_ref_dict[cas][0]:
    #             synl.append(syn)
    #             cas_for_syn.append(cas)
    #     self.SFsyn = pd.DataFrame({'synonym':synl,'cas_number':cas_for_syn})
    #     self.SFsyn['source'] = 'SciFinder'
    #     # print(f'Len SFsyn: {len(self.SFsyn)}')
        
    # def make_SF_deprecated_list(self):        
    #     #n Next produce the deprecated file: dep_cas : cas#
    #     depl = []
    #     casl = self.SFname.cas_number.tolist()
    #     cas_for_dep = []
    #     for cas in casl:
    #         for dep in self.SF_ref_dict[cas][1]:
    #             t = dep.strip()
    #             t = t.replace('\n',';') # allow them to be on multiple lines
    #             if len(t)>0:
    #                 lst = t.split(';')
    #                 for item in lst:
    #                     if not item == '':
    #                         depl.append(item.strip())      
    #                         cas_for_dep.append(cas)
    #     self.SFdeprecated = pd.DataFrame({'deprecated':depl,'cas_replacement':cas_for_dep})
    #     save_df(self.SFdeprecated,os.path.join(self.work_dir,'CAS_deprecated.parquet'))
        

    # def make_all_SF(self):
    #     self.make_SF_name_list()
    #     self.make_SF_syn_list()
    #     self.make_SF_deprecated_list()

# ---------------------------------------------------------------
#  CompTox lists        
# ---------------------------------------------------------------
    
    def make_CT_name_list_from_fn(self,fn):
        t = pd.read_excel(fn, engine="openpyxl",sheet_name="Main Data")
        t = t.rename({'INPUT':'cas_number','PREFERRED_NAME':'epa_preferred_name',
                      'IUPAC_NAME':'iupac_name'},axis=1)
        t = t[['cas_number','FOUND_BY','DTXSID','epa_preferred_name','iupac_name']]
        c = t.epa_preferred_name.notna()
        return t[c].copy()
        
    def make_CT_list_list_from_fn(self,fn):
        """used to collect CT list membership for all lists and chemicals"""
        t = pd.read_excel(fn, engine="openpyxl",sheet_name="Main Data")
        t = t.rename({'INPUT':'cas_number','PREFERRED_NAME':'epa_preferred_name'},
                     axis=1)
        c1 = t.epa_preferred_name.notna()
        c2 = ~t.cas_number.duplicated()
        t = t[c1&c2].drop(['FOUND_BY','DTXSID','CASRN','IUPAC_NAME','epa_preferred_name'],
                          errors='ignore',axis=1)
        cols = t.columns.tolist()
        for col in cols:
            if not col == 'cas_number':
                # convert them to boolean
                t[col] = t[col]=='Y'
        return t
    
    def make_CT_synraw_list_from_fn(self,fn,name_df):
        # name_df is the name df from the same file (it has the CAS numbers)
        st = pd.read_excel(fn, engine="openpyxl",sheet_name="Synonym Identifier")
        st.columns = ['epa_preferred_name','identifier','dummy']
        return pd.merge(name_df[['cas_number','epa_preferred_name']],
                        st[['epa_preferred_name','identifier']],
                        on='epa_preferred_name',how='left')
    
    def make_CT_name_list(self):
        """has the names of the current CAS_curated list"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                self.CTname = self.make_CT_name_list_from_fn(os.path.join(self.work_dir,
                                                              CT_bat_fn))
                print(f' - Using work_dir version of {CT_bat_fn} for name list.')
            except:
                print(' - New CompTox current search file not available, using repo version')
                self.CTname = self.make_CT_name_list_from_fn(os.path.join(self.orig_dir,
                                                                          'CompTox_ref_files',
                                                                          CT_bat_fn))
        #drop all but first instance of unique cas_numbers
        self.CTname = self.CTname[~self.CTname.cas_number.duplicated()]
        # print(f'Number in CompTox names: {len(self.CTname)}')

    def make_syn_list(self,cas,rec,caslst,synlst):
        if rec in ['',None,np.NaN]:
            return caslst, synlst
        lst = rec.split('|')
        for i in lst:
            caslst.append(cas)
            synlst.append(i.strip().lower())
        #print(f'finished syn_list {cas}')
        return caslst,synlst

    def get_CT_list(self,fn):
        # suppressing openpyxl warnings: https://stackoverflow.com/questions/14463277/how-to-disable-python-warnings/14463362#14463362
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            names = self.make_CT_name_list_from_fn(fn)
            #print('got names')
            rawsyn = self.make_CT_synraw_list_from_fn(fn, names)
            #print('got rawsyn')
        caslst = []
        synlst = []
        for i,row in rawsyn.iterrows():
             if row.identifier != np.NaN:
                 caslst,synlst = self.make_syn_list(row.cas_number,
                                                    row.identifier,
                                                    caslst,
                                                    synlst)
        return pd.DataFrame({'cas_number':caslst,'synonym':synlst})
               
        
    def make_CT_syn_list(self):
        # we need the broad_search_file and the FF list. Could be new, but may not exist.

        # current list first - if the fresh batch search file has no syn page 
        # (because EPA's site has lost that function), use previously saved
        # version.  It will not be complete, but will be better than NO CT syns.
        
        #print('start ct syn list')               
        try:
            fn = os.path.join(self.work_dir,CT_bat_fn)
            #print(f' using {fn}')
            curr_syn = self.get_CT_list(fn)
            
            print(f' - Using fresh version of {CT_bat_fn} for synonyms')
        
        except:
            print(f' - Using backup version of {CT_bat_fn} for synonyms')
            curr_syn = get_df(os.path.join(self.orig_dir,'curation_files',
                                           'CT_syn_backup.parquet'))
            
            # fn = os.path.join(self.orig_dir,'CompTox_ref_files',CT_bat_fn)
            # #print(fn)
            # curr_syn = self.get_CT_list(fn)
        # make backup in case next update can't include synonyms
        save_df(curr_syn,os.path.join(self.work_dir,'CT_syn_backup.parquet'))
        
        # now broad search
        #print('start broad sny list')
        try:
            fn = os.path.join(self.work_dir,CT_broad_fn)
            broad_syn = self.get_CT_list(fn)
            print(f' - Using fresh version of {CT_broad_fn} for synonyms')
        except:
            print(f' - Using repo version of {CT_broad_fn} for synonyms')
            fn = os.path.join(self.orig_dir,'CompTox_ref_files',CT_broad_fn)
            broad_syn = self.get_CT_list(fn)

        self.CTsyn = pd.concat([curr_syn,broad_syn],sort=True)
        self.CTsyn['source'] = 'CompTox'
        self.CTsyn = self.CTsyn[~(self.CTsyn[['cas_number','synonym']].duplicated())]
        # print(f'Len CTsyn: {len(self.CTsyn)}')

    def make_all_CT(self):
        self.make_CT_name_list()
        self.make_CT_syn_list()
        
# ---------------------------------------------------------------
#  Other lists        
# ---------------------------------------------------------------

    def make_non_spec_syn_list(self):
        self.NSsyn = get_df(os.path.join(self.orig_dir,'curation_files','IngName_non-specific_list.parquet'))
        self.NSsyn['cas_number'] = 'estab_non_spec'
        self.NSsyn.rename({'non_specific_code':'synonym'},axis=1,inplace=True)
        
        
    def make_CT_lists_list(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ## first the meta file
            try:
                fn = os.path.join(self.work_dir,CT_meta_fn)
                t = pd.read_excel(fn)
            except:
                print(f' - Using repo version for {CT_meta_fn}')
                fn = os.path.join(self.orig_dir,'curation_files',CT_meta_fn)
                t = pd.read_excel(fn)
                shutil.copy(fn,self.work_dir) # get a copy for the repo
            t = t.rename({'List Acronym':'list_acronym',
                          'List Name':'list_name',
                          'Last Updated':'last_updated',
                          '# of Chemicals':'num_Chemicals',
                          'List Description':'list_description'},
                         axis=1)
            
            save_df(t,os.path.join(self.work_dir,'comptox_list_meta.parquet'))
            
            ## now the presence file
            try:
                t = self.make_CT_list_list_from_fn(os.path.join(self.work_dir,
                                                              CT_bat_fn))
                print(f' - Using work_dir version of {CT_bat_fn} for lists table.')
            except:
                print(' - New CompTox current search file not available, using repo version for lists table')
                t = self.make_CT_list_list_from_fn(os.path.join(self.orig_dir,
                                                                          'CompTox_ref_files',
                                                                          CT_bat_fn))
            save_df(t,os.path.join(self.work_dir,'comptox_lists_table.parquet'))
            
        
# ---------------------------------------------------------------
#  Composite lists - SF + CT + others => final lists        
# ---------------------------------------------------------------
    
    def make_full_package(self):
        self.make_non_spec_syn_list()
        # self.make_all_SF()  # this is fr the old version
        self.process_all_SF()
        self.make_all_CT()
        self.final_name_list = pd.merge(self.SFname,self.CTname,
                                        on='cas_number',how='outer',validate='1:1',
                                        indicator=True)
        save_df(self.final_name_list[['cas_number','ing_name','DTXSID',
                                      'epa_preferred_name','iupac_name']],
                os.path.join(self.work_dir,'master_cas_number_list.parquet'))
        
        
        syndf = pd.merge(self.SFsyn[['cas_number','synonym']],
                         self.CTsyn[['cas_number','synonym']],
                         on=['cas_number','synonym'],how='outer',
                         indicator=True,validate='1:1')
        syndf['Source'] = np.where(syndf._merge=='both','SciFinder & CompTox','')
        syndf['Source'] = np.where(syndf._merge=='right_only','CompTox',syndf.Source)
        syndf['Source'] = np.where(syndf._merge=='left_only','SciFinder',syndf.Source)
        # print(len(syndf))
        syndf = pd.merge(syndf.drop('_merge',axis=1),self.NSsyn,
                         on=['cas_number','synonym'],how='outer',
                         indicator=True,validate='1:1')
        syndf.Source = np.where(syndf._merge=='both',
                                syndf.Source+' & '+syndf.source,
                                syndf.Source)
        syndf.Source = np.where(syndf._merge=='right_only',
                                syndf.source,
                                syndf.Source)
        # print(len(syndf))
        self.final_syn_list = syndf
        save_df(self.final_syn_list[['cas_number','synonym','Source']],
                os.path.join(self.work_dir,'master_synonym_list.parquet'))
        
        self.make_CT_lists_list()
        
    def make_partial_set(self):
        # self.make_all_SF()
        self.process_all_SF()
        self.make_all_CT()
        self.final_name_list = pd.merge(self.SFname,self.CTname,
                                        on='cas_number',how='outer',validate='1:1',
                                        indicator=True)
        save_df(self.final_name_list[['cas_number','ing_name','DTXSID',
                                      'epa_preferred_name','iupac_name']],
                os.path.join(self.work_dir,'master_cas_number_list.parquet'))
