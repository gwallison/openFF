# -*- coding: utf-8 -*-
"""
Created on Thu May  6 21:26:21 2021

@author: Gary
"""
import pandas as pd
import numpy as np

large_perc_value = 50
lower_perc_tolerance = 95
upper_perc_tolerance = 105
massComp_upper_limit = 0.1


# def rec_has_it(rec,place):
#     if 'within_total_tolerance' in list(rec.columns):
#         print(f'rec_df has "wi_tot_tol" at <{place}>')

def calc_overall_percentages(rec_df,disc_df):
    # valid CAS here must include proprietary and carriers because they should be included in valid
    # percentages.

    rec_df['is_valid_cas'] = rec_df.bgCAS.str[0].isin(['0','1','2','3','4',
                                                       '5','6','7','8','9'])
    rec_df.is_valid_cas = np.where(rec_df.bgCAS.isin(['proprietary','conflictingID']),
                                                     True,rec_df.is_valid_cas)

    valid = rec_df[rec_df.is_valid_cas|rec_df.is_water_carrier]\
        .groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
    valid.columns = ['UploadKey','total_percent_of_valid']
    c1 = valid.total_percent_of_valid>lower_perc_tolerance
    c2 = valid.total_percent_of_valid<upper_perc_tolerance
    valid['within_total_tolerance'] =c2&c1
    if 'within_total_tolerance' in disc_df.columns:
        disc_df = disc_df.drop(['within_total_tolerance'],axis=1)
    
    allrecs = rec_df.groupby('UploadKey',as_index=False)['PercentHFJob'].sum()
    allrecs.columns = ['UploadKey','total_percent_all_records']
    disc_df = pd.merge(disc_df,valid,on='UploadKey',how='left')
    disc_df = pd.merge(disc_df,allrecs,on='UploadKey',how='left')
    # make sure disclosures without chem records are also marked as out of tolerance
    disc_df.within_total_tolerance = disc_df.within_total_tolerance.fillna(False) 
    
    return disc_df

def calc_MI_values(rec_df,disc_df):
    """This calculates the carrier density based on the MassIngredient mass
    and TotalBaseWaterVolume as well as some other values
    """
    
    max_dev = 0.20 # MI within disclosure inconsistency too high.
    too_small = 0 # anything this size or smaller is disregarded. 0 is especially a problem
    # rec_has_it(rec_df, '2')
    
    rec_df['job_mass_MI'] = rec_df.MassIngredient/rec_df.PercentHFJob
    rec_df.job_mass_MI = np.where(rec_df.MassIngredient>too_small,
                                  rec_df.job_mass_MI,
                                  np.NaN)
    # must also remove records with a 0 for PercentHFJ, otherwise
    # creates a condition where denominator is infinite and therefore NOT inconsistent!
    # April, 2022
    rec_df.job_mass_MI = np.where(rec_df.PercentHFJob>0,
                                  rec_df.job_mass_MI,
                                  np.NaN)
    
    
    # Look for inconsistencies in MassIngredient at the disclosure level,
    #   generate cleanMI
    gb = rec_df.groupby('UploadKey',as_index=False)['job_mass_MI'].agg(['max','min'])
    gb['frac_dev'] = (gb['max']-gb['min'])/gb['max']
    gb['MI_inconsistent'] = gb.frac_dev>max_dev
    gb = gb.reset_index() # collapse multilevel index
    disc_df = pd.merge(disc_df,
                       gb[['UploadKey','MI_inconsistent']],on='UploadKey',
                       how='left',validate='1:1')
    rec_df = pd.merge(rec_df,disc_df[['UploadKey','MI_inconsistent']],
                  on='UploadKey',how='left')
    rec_df['cleanMI'] = np.where(rec_df.MI_inconsistent,np.NaN,rec_df.MassIngredient)
    rec_df = rec_df.drop('MI_inconsistent',axis=1)

    gb2 = rec_df[rec_df.is_water_carrier].groupby('UploadKey',as_index=False)[['PercentHFJob','MassIngredient']].sum()
    gb2.columns = ['UploadKey','carrier_percent','carrier_mass_MI']
    disc_df = pd.merge(disc_df,
                       gb2,on='UploadKey',
                       how='left',validate='1:1')
    gb3 = rec_df[rec_df.is_water_carrier].groupby('UploadKey',as_index=False)['density_from_comment'].mean()
    gb3.columns = ['UploadKey','carrier_density_from_comment']
    disc_df = pd.merge(disc_df,
                       gb3,on='UploadKey',
                       how='left',validate='1:1')
    
    disc_df['carrier_density_MI'] = np.where(disc_df.within_total_tolerance & (~disc_df.MI_inconsistent),
                                             disc_df.carrier_mass_MI/disc_df.TotalBaseWaterVolume,
                                             np.NaN)
    disc_df['bgDensity'] = np.where(disc_df.carrier_density_from_comment>7,
                                    disc_df.carrier_density_from_comment,
                                    8.34)
    disc_df['bgDensity_source'] = np.where(disc_df.carrier_density_from_comment>7,
                                    'from_comment',
                                    'default')
    # rec_has_it(rec_df, '2a')

    return rec_df, disc_df
    
    
