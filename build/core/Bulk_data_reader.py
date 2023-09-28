# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 10:15:03 2019

@author: GAllison

This module is used to read all the raw data in from a FracFocus zip 
of CSV files.

This version created from openFF-build in Jan 2023 

"""
import zipfile
import re
import pandas as pd
import numpy as np
import os
import intg_support.cas_tools as ct
from intg_support.file_handlers import store_df_as_csv, get_csv, save_df, get_df


class Read_FF():
    """While moving to colab operations, we clearly need to cut down on amount
    of ram used for this process."""
    
    def __init__(self,in_name='testData.zip',
                 zipdir='./working/',
                 workdir='./working/',
                 origdir='./orig_dir/',
                 flat_pickle = 'raw_flat.parquet'):
        self.zname = os.path.join(zipdir,in_name)
        #self.sources = sources
        self.working = workdir
        self.origdir = origdir
        self.curdur = os.path.join(self.origdir,'curation_files')
        self.missing_values = self.getMissingList()
        self.dropList = ['ClaimantCompany', 'DTMOD', 'DisclosureKey', 
                         #'IngredientComment', 
                         'IngredientMSDS',
                         'IsWater', 'PurposeIngredientMSDS',
                         'PurposeKey', 'PurposePercentHFJob', 'Source', 
                         'SystemApproach'] # not used, speeds up processing
        self.cols_to_clean = ['OperatorName','Supplier','TradeName',
                              'CASNumber','IngredientName']
        self.cols_to_lower = ['IngredientName']
        self.picklefn = os.path.join(self.working,flat_pickle)
        
    def getMissingList(self):
        df = pd.read_csv(os.path.join(self.curdur,"missing_values.csv"),
                          quotechar='$',encoding='utf-8')
        return df.missing_value.tolist()
    
    def get_api10(self,df):
        df['api10'] = df.APINumber.str[:10]
        return df
    

    def get_density_from_comment(self,cmmt):
        """take a comment field and return density if it is present; there is a 
        common format"""
        if pd.isna(cmmt):
            return np.NaN
        if 'density' not in cmmt.lower():
            return np.NaN
        try:
            dens = re.findall(r"(\d*\.\d+|\d+)",cmmt)[0]
            return float(dens)
        except:
            return np.NaN
    
    def make_date_fields(self,df):
        """Create the 'date' and 'year' fields from JobEndDate and correct errors"""

        # drop the time portion of the datatime
        df['d1'] = df.JobEndDate.str.split().str[0]
        # fix some obvious typos that cause hidden problems
        df['d2'] = df.d1.str.replace('3012','2012')
        df['d2'] = df.d2.str.replace('2103','2013')
        # instead of translating ALL records, just do uniques records ...
        tab = pd.DataFrame({'d2':list(df.d2.unique())})
        tab['date'] = pd.to_datetime(tab.d2)
        # ... then merge back to whole data set
        df = pd.merge(df,tab,on='d2',how='left',validate='m:1')
        df = df.drop(['d1','d2'],axis=1)
        df['year'] = df.date.dt.year
        return df
    
    def clean_cols(self,df):
        """FracFocus CSV data can sometimes include non-printing characters which
        are not intended and are a nuisance.  This function removes them from the
        given columns.  It is time intensive so is only performed on critical
        columns
        
        There are a handful of annoying entries that cause havoc if left as is:
            '0.0' (in Supplier) is changed here to '0'"""
        
        # if cols ==[]: 
        #     workcols = self.cols_to_clean
        # else:
        #     workcols = []
        #     for col in cols:
        #         if col in self.cols_to_clean:
        #             workcols.append(col)

        # for colname in self.cols_to_clean:
        #     print(f'   -- cleaning {colname}')
        #     gb = df.groupby(colname,as_index=False).size()
        #     gb.columns = [colname,'junk']
        #     # replace return, newline, tab with single space
        #     gb['clean'] = gb[colname].replace(r'\r+|\n+|\t+',' ', regex=True)
        #     # remove whitespace from the ends
        #     gb.clean = gb.clean.str.strip()
        #     print(f'    -- Num cleaned : {(gb.clean!=gb[colname]).sum()}')
        #     if colname in self.cols_to_lower:
        #         gb.clean = gb.clean.str.lower()
        #     df = pd.merge(df,gb,on=colname,how='left',validate='m:1')
        #     df.rename({colname:'oldRaw','clean':colname},axis=1,inplace=True)
        #     df.drop(['oldRaw','junk'],axis=1,inplace=True)
            
        #     # # last check: do the has_nonprintable check in cas_tools
        #     # flag = df[colname].map(lambda x: ct.has_non_printable(x))
        #     # if flag.sum()!=0:
        #     #     print(f'Warning: non-printable characters still detected in {colname}!')
           
        #     df.Supplier = np.where(df.Supplier=='0.0','0',df.Supplier)
            
        # return df

        for colname in self.cols_to_clean:
            #print(f'   -- cleaning {colname}')
            gb = df.groupby(colname,as_index=False).size()
            gb.columns = [colname,'junk']
            # replace return, newline, tab with single space
            gb['clean'] = gb[colname].replace(r'\r+|\n+|\t+',' ', regex=True)
            # remove whitespace from the ends
            gb.clean = gb.clean.str.strip()
            #print(f'    -- Num cleaned : {(gb.clean!=gb[colname]).sum()}')
            if colname in self.cols_to_lower:
                gb.clean = gb.clean.str.lower()
            gb.set_index(colname,inplace=True)
            df.set_index(colname,inplace=True)
            df = df.join(gb,on=colname,how='left') 
            df.reset_index(inplace=True)
            #print(df.columns)
            #df = pd.merge(df,gb,on=colname,how='left',validate='m:1')
            df = df.rename({colname:'oldRaw','clean':colname},axis=1)
            #print(df.columns)
            df.drop(['oldRaw','junk'],axis=1,inplace=True)
            
            # # last check: do the has_nonprintable check in cas_tools
            # flag = df[colname].map(lambda x: ct.has_non_printable(x))
            # if flag.sum()!=0:
            #     print(f'Warning: non-printable characters still detected in {colname}!')
           
            df.Supplier = np.where(df.Supplier=='0.0','0',df.Supplier)
            
        return df
    
    def import_raw(self):
        """
        """
        fill_lst = ['CASNumber','IngredientName','OperatorName',
                    'Supplier','TradeName','Purpose']
        dflist = []
        with zipfile.ZipFile(self.zname) as z:
            inf = []
            for fn in z.namelist():
                # the files in the FF archive with the Ingredient records
                #  always start with this prefix...
                if fn[:17]=='FracFocusRegistry':
                    # need to extract number of file to correctly order them
                    num = int(re.search(r'\d+',fn).group())
                    inf.append((num,fn))
                    
            inf.sort()
            infiles = [x for _,x in inf]  # now we have a well-sorted list
            #print(self.startfile,self.endfile)
            for fn in infiles[0:]:
                with z.open(fn) as f:
                    print(f' -- processing {fn}')
                    t = pd.read_csv(f,low_memory=False,
                                    dtype={'APINumber':'str',
                                           'CASNumber':'str',
                                           'IngredientName':'str',
                                           'Supplier':'str',
                                           'OperatorName':'str',
                                           'StateName':'str',
                                           'CountyName':'str',
                                           'FederalWell':'str',
                                           'IndianWell':'str',
                                           'IngredientComment': 'str'},
                                    na_values = self.missing_values
                                    )
                    
                    t = self.make_date_fields(t)
                    
                    t['ingKeyPresent'] = t.IngredientKey.notna()
                    
                    t['raw_filename'] = fn # helpful for manual searches of raw files
                    t['data_source'] = 'bulk' # needed for backwards compat with catalog
                    t['density_from_comment'] = t.IngredientComment\
                                                .map(lambda x: self.get_density_from_comment(x))
                    for col in fill_lst:
                        t[col].fillna('MISSING',inplace=True)
                        
                    t = self.clean_cols(t)            
                    t = self.get_api10(t)

                    dflist.append(t)
        final = pd.concat(dflist,sort=True)
        
        final.reset_index(drop=True,inplace=True) #  single integer as index
        final['reckey'] = final.index.astype(int)
        final.drop(columns=self.dropList,inplace=True)
        assert(len(final)==len(final.reckey.unique()))
        # final.to_pickle(self.picklefn)
        save_df(final,self.picklefn)
        #return final
        
    def import_raw_old(self):
        """
        """
        dflist = []
        with zipfile.ZipFile(self.zname) as z:
            inf = []
            for fn in z.namelist():
                # the files in the FF archive with the Ingredient records
                #  always start with this prefix...
                if fn[:17]=='FracFocusRegistry':
                    # need to extract number of file to correctly order them
                    num = int(re.search(r'\d+',fn).group())
                    inf.append((num,fn))
                    
            inf.sort()
            infiles = [x for _,x in inf]  # now we have a well-sorted list
            #print(self.startfile,self.endfile)
            for fn in infiles[0:]:
                with z.open(fn) as f:
                    print(f' -- processing {fn}')
                    t = pd.read_csv(f,low_memory=False,
                                    dtype={'APINumber':'str',
                                           'CASNumber':'str',
                                           'IngredientName':'str',
                                           'Supplier':'str',
                                           'OperatorName':'str',
                                           'StateName':'str',
                                           'CountyName':'str',
                                           'FederalWell':'str',
                                           'IndianWell':'str',
                                           'IngredientComment': 'str'},
                                    na_values = self.missing_values
                                    )
                    
                    t = self.make_date_fields(t)
                    
                    # we need an indicator of the presence of IngredientKey
                    # whitout keeping the whole honking thing around
                    t['ingKeyPresent'] = t.IngredientKey.notna()
                    
                    t['raw_filename'] = fn # helpful for manual searches of raw files
                    t['data_source'] = 'bulk' # needed for backwards compat with catalog
                    t['density_from_comment'] = t.IngredientComment\
                                                .map(lambda x: self.get_density_from_comment(x))
                    dflist.append(t)
        final = pd.concat(dflist,sort=True)
        
        fill_lst = ['CASNumber','IngredientName','OperatorName',
                    'Supplier','TradeName','Purpose']
        for col in fill_lst:
            final[col].fillna('MISSING',inplace=True)
            
        final = self.clean_cols(final)

        final = self.get_api10(final)
        final.reset_index(drop=True,inplace=True) #  single integer as index
        final['reckey'] = final.index.astype(int)
        final.drop(columns=self.dropList,inplace=True)
        assert(len(final)==len(final.reckey.unique()))
        # final.to_pickle(self.picklefn)
        save_df(final,self.picklefn)
        #return final
