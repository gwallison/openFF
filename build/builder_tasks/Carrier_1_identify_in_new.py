# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 15:37:55 2021

@author: Gary
"""
import pandas as pd
import numpy as np
import os
import datetime
from intg_support.file_handlers import store_df_as_csv, get_csv, save_df, get_df

#import build_common
#trans_dir = build_common.get_transformed_dir()


lower_tolerance = 95
upper_tolerance = 105

density_min = 6.0
density_max = 13.0

today_str = datetime.datetime.today().strftime("%Y-%m-%d")


class Carrier_ID():
    def __init__(self,input_df,ref_dir='./ref_dir',out_dir='./out_dir'):
        # self.remove_dropped_keys = remove_dropped_keys
        # if not self.remove_dropped_keys:
        #     print('  -- Not removing dropped keys from carrier sets')
        self.df = input_df
        self.in_upk = self.df.UploadKey
        self.in_ik = self.df.IngredientKey
        self.ref_dir = ref_dir
        self.out_dir = out_dir
        #self.curdf_fn = os.path.join(self.ref_dir,'curation_files','carrier_list_curated.csv')
        #self.curprobdf_fn = os.path.join(self.ref_dir,'curation_files','curated_carrier_problems.csv')
        # self.data_source = data_source
        # self.auto_fn = trans_dir+f'{data_source}/carrier_list_auto.csv'
        # self.curdf_fn = trans_dir+f'{data_source}/carrier_list_curated.csv'
        # self.probdf_fn = trans_dir+f'{data_source}/carrier_list_prob.csv'
        
        # list of single purpose lables for carriers
        self.wlst = ['carrier / base fluid', 'carrier/base fluid', 'carrier fluid',
                'carrier','base fluid','base carrier fluid','carrier/base flud',
                'base fluid / carrier','carrier/ base fluid','base/carrier fluid',
                'carrier base fluid','water','base fluid ',' carrier / base fluid ',
                'base fluid & mix water', 'base fluid & mix water,', 'fresh water',
                'carrier/base fluid ', 'treatment carrier', 'carrier/basefluid',
                'carrying agent', 'base / carrier fluid', 'carrier / base fluid - water',
                'carrier fluid ', 'base frac fluid', 'water',
                'water / produced water', 'carrier ', 'base carrier',
                'fracture fluid', 'frac base fluid']

        self.proppants = ['14808-60-7','1302-93-8','1318-16-7','1302-74-5',
                              '1344-28-1','14464-46-1','7631-86-9','1302-76-7',
                              '308075-07-2','66402-68-4']
        self.gasses = ['7727-37-9','124-38-9']
        self.merge_bgCAS()
        self.make_percent_sums()
        # self.fetch_carrier_lists()

        
    

    # def fetch_carrier_lists(self):
        
    #     try:
    #         #print('  -- loading curated carrier records')
    #         self.curdf = pd.read_csv(self.curdf_fn,low_memory=False,
    #                                   quotechar='$',encoding='utf-8')
    #         #print(f' curdf: {len(self.curdf.UploadKey.unique())}')
    #         #self.curdf = self.check_for_removed_keys(self.curdf)        
    #         self.remove_disclosures(self.curdf)
    #     except:
    #         self.curdf = pd.DataFrame()
            
    #     try:
    #         #print('  -- loading curated problem records')
    #         self.curprobdf = pd.read_csv(self.curprobdf_fn,low_memory=False,
    #                                   quotechar='$',encoding='utf-8')
    #         # self.curdf = self.check_for_removed_keys(self.curdf)        
    #         self.remove_disclosures(self.curprobdf)
    #     except:
    #         self.curprobdf = pd.DataFrame()
            
    def merge_bgCAS(self):
        #casing =  pd.read_csv('./sources/casing_curate_master.csv',
        casing =  get_df(os.path.join(self.out_dir,'casing_curated.parquet'))
        casing['is_valid_CAS'] = casing.bgCAS.str[0].str.isnumeric()
        self.df = pd.merge(self.df,casing[['CASNumber','IngredientName',
                                           'bgCAS','is_valid_CAS']],
                           on=['CASNumber','IngredientName'],how='left')
        self.df.is_valid_CAS.fillna(False,inplace=True)
        
    # def make_MI_fields(self):
    #     # remove records that are more likely unreliable: when MI is small
    #     cond = (self.df.MassIngredient>2)&(self.df.PercentHFJob>0)
    #     t = self.df[cond][['MassIngredient','PercentHFJob','UploadKey']].copy()
        
    #     # make a simple ratio of MI to %HFJ.  If everything is consistent, this
    #     # ratio should essentially be the same for all records in a disclosure
    #     t['permassratio'] = t.MassIngredient/t.PercentHFJob
    #     gb = t.groupby('UploadKey',as_index=False)['permassratio'].agg(['min','max']).reset_index()
    #     gb.columns = ['UploadKey','small','big']
    #     gb['rat_dev'] = (gb.big-gb.small)/gb.big
    #     # set MIok to true if the range within a disclosure is less than 10%
    #     #    MIok is a disclosure level flag.
    #     gb['MIok'] = gb.rat_dev<.1
        
    #     print(f'Creating MIok: Number disclosures with MI: {len(gb)}, out of tolerance: {len(gb[gb.rat_dev>0.1])}')

    #     self.df = pd.merge(self.df,gb[['UploadKey','MIok']],on='UploadKey',how='left')
    #     self.df.MIok = np.where(~cond,False,self.df.MIok)  
        
    #     cond2 = (self.df.MassIngredient>5)&(self.df.TotalBaseWaterVolume>10000)&self.df.MIok
    #     self.df['dens_test'] = np.where(cond2,
    #                            self.df.MassIngredient/self.df.TotalBaseWaterVolume,
    #                            np.NaN)
    #     # density can be within pretty wide range; will check again at 
    #     c1 = self.df.dens_test>density_min
    #     c2 = self.df.dens_test<density_max
    #     self.df['maybe_water_by_MI']=np.where(c1&c2,'yes','no')
    #     self.df.maybe_water_by_MI = np.where(self.df.dens_test.isna(),
    #                                          'not testable',
    #                                          self.df.maybe_water_by_MI)        
        
    def make_percent_sums(self):
        gball = self.df.groupby('UploadKey',as_index=False)[['PercentHFJob',
                                                            'is_valid_CAS']].sum()
        gball['has_no_percHF'] = ~(gball.PercentHFJob>0)
        gball['has_no_valid_CAS'] = ~(gball.is_valid_CAS>0)

        gbmax = self.df.groupby('UploadKey',as_index=False)[['PercentHFJob',
                                                             'TotalBaseWaterVolume']].max()
        gbmax.columns = ['UploadKey','PercMax','TBWV']
        gball = pd.merge(gball,gbmax,on='UploadKey',how='left')

        cond = self.df.PercentHFJob>0
        gbw = self.df[cond].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbw.columns = ['UploadKey','percSumAll']
        gbwo = self.df[cond&self.df.is_valid_CAS].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbwo.columns = ['UploadKey','percSumValid']
        gbwoSA = self.df[cond&(~(self.df.bgCAS=='sysAppMeta'))].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbwoSA.columns = ['UploadKey','percNoSysApp']
        mg = pd.merge(gball,gbw,on=['UploadKey'],how='left')
        mg = pd.merge(mg,gbwo,on='UploadKey',how='left')
        mg = pd.merge(mg,gbwoSA,on='UploadKey',how='left')

        c1 = self.df.bgCAS.isin(self.proppants)
        c2 = self.df.Purpose == 'Proppant'
        gbprop = self.df[cond&(c1|c2)].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbprop.columns = ['UploadKey','percProp']
        mg = pd.merge(mg,gbprop,on='UploadKey',how='left')
        gbwater = self.df[self.df.bgCAS=='7732-18-5'].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbwater.columns = ['UploadKey','percWater']
        mg = pd.merge(mg,gbwater,on='UploadKey',how='left')

        gbgas = self.df[self.df.bgCAS.isin(self.gasses)].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbgas.columns = ['UploadKey','percGas']
        mg = pd.merge(mg,gbgas,on='UploadKey',how='left')

        gbclo2 = self.df[self.df.bgCAS=='10049-04-4'].groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gbclo2.columns = ['UploadKey','percClo2']
        mg = pd.merge(mg,gbclo2,on='UploadKey',how='left')
        
        # trying to remove disclosures where non-water individual records are too big
        # c1 is the standard chemicals used as carriers; c2 covers ambiguousID etc
        # the salts are sometimes used as proxies for water; as in brine water is labelled as 7647-14-5
        self.df.bgCAS.fillna('unknown',inplace=True)
        c1 = self.df.bgCAS.isin(['7732-18-5', # water
                                 '7447-40-7', # potassium chloride
                                 '10043-52-4', # calcium chloride
                                 '7647-14-5', # sodium chloride
                                 '10049-04-4']) # chlorine dioxide        
        c2 = ~(self.df.bgCAS.str[0].str.isnumeric())
        c_not_either = ~(c1|c2)
        gbnonwater = self.df[c_not_either].groupby('UploadKey',as_index=False)['PercentHFJob'].max()
        gbnonwater.columns = ['UploadKey','percnonwater']
        self.disc = pd.merge(mg,gbnonwater,on='UploadKey',how='left')
        
        
    def addToProbDict(self,dic,UploadKeyList,problem):
        for upl in UploadKeyList:
            dic.setdefault(upl, []).append(problem)
        return dic            
    
    def show_prob_summary(self,dic):
        probs = {0:'No ingredients',
                 1:'Total water volume missing or 0',
                 2:'Ingredients have only 0 or missing PercentHFJob',
                 3:'Sum of all valid ingredients is greater than upper tolerance',
                 4:'Sum of ingredients with sys app meta removed sum is greater than upper tolerance',
                 5:'Proppant percentage sum is greater than water percentage',
                 6:'Sum of all ingredients is less than 90%',
                 7:'Not used: Gasses are dominant (>50%)',
                 8:'Chlorine dioxide percentage is 100',
                 #9:'Nonwater carrier record too large (>50%)'
                 }
        print('Summary of disclosures with water carrier identification problems:')
        for i in probs.keys():
            cntr = 0
            for disc in dic:
                if i in dic[disc]:
                    cntr +=1
            print(f'{cntr:8,} : {probs[i]}')

    def check_for_prob_disc(self):
        d = {}
        
        upkl = self.disc[~(self.disc.TBWV>0)].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 1)

        upkl = self.disc[self.disc.percSumValid>upper_tolerance].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 3)

        upkl = self.disc[self.disc.percNoSysApp>upper_tolerance].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 4)

        upkl = self.disc[self.disc.has_no_percHF].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 2)
        
        upkl = self.disc[self.disc.has_no_valid_CAS].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 0)
        
        upkl = self.disc[self.disc.percProp>50].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 5)

        upkl = self.disc[self.disc.percSumAll<90].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 6)

        #gasses are dominant        
        upkl = self.disc[self.disc.percGas>=50].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 7)
        
        # if chlorine dioxide is 100%        
        upkl = self.disc[self.disc.percClo2>=99.9].UploadKey.unique().tolist()
        d = self.addToProbDict(d, upkl, 8)

        # # if nonwater carrier records is too large        
        # upkl = self.disc[self.disc.percnonwater>50].UploadKey.unique().tolist()
        # d = self.addToProbDict(d, upkl, 9)

        self.show_prob_summary(d)

        

        uploadKeys = []
        problems = []
        for upk in d.keys():
            uploadKeys.append(upk)
            problems.append(str(d[upk])[1:-1])
        self.probdf = pd.DataFrame({'UploadKey':uploadKeys,
                            'reasons':problems})
        # self.probdf.to_csv(os.path.join(self.out_dir,'carrier_list_prob.csv'),
        #                    encoding= 'utf-8',quotechar='$',index=False)
        save_df(self.probdf,os.path.join(self.out_dir,'carrier_list_prob.parquet'))

        self.remove_disclosures(self.probdf)
        print(f'Total problem disclosures: {len(d):,}; Number remaining: {len(self.df.UploadKey.unique()):,}\n')
        
    def auto_set_1(self):
        """ THis is the most basic auto algorithm set:
            - looking only at records with valid CAS numbers
            - single record with a carrier purpose
            - CASNumber is water
            - 50% < %HFJob <= 100% (changing so single records of 100% are ok; 3/2023) 
        """
        
        t = self.df[self.df.is_valid_CAS].copy()
        t['has_purp'] = t.Purpose.str.strip().str.lower().isin(self.wlst)
        gbp = t.groupby('UploadKey',as_index=False)['has_purp'].sum()
        t = t.drop('has_purp',axis=1)
        t = pd.merge(t,gbp,on='UploadKey',how='left')
        
        #print(f'IS IN t: {(t.UploadKey=="ffd52c1a-1868-4b7f-a8a8-47c6621d4802").sum()}')
    
        c1 = t.has_purp==1  # only 1 record with Purpose in wlst
        c2 = t.bgCAS == '7732-18-5'  # must be water
        c3 = (t.PercentHFJob >= 50)&(t.PercentHFJob <= 100)  # should be at least this amount
        c4 =  t.Purpose.str.strip().str.lower().isin(self.wlst)
        slic = t[c1&c2&c3&c4][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's1'
        #print(f'Disclosure is in set: {len(slic[slic.UploadKey=="f961a561-edd3-4c9e-8b38-3ba58d2b73c9"])}')
        #print(f"Auto_set_1: new {len(slic)}, maybe_water_by_MI? {len(slic[slic.maybe_water_by_MI=='yes'])}, not kept (MIdensity out of range): {len(slic[slic.maybe_water_by_MI=='no'])}")
        #slic = slic[~(slic.maybe_water_by_MI=='no')] # don't keep those flagged disclosures
        
        return slic

    def auto_set_2(self):
        """ THis basic auto algorithm set allows more than one water record, but still restricted:
            - only include records with valid CAS numbers as water
            - sum of %HFJob for all is < upper tolerance
            - sum of water records should be >50 % (otherwise we pick up Nitrogen dominated fracks)
            Note this can still produce single record carriers if only one of 
            the identified 'carrier/base' records meets the criteria especially
            that there is more than one carrier record, but only one is water.  Set 1
            requires that there is only ONE carrier record.
        """
        
        t = self.df[self.df.is_valid_CAS].copy()
        #print(self.df.columns)
        t['has_purp'] = (t.Purpose.str.strip().str.lower().isin(self.wlst))\
                        &(t.PercentHFJob>0)  # prevent some carriers with no %HFJ from the calculation
                                             # Added 11/9/2021, after removing all previous S2 from 
        gbp = t.groupby('UploadKey',as_index=False)['has_purp'].sum() 
        gbwater = t[t.bgCAS=='7732-18-5'].groupby('UploadKey',as_index=False)\
            ['PercentHFJob'].sum().rename({'PercentHFJob':'perc_water'},axis=1)
        t = t.drop('has_purp',axis=1)
        t = pd.merge(t,gbp,on='UploadKey',how='left')
        t = pd.merge(t,gbwater,on='UploadKey',how='left')
        
        # first find each prospective record could be part of carrier
        c1 = t.has_purp>1  # requires more than one carrier in disclosure
        c2 = t.bgCAS == '7732-18-5'  # keep only water records as carrier
        c3 = t.Purpose.str.strip().str.lower().isin(self.wlst) 
        c4 = t.PercentHFJob > 0  # added 11/9/2021
        c5 = t.perc_water>=50 # added 11/15/2021
        slic = t[c1&c2&c3&c4&c5][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()

        # make sure sum percentage of slic records is not too much
        gb = slic.groupby('UploadKey',as_index=False)[['PercentHFJob']].sum()
        gb['test'] = gb.PercentHFJob<=upper_tolerance
        #print(f'Auto_set_2: detected length {len(gb)} ')
        slic = pd.merge(slic,gb[['UploadKey','test']],on='UploadKey',how='left')
        slic = slic[slic.test]
        slic = slic[slic.test].drop('test',axis=1)
                        

        slic['auto_carrier_type'] = 's2'
        return slic

    def auto_set_3(self):
        """ Set3 has three conditions:
            - CASNumber is water (7732-18-5)
            - IngredientName has the words "including mix water" (a common identifier)
            - that record is > 40% PercentHFJob 
            
            These records do not have direct indications of carrier records in
            the Purpose (which is often cluttered with multiple purposes) but
            are clearly single record water-based carriers.
        """
        
        t = self.df[self.df.is_valid_CAS].copy()
        c1 = t.IngredientName.str.contains('including mix water')
        c2 = t.bgCAS == '7732-18-5'  # must be water
        c3 = (t.PercentHFJob >= 40)&(t.PercentHFJob < 100)  # should be at least this amount
        slic = t[c1&c2&c3][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's3'
       
        return slic

    def auto_set_4(self):
        """ Set4 has four conditions:
            - CASNumber is 'MISSING'
            - IngredientName has the words "including mix water" (a common identifier)
            - that record is > 60% PercentHFJob
            - the total_percent_valid_job (including the "including mix" record) is <105%
            
            These records do not have direct indications of carrier records in
            the Purpose (which is often cluttered with multiple purposes) but
            are clearly single record water-based carriers.
        """
        precond = (self.df.CASNumber=='MISSING')&\
                (self.df.IngredientName.str.contains('including mix water'))&\
                ((self.df.PercentHFJob >= 60)&(self.df.PercentHFJob < 100))
        #print(f'Number of raw records with primary condition: {precond.sum()}')
        t = self.df[(self.df.is_valid_CAS)|precond|(self.df.bgCAS=='proprietary')].copy()
        gb = t.groupby('UploadKey',as_index=False)['PercentHFJob'].sum()\
            .rename({'PercentHFJob':'totPercent'},axis=1)
        t = pd.merge(t,gb,on='UploadKey',how='left')
        # calc total%
        cond = (t.CASNumber=='MISSING')&\
                (t.IngredientName.str.contains('including mix water'))&\
                ((t.PercentHFJob >= 60)&(t.PercentHFJob < 100))
        c1 = (t.totPercent>95) & (t.totPercent<105)
        slic = t[c1&cond][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's4'
       
        return slic

    def auto_set_5(self):
        """ This is just like set one, except that no carrier purpose is present:
            - looking only at records with valid CAS numbers
            - CASNumber is water
            - 50% < %HFJob < 100% (single 100% records not ok) 
        """
        
        t = self.df[self.df.is_valid_CAS].copy()
        t['has_purp'] = t.Purpose.str.strip().str.lower().isin(self.wlst)
        gbp = t.groupby('UploadKey',as_index=False)['has_purp'].sum()
        t = t.drop('has_purp',axis=1)
        t = pd.merge(t,gbp,on='UploadKey',how='left')
        
    
        c1 = t.has_purp==0  # no records with Purpose in wlst
        c2 = t.bgCAS == '7732-18-5'  # must be water
        c3 = (t.PercentHFJob >= 50)&(t.PercentHFJob < 100)  # should be at least this amount
        #c4 =  t.Purpose.str.strip().str.lower().isin(self.wlst)
        slic = t[c1&c2&c3][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's5'
        slic['is_new'] = True
       
        return slic

    def auto_set_6(self):
        """ Similar to set 1;
            - bgCAS is ambiguousID
            - single record with a carrier purpose
            - IngredientName is either in 'wst' list or has "water" in it
            - 50% < %HFJob < 100% (single 100% records not ok) 
        """
        
        t = self.df.copy()
        t['has_purp'] = t.Purpose.str.strip().str.lower().isin(self.wlst)
        gbp = t.groupby('UploadKey',as_index=False)['has_purp'].sum()
        t = t.drop('has_purp',axis=1)
        t = pd.merge(t,gbp,on='UploadKey',how='left')
        t.TradeName = t.TradeName.str.lower()
        t.TradeName.fillna('empty',inplace=True)
        c1 = t.has_purp==1  # only 1 record with Purpose in wlst
        c2 = t.bgCAS == 'ambiguousID'  # must be water
        c3 = (t.PercentHFJob >= 50)&(t.PercentHFJob < 100)  # should be at least this amount
        c4 =  t.Purpose.str.strip().str.lower().isin(self.wlst)
        c5 = t.IngredientName.isin(self.wlst)|t.IngredientName.str.contains('water')
        c6 = t.TradeName.isin(self.wlst)|t.TradeName.str.contains('water')
        c6 = (~(t.TradeName.str.contains('slick'))) & c6 # prevent 'slickwater' from counting as 'water'
        slic = t[c1&c2&c3&c4&c5&c6][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's6'
        
        return slic

    def auto_set_7(self):
        """ Like set_1, but for salted water:
            - looking only at records with valid CAS numbers
            - single record with a carrier purpose
            - CASNumber is either 7447-40-7 or 7647-14-5
            - 50% < %HFJob < 100% (single 100% records not ok) 
        """
        
        t = self.df[self.df.is_valid_CAS].copy()
        t['has_purp'] = t.Purpose.str.strip().str.lower().isin(self.wlst)
        gbp = t.groupby('UploadKey',as_index=False)['has_purp'].sum()
        t = t.drop('has_purp',axis=1)
        t = pd.merge(t,gbp,on='UploadKey',how='left')
    
        c1 = t.has_purp==1  # only 1 record with Purpose in wlst
        c2 = t.bgCAS.isin(['7447-40-7','7647-14-5'])  # kcl or nacl
        c3 = (t.PercentHFJob >= 50)&(t.PercentHFJob < 100)  # should be at least this amount
        c4 =  t.Purpose.str.strip().str.lower().isin(self.wlst)
        slic = t[c1&c2&c3&c4][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's7'
     
        return slic

    def auto_set_8(self):
        """ Many skytruth carriers have this profile;
            - bgCAS is ambiguousID or 7732-18-5
            - IngredientName is MISSING
            - Purpose is "unrecorded purpose"
            - TradeName has either "water" or "brine"
            - can be one or two records in each disclosure
            - 50% < sum of %HFJob < 100%  
        """
        
        t = self.df.copy()
        #gbp = t.groupby('UploadKey',as_index=False)['has_unrec_purp'].sum()
        #t = t.drop('num_unrec_purp',axis=1)
        #t = pd.merge(t,gbp,on='UploadKey',how='left')
        t.TradeName = t.TradeName.str.lower()
        t.TradeName.fillna('empty',inplace=True)
        c1 = t.Purpose == 'unrecorded purpose'
        c2 = t.bgCAS.isin(['ambiguousID','7732-18-5'])         
        c3 = t.IngredientName=='MISSING'
        c4 = t.TradeName.str.contains('water')
        c4 = (~(t.TradeName.str.contains('slick'))) & c4 # prevent 'slickwater' from counting as 'water'
        tt = t[c1&c2&c3&c4].copy()
        gb = tt.groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gb.columns = ['UploadKey','unrec_percent']
        tt = pd.merge(tt,gb,on='UploadKey',how='left')
        c5 = (tt.unrec_percent >= 50)&(tt.unrec_percent< 100)  # should be at least this amount
        slic = tt[c5][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's8'
      
        return slic

    def auto_set_9(self):
        """ Many skytruth carriers have this profile;
            - bgCAS is ambiguousID or 7732-18-5
            - IngredientName is MISSING
            - Purpose is one of the standard carrier words or phrases
            - TradeName has either "water" or "brine"
            - can be one or two records in each disclosure
            - 50% < sum of %HFJob < 100%  
        """
        
        t = self.df.copy()
        t.TradeName = t.TradeName.str.lower()
        t.TradeName.fillna('empty',inplace=True)
        c1 = t.Purpose.str.strip().str.lower().isin(self.wlst) 
        c2 = t.bgCAS.isin(['ambiguousID','7732-18-5'])         
        c3 = t.IngredientName=='MISSING'
        c4 = t.TradeName.str.contains('water')
        c4 = (~(t.TradeName.str.contains('slick'))) & c4 # prevent 'slickwater' from counting as 'water'
        tt = t[c1&c2&c3&c4].copy()
        gb = tt.groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
        gb.columns = ['UploadKey','unrec_percent']
        tt = pd.merge(tt,gb,on='UploadKey',how='left')
        c5 = (tt.unrec_percent >= 50)&(tt.unrec_percent< 100)  # should be at least this amount
        slic = tt[c5][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',#'maybe_water_by_MI','dens_test',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's9'
     
        return slic

    def auto_set_10(self):
        """ This set catches a pattern seen in later disclosures: that the carrier
            is only reported in the top part of the systems approach section under
            the "Listed Below"  CASNumber.  The actual PercentHFJob value isn't even
            reported in the PDF version, but is in the bulk download.
            - CASNumber is "Listed Below"
            - record has a carrier purpose and a percentHFJob>50 %
            - TradeName has "water" in it
        """
        
        t = self.df.copy()
        t['has_purp'] = t.Purpose.str.strip().str.lower().isin(self.wlst)
        gbp = t.groupby('UploadKey',as_index=False)['has_purp'].sum()
        t = t.drop('has_purp',axis=1)
        t = pd.merge(t,gbp,on='UploadKey',how='left')
        t.TradeName = t.TradeName.str.lower()
        t.TradeName.fillna('empty',inplace=True)
        c1 = t.CASNumber.str.lower() == 'listed below'  # must be water
        c2 = (t.PercentHFJob >= 50)&(t.PercentHFJob <= 100)  # should be at least this amount
        c3 =  t.Purpose.str.strip().str.lower().isin(self.wlst)
        c4 = t.TradeName.str.contains('water')
        slic = t[c1&c2&c3&c4][['IngredientKey','UploadKey','CASNumber',
                            'IngredientName','Purpose','TradeName',
                             'PercentHFJob','bgCAS',
                           'MassIngredient','TotalBaseWaterVolume']].copy()
        slic['auto_carrier_type'] = 's10'
        
        return slic

    def check_for_auto_disc(self):
        results = []

        res = self.auto_set_1()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 1: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_2()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 2: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_3()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 3: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_4()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 4: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_5()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 5: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_6()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 6: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_7()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 7: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_8()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 8: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_9()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 9: {len(res.UploadKey.unique()):10,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        res = self.auto_set_10()
        self.remove_disclosures(res)
        if len(res)>0:
            results.append(res)
        print(f'Auto set 10: {len(res.UploadKey.unique()):9,}, with {len(self.df.UploadKey.unique()):10,} remaining')                

        self.autodf = pd.concat(results,sort=True)
        # self.autodf.to_csv(os.path.join(self.out_dir,'carrier_list_auto.csv'),
        #                    quotechar='$',
        #                    encoding = 'utf-8',index=False)
        save_df(self.autodf,os.path.join(self.out_dir,'carrier_list_auto.parquet'))
   
        
    def save_curation_candidates(self):
        self.df = pd.merge(self.df,self.disc[['UploadKey','percSumValid','percSumAll']],
                           on='UploadKey',how='left')
        c1 = self.df.Purpose.str.strip().str.lower().isin(self.wlst)
        c2 = self.df.PercentHFJob>=5
        self.curdf = self.df[c1|c2].copy()
        #t['multi_rec'] = t.UploadKey.duplicated(keep=False)
        #t['problem_disc'] = ''
        #t['is_water_carrier'] = ''
        ukt = self.curdf.UploadKey.unique().tolist()
        
        print(f'Disclosures not caught: {len(self.curdf.UploadKey.unique())} ')
        # add blank line to make excel curation easier
        self.curdf = pd.concat([self.curdf,pd.DataFrame({'UploadKey':ukt})],sort=True)
        self.curdf = self.curdf.sort_values(['UploadKey','PercentHFJob'],ascending=False)
        self.curdf['year'] = self.curdf.date.dt.year
        # self.curdf[['UploadKey','IngredientKey','APINumber','is_valid_CAS','year',
        #             'TotalBaseWaterVolume','CASNumber','bgCAS','IngredientName',
        #             'Purpose','TradeName','PercentHFJob','percSumValid','percSumAll']]\
        #             .to_csv(os.path.join(self.out_dir,'carrier_list_NOT_CURATED.csv'),
        #                                  quotechar='$',
        #                                  encoding='utf-8',index=False)
        store_df_as_csv(self.curdf[['UploadKey','IngredientKey','APINumber','is_valid_CAS','year',
                                    'TotalBaseWaterVolume','CASNumber','bgCAS','IngredientName',
                                    'Purpose','TradeName','PercentHFJob','percSumValid','percSumAll']],
                                    
                        os.path.join(self.out_dir,'carrier_list_NOT_CURATED.csv'))
        
    def remove_disclosures(self,sourcedf):
        upk = sourcedf.UploadKey.unique().tolist()
        #print(f'Before len df = {len(self.df)}')
        self.df = self.df[~(self.df.UploadKey.isin(upk))]
        self.disc = self.disc[~(self.disc.UploadKey.isin(upk))]
        #print(f'After len df = {len(self.df)}')
        
        
    def create_full_carrier_set(self):
        # try:
            self.check_for_prob_disc()
            self.check_for_auto_disc()
            self.save_curation_candidates()
            return True
        # except:
            # return False
        
    # def process_curated_files(self):
    #     try:
    #         mod_df = pd.read_csv(os.path.join(self.ref_dir,'carrier_list_modified.csv'),
    #                              quotechar='$',encoding='utf-8',
    #                              dtype={'APINumber':'str'})
    
    #         # first process the newly curated carriers
    #         newdf = mod_df[mod_df.is_water_carrier.isin(['X','x'])][['UploadKey','IngredientKey',
    #                                                                  'APINumber','TotalBaseWaterVolume',
    #                                                                  'CASNumber','bgCAS',
    #                                                                  'IngredientName','Purpose',
    #                                                                  'TradeName','PercentHFJob',
    #                                                                  ]].copy()
    #         newdf['first_date'] = 'D:'+today_str
    #         print(f'  -- Newly curated carriers: {len(newdf.UploadKey.unique())}')
    #         self.curdf = pd.concat([self.curdf,newdf],sort=True)\
    #             [['UploadKey','IngredientKey','APINumber','TotalBaseWaterVolume',
    #               'CASNumber','bgCAS','IngredientName','Purpose',
    #               'TradeName','PercentHFJob','first_date']]
    #         self.curdf.to_csv(os.path.join(self.out_dir,'carrier_list_curated.csv'),
    #                           quotechar='$',encoding='utf-8')
    #         if self.curdf.duplicated(['UploadKey','IngredientKey']).sum()>0:
    #             print('    -- Removing duplicates (already added?)')
    #             self.curdf = self.curdf[~self.curdf.duplicated(['UploadKey','IngredientKey'])]
    #         print(f'  -- saved curated carrier disclosures: {len(self.curdf.UploadKey.unique())}')
    
    #         # now process the problem disclosures
    #         newdf = mod_df[mod_df.problem_disc.isin(['X','x'])][['UploadKey',
    #                                                              'APINumber']].copy()
    #         newdf['first_date'] = 'D:'+today_str
    #         print(f'  -- Newly curated problems: {len(newdf.UploadKey.unique())}')
    #         self.curprobdf = pd.concat([self.curprobdf,newdf],sort=True)\
    #             [['UploadKey','APINumber','first_date']]        
    #         if self.curprobdf.duplicated('UploadKey').sum()>0:
    #             print('    -- Removing duplicates (already added?)')
    #             self.curprobdf = self.curprobdf[~self.curprobdf.duplicated('UploadKey')]
    #         self.curprobdf.to_csv(os.path.join(self.out_dir,'curated_carrier_problems.csv'),
    #                           quotechar='$',encoding='utf-8')
    #         print(f'  -- saved curated problem disclosures: {len(self.curprobdf.UploadKey.unique())}')
    #         return True
    #     except:
    #         return False
                        