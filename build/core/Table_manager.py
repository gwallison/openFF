# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 14:19:41 2019

@author: Gary
"""
import pandas as pd
import numpy as np
import gc
import os
import datetime
import openFF.build.core.mass_tools as mt
#import openFF.build.core.cas_tools as ct
import openFF.build.core.external_dataset_tools as et
from openFF.common.file_handlers import save_df, get_df

class Table_constructor():
    
    def __init__(self,pkldir,sources,
                 outdir,extdir):
        self.pkldir = pkldir
        self.sources = sources
        self.trans_dir = os.path.join(self.sources,'curation_files')
        self.outdir = outdir
        self.extdir = extdir
        self.tables = {'disclosures': None,
                       'chemrecs': None,
                       'cas_ing': None,
                       'bgCAS': None,
                       'companies': None, # all company data is also in records/disc
                       }

        # self.pickle_fn = {'disclosures': os.path.join(self.pkldir,'disclosures.pkl'),
        #                   'chemrecs': os.path.join(self.pkldir,'chemrecs.pkl'),
        #                   'cas_ing': os.path.join(self.pkldir,'cas_ing.pkl'),
        #                   'bgCAS': os.path.join(self.pkldir,'bgCAS.pkl'),
        #                   'companies': os.path.join(self.pkldir,'companies.pkl'),
        #                   }

        self.pickle_fn = {'disclosures': os.path.join(self.pkldir,'disclosures.parquet'),
                          'chemrecs': os.path.join(self.pkldir,'chemrecs.parquet'),
                          'cas_ing': os.path.join(self.pkldir,'cas_ing.parquet'),
                          'bgCAS': os.path.join(self.pkldir,'bgCAS.parquet'),
                          'companies': os.path.join(self.pkldir,'companies.parquet'),
                          }
        self.cas_ing_fn = os.path.join(self.trans_dir,'casing_curated.parquet')
        self.cas_ing_source = get_df(self.cas_ing_fn)


        self.location_ref_fn = os.path.join(self.trans_dir,'DisclosureId_ref.parquet')
        self.loc_ref_df = get_df(self.location_ref_fn)
        dates = get_df(os.path.join(self.trans_dir,'upload_dates.parquet'))
        dates = dates[dates.DisclosureId.notna()] # ignore all UploadKey-only disclosures
        self.loc_ref_df = pd.merge(self.loc_ref_df,dates[['DisclosureId','date_added']],
                           on='DisclosureId',how='left',validate='1:1')

        
    def print_step(self,txt,indent=0,newlinefirst=False):
        if newlinefirst:
            print()
        s = ''
        if indent>0:
            s = '   '*indent
        print(f' {s}-- {txt}')
        
    def print_size(self,df,name='table'):
        rows,cols = df.shape
        self.print_step(f'{name:15}: rows: {rows:7}, cols: {cols:3}',1)


    def assemble_cas_ing_table(self):
        self.print_step('assembling CAS/IngredientName table')
        df = self.cas_ing_source[['CASNumber','IngredientName','bgCAS',
                                  'source','synCAS',
                                  #'categoryCAS','syn_code',
                                  #'bgSource','alt_CAS'
                                  ]]
        self.tables['cas_ing'] = df
        #ct.na_check(df,txt='assembling cas_ing table')

        
    def assemble_companies_table(self):
        self.print_step('assembling companies table')
        self.tables['companies'] = get_df(os.path.join(self.trans_dir,
                                                       'company_xlate.parquet'))\
                                      .drop(['first_date',
                                             'change_date','change_comment'],axis=1)
        
    def assemble_bgCAS_table(self,cas_ing):
        self.print_step('assembling bgCAS table')
        # ref = get_df(os.path.join(self.trans_dir,
        #                           'CAS_ref_and_names.parquet'))
        # ref.columns=['bgCAS','bgIngredientName']
        ref = get_df(os.path.join(self.trans_dir,'master_cas_number_list.parquet'))
        ref = ref[['cas_number','ing_name']]
        ref.columns = ['bgCAS','bgIngredientName']
        df = pd.DataFrame({'bgCAS':cas_ing.bgCAS.unique().tolist()})
        df = pd.merge(df,ref,on='bgCAS',how='left')
        
        self.print_step('add external references such as TEDX and PFAS',1)
        df = et.add_all_bgCAS_tables(df,sources=self.extdir,
                                     ci_source=self.trans_dir)
        self.tables['bgCAS'] = df

    def assemble_PADUS_data(self,df):
        # ext_sources_dir = self.extdir
        return et.process_PADUS(df,sources=self.extdir,
                                outdir=self.outdir)
        
        
    #########   DISCLOSURE TABLE   ################
    def make_date_fields(self,df):
        self.print_step('constructing dates',1)
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
        
        #convert date_added field
        df.date_added = pd.to_datetime(df.date_added)
        df['pub_delay_days'] = (df.date_added-df.date).dt.days
        # Any date_added earlier than 10/2018 is unknown
        refdate = datetime.datetime(2018,10,1) # date that I started keeping track
        df.pub_delay_days = np.where(df.date_added<refdate,
                                     np.NaN,
                                     df.pub_delay_days)# is less recent than refdate
        # any fracking date earlier than 4/1/2011 is before FF started taking data
        refdate = datetime.datetime(2011,4,1) # date that fracfocus started
        df.pub_delay_days = np.where(df.date<refdate,
                                     np.NaN,
                                     df.pub_delay_days)# is less recent than refdate
        return df


    def assemble_disclosure_table(self,raw_df):
        self.print_step('assembling disclosure table')
        df = raw_df.groupby('DisclosureId',as_index=False)\
                                [['JobEndDate','JobStartDate','OperatorName',
                                  'APINumber', 'TotalBaseWaterVolume',
                                  'TotalBaseNonWaterVolume','FFVersion','TVD',
                                  #'StateNumber','CountyNumber',
                                  'api10',
                                  'Projection',
                                  'data_source', # needed for backwards compat
                                  'WellName','FederalWell','IndianWell']].first()
        
        self.print_step('create bgOperatorName',1)
        cmp = self.tables['companies'][['rawName','xlateName']]
        cmp.columns = ['OperatorName','bgOperatorName']
        df = pd.merge(df,cmp,on='OperatorName', how='left')

        unOp = df[df.bgOperatorName.isna()]
        if len(unOp)>0: flag = '<******'
        else: flag= ''
        self.print_step(f'Number uncurated Operators: {len(unOp)} {flag}',2)

        df = pd.merge(df,self.loc_ref_df,on='DisclosureId',how='left',
                      validate='1:1')
        df = self.make_date_fields(df)
        # df = self.assemble_PADUS_data(df) # adds bgFederalWell, bgNat...
        self.tables['disclosures']= df



    ##########   CHEMICAL RECORDS TABLE   #############
    

    def flag_duplicated_records(self,records):
        """The duplicate record problem got somewhat worse with FFv4. In the bulk data, FF started treating
        anything below the red line as 'Ingredient Container' and labeling the old dup_rec disclosures that way,
        but in the new dup_rec disclosures, they've just moved the "other chemicals" above the red line and
        are labelled """
        records['dup_rec'] = records.duplicated(subset=['DisclosureId',
                                                    'IngredientName',
                                                    'CASNumber',
                                                    'MassIngredient',
                                                    'PercentHFJob',
                                                    'PercentHighAdditive'],
                                        keep=False)
        # records.to_csv('./sandbox/dup_rec.csv')
        c0 = records.ingKeyPresent
        # c1 = records.Supplier.str.lower().isin(['listed above','ingredient container'])
        c1a = (records.Supplier.str.lower()=='ingredient container')&(records.FFVersion<4)
        c1b = (records.Supplier.str.lower()=='listed above')&(records.FFVersion==4)
        c2b = (records.Purpose.str.lower().str[:9]=='see trade')&(records.FFVersion==4)
        c2a = (records.Purpose.str.lower().str[:9]=='ingredien')&(records.FFVersion<4)

        records['dup_rec'] = np.where(records.dup_rec&c0&(c1a|c1b)&(c2a|c2b),True,False)
        self.print_step(f'Number dups: {records.dup_rec.sum()}',2)
        return records
    
    def assemble_chem_rec_table(self,raw_df):
        self.print_step('assembling chemical records table')
        df= raw_df[['DisclosureId','CASNumber','IngredientName','PercentHFJob',
                    'Supplier','Purpose','TradeName','FFVersion',
                    'PercentHighAdditive','MassIngredient',
                    'ingKeyPresent','reckey','IngredientsId',
                    'IngredientComment','density_from_comment']].copy()
        #ct.na_check(df,txt='assembling chem_rec 1')
        
        df.Supplier = df.Supplier.fillna('MISSING')

        self.print_step('adding bgCAS',1)
        df = pd.merge(df,self.tables['cas_ing'],
                                on=['CASNumber','IngredientName'],
                                how='left')     
        # ct.na_check(df,txt='bgCAS add')
        unCAS = df[df.bgCAS.isna()]\
                    .groupby(['CASNumber','IngredientName'],as_index=False)\
                        ['DisclosureId'].count()
        unCAS.columns = ['CASNumber','IngredientName','rec_num']
        if unCAS.rec_num.sum() > 0:
            s = ' <<******'
        else:
            s = ''
        self.print_step(f'Number uncurated CAS/Ingred pairs: {len(unCAS)}, n: {unCAS.rec_num.sum()}{s}',2)
        # unCAS.to_csv(self.pkldir+'uncurated_CAS_ING.csv',encoding='utf-8',
        #              index=False, quotechar = '$')
        

        self.print_step('create bgSupplier',1)

        cmp = self.tables['companies'][['rawName','xlateName']]
        cmp.columns = ['Supplier','bgSupplier']

        if len(cmp[cmp.Supplier.duplicated()])>0:
            print(f'******  LOOKS like duplicates in COMPANY table; N: {len(cmp)} ;keeping just the first')
            # finding duplicates in company field
            print(cmp[cmp.Supplier.duplicated(keep=False)])
            cmp = cmp[~cmp.Supplier.duplicated()]

        df = pd.merge(df,cmp,on='Supplier',
                                 how='left',validate='m:1')
        # ct.na_check(df,txt='bgSupplier add')
        
        unSup = df[df.bgSupplier.isna()]
        if len(unSup)>0: 
            flag = '<******'
            print(unSup.Supplier.unique().tolist())
        else: flag= ''
        self.print_step(f'Number uncurated Suppliers: {len(unSup)} {flag}',2)
        
        self.print_step('flagging duplicate records',1)
        print(df.columns)
        self.tables['chemrecs'] = self.flag_duplicated_records(df)

        # ct.na_check(df,txt='assembling chem_rec end')

    ############   POST ASSEMBLY PROCESSING   ############

    def flag_empty_disclosures(self):
        self.print_step('flagging disclosures without chem records')
        gb = self.tables['chemrecs'].groupby('DisclosureId',as_index=False)['ingKeyPresent'].sum()
        gb['no_chem_recs'] = np.where(gb.ingKeyPresent==0,True,False)
        df = pd.merge(self.tables['disclosures'],
                      gb[['DisclosureId','no_chem_recs']],
                      on='DisclosureId',how='left')
        self.print_step(f'number empty disclosures: {df.no_chem_recs.sum()} of {len(df)}',1)
        self.tables['disclosures'] = df
        
    def flag_duplicate_disclosures(self):
        self.print_step('flag duplicate disclosures')
        df = self.tables['disclosures'].copy()
        df['api10'] = df.APINumber.str[:10]        
        df['is_duplicate'] = df.duplicated(subset=['APINumber',
                                                      'date'],
                                              keep=False)
        df.is_duplicate = np.where(df.no_chem_recs,False,df.is_duplicate)
        
        upk = df[df.is_duplicate].DisclosureId.unique().tolist()

        self.tables['disclosures']['is_duplicate'] = self.tables['disclosures'].DisclosureId.isin(upk)
        #self.tables['disclosures']['skytruth_removed'] = self.tables['disclosures'].DisclosureId.isin(stupk)
        # self.print_step(f'n redundant SkyTruth disclosures: {df.redund_skytruth.sum()}',1)
        # self.print_step(f'n duplicate SkyTruth disclosures: {df.duplicate_skytruth.sum()}',1)
        # self.print_step(f'n SkyTruth disclosures deleted from pdf library: {len(stupk)}',1)        
        # self.print_step(f'final n of SkyTruth disclosures included: {len(df[(~df.is_duplicate)&cond].DisclosureId.unique())}',1)
        self.print_step(f'n is_duplicate: {df.is_duplicate.sum()}',1)
        

    def apply_carrier_tables(self):
        self.print_step('applying carrier table data')
        ukl = self.tables['disclosures'].DisclosureId.unique().tolist()
        ikl = self.tables['chemrecs'].IngredientsId.unique().tolist()        

        recs = self.tables['chemrecs']
        disc = self.tables['disclosures']
        disc = disc.set_index('DisclosureId')
        recs = recs.set_index('IngredientsId')
        
        # set up defaults of new fields
        
        recs['is_water_carrier'] = False
        disc['carrier_status'] = 'unknown'
        #disc['carrier_percent'] = np.NaN
        #disc['has_curated_carrier'] = False
        disc['has_water_carrier'] = False
        disc['carrier_problem_flags'] = ''
        #disc['non_water_carrier'] = False

        # **** auto carrier install
        # auto_carrier_df = pd.read_csv(os.path.join(self.trans_dir,
        #                                            'carrier_list_auto.csv'),
        #                                quotechar = '$',encoding='utf-8',
        #                                low_memory=False)
        auto_carrier_df = get_df(os.path.join(self.trans_dir,'carrier_list_auto.parquet'))

        # pass auto carrier type into disc table
        gb = auto_carrier_df.groupby('DisclosureId')['auto_carrier_type'].first()
        disc = pd.merge(disc,gb,on='DisclosureId',how='left')

        # to keep sub-runs from failing...
        # if an IngredientsId is no longer
        cond = ~(auto_carrier_df.IngredientsId.isin(ikl))
        missing_uk = auto_carrier_df[cond].DisclosureId.unique().tolist()
        #auto_carrier_df[auto_carrier_df.DisclosureId.isin(missing_uk)].to_csv('./tmp/auto-carrier_UplKey_no_longer_present.csv')
        self.print_step(f'Number of auto disclosures without current matches: {len(missing_uk)}',2)
        auto_carrier_df = auto_carrier_df[~(auto_carrier_df.DisclosureId.isin(missing_uk))]
        self.print_step(f'Auto-detected carriers: {len(auto_carrier_df)}',1)
        # save list of auto carriers no longer in data set

        # get the auto_carrier label 
        uk = auto_carrier_df.DisclosureId.unique().tolist()
        ik = auto_carrier_df.IngredientsId.tolist()

        
        disc.loc[uk,'has_water_carrier'] = True
        disc.loc[uk,'carrier_status'] = 'auto-detected'
        try:
            recs.loc[ik,'is_water_carrier']  = True
        except:
            print('***ERROR applying is_water_carrier: SOMETHING IS WRONG')
        
        # **** disclosures with problems preventing carrier detection
        # prob_carrier_df = pd.read_csv(os.path.join(self.trans_dir,
        #                                            'carrier_list_prob.csv'),
        #                                quotechar = '$',encoding='utf-8')
        prob_carrier_df = get_df(os.path.join(self.trans_dir,'carrier_list_prob.parquet'))

        # to keep sub-runs from failing...
        prob_carrier_df = prob_carrier_df[prob_carrier_df.DisclosureId.isin(ukl)]
        self.print_step(f'Problem disclosures excluded: {len(prob_carrier_df)}',1)

        uk = prob_carrier_df.DisclosureId.tolist()
        reas = prob_carrier_df.reasons.tolist()
        disc.loc[uk,'carrier_status'] = 'problems-detected; carrier not identified'
        disc.loc[uk,'carrier_problem_flags'] = reas
        
        # ### the following steps remove the curation 'helpers' to make it
        # ###   a useful file
        # mg = pd.read_csv(os.path.join(self.trans_dir,
        #                               'carrier_list_curated.csv'),
        #                  quotechar='$',encoding='utf-8',low_memory=False,
        #                  dtype={'is_water_carrier':'str'})
        # #print(len(mg))
        # # this drops any spacer lines
        # mg = mg[mg.IngredientsId.notna()]
        # test = ['******','FALSE']
        # mg['temp'] = ~mg.is_water_carrier.isin(test)
        # mg.is_water_carrier = mg.temp
        # gb = mg.groupby('DisclosureId',as_index=False)['is_water_carrier'].sum()
        # upk = gb[gb.is_water_carrier>0].DisclosureId.tolist()
        # mg['cur_carrier_status'] = np.where(mg.DisclosureId.isin(upk),
        #                                     'water_based_carrier',
        #                                     'carrier_not_water')
        
        # cur_carrier_df = mg
        
        
        # # to keep sub-runs from failing...
        # cur_carrier_df = cur_carrier_df[cur_carrier_df.DisclosureId.isin(ukl)]
        # self.print_step(f'Curation detected carriers: {len(cur_carrier_df[cur_carrier_df.cur_carrier_status=="water_based_carrier"])}',1)

        # # first install data from water-based-carriers
        # cond = cur_carrier_df.cur_carrier_status=='water_based_carrier'
        # uk = cur_carrier_df[cond].DisclosureId.tolist()
        # disc.loc[uk,'has_water_carrier'] = True
        # disc.loc[uk,'carrier_status'] = 'curation-detected'

        # ik = cur_carrier_df[cur_carrier_df.is_water_carrier].IngredientsId.tolist()
        # recs.loc[ik,'is_water_carrier']  = True
        
        self.tables['disclosures'] = disc.reset_index()
        self.tables['chemrecs'] = recs.reset_index()
        
        

    def make_whole_dataset_flags(self):
        self.print_step('make whole data set flags')
        rec_df, disc_df = mt.prep_datasets(rec_df=self.tables['chemrecs'],
                                           disc_df=self.tables['disclosures'])
        self.tables['chemrecs'] = rec_df
        self.tables['disclosures'] = disc_df

    def mass_calculations(self):
        self.print_step('calculating mass',newlinefirst=True)
        rec_df, disc_df = mt.calc_mass(rec_df=self.tables['chemrecs'],
                                       disc_df=self.tables['disclosures'])
        rec_df = pd.merge(rec_df,disc_df[['DisclosureId','within_total_tolerance']],
                          on='DisclosureId',how='left')
        rec_df.calcMass = np.where(rec_df.within_total_tolerance,
                                   rec_df.calcMass,np.NaN)
        self.tables['chemrecs'] = rec_df.drop(['within_total_tolerance'],axis=1)
        self.tables['disclosures'] = disc_df
        
        self.print_step(f'number of recs with calculated mass: {len(rec_df[rec_df.calcMass>0]):,}',1)                
    
            
    def gen_primarySupplier(self): 
        self.print_step('generating primarySupplier')
        non_company = ['third party','operator','ambiguous',
                       'company supplied','customer','multiple suppliers',
                       'not a company','missing']
        rec = self.tables['chemrecs'].copy()
        rec = rec[~(rec.bgSupplier.isin(non_company))]
        rec = rec[rec.bgSupplier.notna()] # added for non curated runs
        gb = rec.groupby('DisclosureId')['bgSupplier'].agg(lambda x: x.value_counts().index[0])
        gb = gb.reset_index()
        gb.rename({'bgSupplier':'primarySupplier'},axis=1,inplace=True)
        self.tables['disclosures'] = pd.merge(self.tables['disclosures'],
                                              gb,on='DisclosureId',how='left',
                                              validate='1:1')
        
    def pickle_tables(self):
        self.print_step('pickling all tables',newlinefirst=True)
        for name in self.tables.keys():
            # self.tables[name].to_pickle(self.pickle_fn[name])
            save_df(self.tables[name],self.pickle_fn[name])

            
    def load_pickled_tables(self):
        for t in self.tables.keys():
            self.tables[t] = self.fetch_df(df_name=t)
        
    def show_size(self):
        for name in self.tables.keys():
            self.print_size(self.tables[name],name)
     
    def assemble_all_tables(self,df):
        # ct.na_check(df,txt='top of assemble all tables')
        self.assemble_cas_ing_table()
        self.assemble_companies_table()
        self.assemble_bgCAS_table(self.tables['cas_ing'])
        self.assemble_disclosure_table(df)
        #df = self.assemble_PADUS_data(df)
        self.assemble_chem_rec_table(df)
        self.apply_carrier_tables()
        self.flag_empty_disclosures()
        self.flag_duplicate_disclosures()
        self.gen_primarySupplier()
        self.make_whole_dataset_flags()
        self.mass_calculations()
        self.pickle_tables()
        self.show_size()
        
    def fetch_df(self,df_name='bgCAS',verbose=False):
        #df = pd.read_pickle(self.pickle_fn[df_name])
        df = get_df(self.pickle_fn[df_name])
        if verbose:
            print(f'  -- fetching {df_name} df')
        return df
        
    def release_tables(self):
        for name in self.tables:
            self.tables[name] = None
        gc.collect()

    def get_table_creation_date(self):
        try:
            t = os.path.getmtime(self.pickle_fn['chemrecs'])
            return datetime.datetime.fromtimestamp(t)
        except:
            return False