def prep_datasets(rec_df,disc_df):
    #print(f'in prep: {len(disc_df)}')
    disc_df['has_TBWV'] = disc_df.TotalBaseWaterVolume>0
    disc_df = calc_overall_percentages(rec_df, disc_df)
    #upk = disc_df[disc_df.within_total_tolerance].UploadKey.unique().tolist()
    #rec_df['large_percent_rec'] = rec_df.PercentHFJob>large_perc_value
    #rec_df['is_water_carrier'] = rec_df.large_percent_rec & \
    #                             (rec_df.bgCAS=='7732-18-5') &\
    #                             ~(rec_df.dup_rec) 
    #hasWC = rec_df[rec_df.is_water_carrier].UploadKey.unique().tolist()
    #disc_df['has_water_carrier'] = disc_df.UploadKey.isin(hasWC)
    #rec_df.is_water_carrier= rec_df.is_water_carrier & rec_df.UploadKey.isin(upk)
    # rec_has_it(rec_df, '3')
    
    return rec_df,disc_df                             
     


def calc_mass(rec_df,disc_df):
    #print(disc_df.columns)
    # rec_has_it(rec_df, '4')
    
    rec_df,disc_df = calc_MI_values(rec_df, disc_df)
    #upk = disc_df[disc_df.within_total_tolerance].UploadKey.unique().tolist()
    #cond = rec_df.UploadKey.isin(upk)                             

    # because we are dependent on 50% and within tolerance, we
    # don't merge for those disclosures out of tolerance, too many multiple 50%'ers. 

# =============================================================================
#     cond = disc_df.within_total_tolerance&disc_df.has_TBWV
#     disc_df.carrier_percent = np.where(cond,
#                                        disc_df.carrier_percent,
#                                        np.NaN)    
# =============================================================================
    disc_df['carrier_mass'] = disc_df.TotalBaseWaterVolume * disc_df.bgDensity
    disc_df['job_mass'] = disc_df.carrier_mass/(disc_df.carrier_percent/100)
    
    rec_df = pd.merge(rec_df,disc_df[['UploadKey','job_mass']],
                      on='UploadKey',how='left',validate='m:1')
    rec_df['calcMass'] = (rec_df.PercentHFJob/100)*rec_df.job_mass

    # a calcMass of ZERO is a non-disclosure, so set to NaN (added Dec 2021)
    rec_df.calcMass = np.where(rec_df.calcMass==0,np.NaN,rec_df.calcMass)
    rec_df = rec_df.drop('job_mass',axis=1)
    
    rec_df = calc_massComp(rec_df,disc_df)
    
    return rec_df,disc_df


def calc_massComp(rec_df,disc_df):
    c1 = rec_df.calcMass>2
    c2 = rec_df.cleanMI>2 

    #df['MI_larger'] = df.MassIngredient>df.calcMass
    #c3 = df.MI_larger
    sp = ' '*10
    rec_df['massComp'] = ((rec_df[c1&c2].calcMass - rec_df[c1&c2].cleanMI).abs())/rec_df[c1&c2].calcMass
    print(f'{sp}Number of disclosures with inconsistent MI:        {len(disc_df[disc_df.MI_inconsistent]):,}')
    print(f'{sp}Number of records with both calcMass and cleanMI: {len(rec_df[rec_df.massComp.notna()]):,}')
    print(f'{sp}   Number of disclosures with both: {len(rec_df[rec_df.massComp.notna()].UploadKey.unique()):,}')
    print(f'{sp}Number where only calcMass is non-zero:             {len(rec_df[c1&~(c2)]):,}')
    print(f'{sp}Number where only cleanMI is non-zero:              {len(rec_df[~(c1)&(c2)]):,}')

    rec_df['massCompFlag'] = rec_df.massComp>massComp_upper_limit
    print(f'{sp}Number calcMass values rejected by massComp: {rec_df.massCompFlag.sum():,}')
    rec_df.calcMass = np.where(rec_df.massCompFlag,np.NaN,rec_df.calcMass)
    #rec_df = rec_df.drop('MI_inconsistent',axis=1)
    return rec_df