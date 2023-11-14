# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 16:43:00 2023

@author: garya
"""
import pandas as pd
import numpy as np
# from intg_support.common import round_sig, getCatLink, getPubChemLink, getDataLink, getCompToxRef
from openFF.common.text_handlers import getFingerprintImg

def make_chem_single_disclosure(rec_table,cas_table,
                                 show_dup_recs=True,
                                 removeCAS=[],showOnlyCAS=[],
                                 ):
    """This is for the display of a single disclosure. Records are not collapsed to one/CASRN."""
    assert len(rec_table.UploadKey.unique()) == 1, 'More than one disclosure not allowed!'

    # filters
    if not show_dup_recs: rec_table = rec_table[~rec_table.dup_rec]
    if removeCAS: rec_table = rec_table[~rec_table.bgCAS.isin(removeCAS)]
    if showOnlyCAS: rec_table = rec_table[rec_table.bgCAS.isin(showOnlyCAS)]
    cas_table.fillna('--',inplace=True)
    chem_df = pd.merge(rec_table,cas_table,on='bgCAS',how='left')


    chem_df['CASRN'] = chem_df.bgCAS+'<br><em>('+chem_df.CASNumber+')</em>'
    chem_df['name'] = chem_df.epa_pref_name+'<br><em>('+chem_df.IngredientName+')</em>'
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

    chem_df['Hazard fingerprint'] = chem_df.bgCAS.map(lambda x: getFingerprintImg(x))

    chem_df.TradeName = '<em>'+chem_df.TradeName+'</em>'
    chem_df.Supplier = '<em>'+chem_df.Supplier+'</em>'
    # chem_df.PercentHFJob = '<em>'+chem_df.PercentHFJob+'</em>'

    return chem_df[['TradeName','Supplier','CASRN','name','PercentHFJob',
                    'calcMass','extrnl','Hazard fingerprint','is_water_carrier','dup_rec']]


# def make_chem_summary(df_cas):
#     chem_df = df_cas.groupby('bgCAS',as_index=False)[['UploadKey']].count()
#     chem_df = chem_df.rename({'UploadKey':'numRecords'},axis=1)
#     gb1 = df_cas[df_cas.in_std_filtered].groupby('bgCAS',as_index=False)[['UploadKey']].count()
#     chem_df = pd.merge(chem_df,gb1,on='bgCAS',how='left')
#     chem_df.fillna(0,inplace=True)
#     chem_df.numRecords = chem_df.UploadKey.astype('int').astype('str')+ '<br>'+ chem_df.numRecords.astype('str')
#     t = df_cas[(df_cas.calcMass>0)&(df_cas.in_std_filtered)].groupby('bgCAS',as_index=False)[['UploadKey']].count()
#     t = t.rename({'UploadKey':'numWithMass'},axis=1)
    
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
#     chem_df.numWithMass.fillna(0,inplace=True)
    
#     t = df_cas.groupby('bgCAS')[['bgIngredientName','is_on_TEDX','is_on_prop65',#'is_on_CWA_priority',
#                                  'is_on_CWA','is_on_DWSHA','is_on_PFAS_list','is_on_volatile_list',
#                                  'is_on_UVCB','is_on_diesel','is_on_AQ_CWA','is_on_HH_CWA','is_on_IRIS',
#                                  'is_on_NPDWR','rq_lbs',
#                                  'DTXSID']].first()
#     #t.rq_lbs = t.rq_lbs.map(lambda x: round_sig(x,2))
#     t.rq_lbs.fillna('  ',inplace=True)
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
    
#     t = df_cas[(df_cas.calcMass>0)&(df_cas.in_std_filtered)].groupby('bgCAS',as_index=False)['calcMass'].sum()
#     t.calcMass = t.calcMass.map(lambda x: round_sig(x,3))
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
#     chem_df.calcMass.fillna(0,inplace=True)
    
#     #chem_df['Filtered Data'] = chem_df.bgCAS.map(lambda x: getDataLink(x))
#     chem_df['History'] = chem_df.bgCAS.map(lambda x: getCatLink(x,x,use_remote=True))
#     chem_df['ChemID'] = chem_df.bgCAS.map(lambda x: getPubChemLink(x)) # Now through PubChem instead of ChemID
#     chem_df['EPA_ref'] = chem_df.DTXSID.map(lambda x: getCompToxRef(x))
    
#     #chem_df['molecule'] = chem_df.bgCAS.map(lambda x: getMoleculeImg(x))
#     #chem_df.molecule = chem_df.molecule # ?! why is this here?
#     chem_df['fingerprint'] = chem_df.bgCAS.map(lambda x: getFingerprintImg(x))
    
#     #opt.classes = ['display','cell-border']
#     chem_df.bgIngredientName.fillna('non CAS',inplace=True)
#     chem_df['names'] = chem_df.bgIngredientName 
#     chem_df['just_cas'] = chem_df.bgCAS
#     chem_df.bgCAS = '<center><h3>'+chem_df.History+'</h3>'+chem_df.names+'</center>'
#     chem_df['ref'] = chem_df.ChemID+'<br>'+chem_df.EPA_ref
    
#     chem_df['extrnl'] = np.where(chem_df.is_on_CWA,'CWA; ','')
#     chem_df.extrnl = np.where(chem_df.is_on_AQ_CWA,chem_df.extrnl+'AQ_CWA; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_HH_CWA,chem_df.extrnl+'HH_CWA; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_NPDWR,chem_df.extrnl+'NPDWR; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_DWSHA,chem_df.extrnl+'DWSHA; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_TEDX,chem_df.extrnl+'TEDX; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_prop65,chem_df.extrnl+'prop65; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_PFAS_list,chem_df.extrnl+'EPA_PFAS; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_volatile_list,chem_df.extrnl+'EPA_volatile; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_UVCB,chem_df.extrnl+'UVCB; ',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_diesel,chem_df.extrnl+'diesel; ',chem_df.extrnl)
#     #chem_df.extrnl = np.where(chem_df.is_on_IRIS,chem_df.extrnl+'IRIS; ',chem_df.extrnl)
    
#     t = df_cas.groupby('bgCAS',as_index=False)['date'].min().rename({'date':'earliest_date',
#                                                                      'bgCAS':'just_cas'},axis=1)
#     chem_df = pd.merge(chem_df,t,on='just_cas',how='left')
#     chem_df = chem_df[['bgCAS','ref',#'molecule',#'names',
#                        #'bgIngredientName','comm_name',
#                        'numRecords','numWithMass','calcMass',
#                        'rq_lbs','fingerprint','extrnl']].sort_values('numWithMass',ascending=False)
#     chem_df = chem_df.rename({'bgCAS':'Material',#'bgIngredientName':'Name',# 'comm_name':'Common Name',
#                               'numRecords':'total num records',
#                               'numWithMass':'num records with mass','calcMass':'Total mass used (lbs)',
#                               'extrnl':'on external lists',
#                               'rq_lbs':'Reportable quant (lbs)'},
#                               #'is_on_TEDX':'on TEDX list','is_on_prop65':'on Prop 65 list',
#                               #'is_on_CWA_SDWA':'on CWA SDWA lists',
#                               #'is_on_PFAS_list':'is PFAS or precursor','is_on_volatile_list':'on EPA volatile list'},
#                               #'eh_Class_L1':'eh Class lvl 1','eh_Class_L2':'eh Class lvl 2'},
#                              axis=1)    
#     return chem_df

# def make_compact_chem_summary(df_cas,removeCAS=['ambiguousID','sysAppMeta','conflictingID']):

#     df_cas = df_cas[~df_cas.bgCAS.isin(removeCAS)]
    
#     chem_df = df_cas.groupby('bgCAS',as_index=False)[['UploadKey']].count()
#     chem_df = chem_df.rename({'UploadKey':'numRecords'},axis=1)
#     gb1 = df_cas[df_cas.in_std_filtered].groupby('bgCAS',as_index=False)[['UploadKey']].count()
#     chem_df = pd.merge(chem_df,gb1,on='bgCAS',how='left')
#     chem_df.fillna(0,inplace=True)
#     chem_df.numRecords = chem_df.UploadKey.astype('int').astype('str') #+ '<br>'+ chem_df.numRecords.astype('str')
#     t = df_cas[(df_cas.calcMass>0)&(df_cas.in_std_filtered)].groupby('bgCAS',as_index=False)[['UploadKey']].count()
#     t = t.rename({'UploadKey':'numWithMass'},axis=1)
    
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
#     chem_df.numWithMass.fillna(0,inplace=True)
    
#     t = df_cas.groupby('bgCAS')[['bgIngredientName','is_on_TEDX','is_on_prop65',#'is_on_CWA_priority',
#                                  'is_on_CWA','is_on_DWSHA','is_on_PFAS_list','is_on_volatile_list',
#                                  'is_on_UVCB','is_on_diesel','is_on_AQ_CWA','is_on_HH_CWA','is_on_IRIS',
#                                  'is_on_NPDWR','rq_lbs',
#                                  'DTXSID']].first()
#     #t.rq_lbs = t.rq_lbs.map(lambda x: round_sig(x,2))
#     #t.rq_lbs.fillna('  ',inplace=True)
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
    
#     t = df_cas[(df_cas.calcMass>0)&(df_cas.in_std_filtered)].groupby('bgCAS',as_index=False)['calcMass'].sum()
#     t.calcMass = t.calcMass.map(lambda x: round_sig(x,3))
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
#     chem_df.calcMass.fillna(0,inplace=True)
    
#     #chem_df['Filtered Data'] = chem_df.bgCAS.map(lambda x: getDataLink(x))
#     chem_df['History'] = chem_df.bgCAS.map(lambda x: getCatLink(x,x,use_remote=True))
#     chem_df['ChemID'] = chem_df.bgCAS.map(lambda x: getPubChemLink(x)) # Now through PubChem instead of ChemID
#     chem_df['EPA_ref'] = chem_df.DTXSID.map(lambda x: getCompToxRef(x))
    
#     #chem_df['molecule'] = chem_df.bgCAS.map(lambda x: getMoleculeImg(x))
#     #chem_df.molecule = chem_df.molecule # ?! why is this here?
#     chem_df['fingerprint'] = chem_df.bgCAS.map(lambda x: getFingerprintStatus(x))
    
#     #opt.classes = ['display','cell-border']
#     chem_df.bgIngredientName.fillna('non CAS',inplace=True)
#     chem_df['names'] = chem_df.bgIngredientName 
#     chem_df['just_cas'] = chem_df.bgCAS
#     chem_df.bgCAS = '<center><h3>'+chem_df.History+'</h3>'+chem_df.names+'</center>'
#     chem_df['ref'] = chem_df.ChemID+'<br>'+chem_df.EPA_ref
    
#     chem_df['extrnl'] = np.where(chem_df.is_on_CWA,'CWA<br>','    ')
#     chem_df.extrnl = np.where(chem_df.is_on_AQ_CWA,chem_df.extrnl+'AQ_CWA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_HH_CWA,chem_df.extrnl+'HH_CWA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_NPDWR,chem_df.extrnl+'NPDWR<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_DWSHA,chem_df.extrnl+'DWSHA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_TEDX,chem_df.extrnl+'TEDX<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_prop65,chem_df.extrnl+'prop65<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_PFAS_list,chem_df.extrnl+'EPA_PFAS<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_volatile_list,chem_df.extrnl+'EPA_volatile<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_UVCB,chem_df.extrnl+'UVCB<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_diesel,chem_df.extrnl+'diesel<br>',chem_df.extrnl)
#     chem_df.extrnl = '<p style="color:green;font-size:105%;text-align:center;background-color:lightgrey;">'+chem_df.extrnl.str[:-4]+'</p>'
#     #chem_df.extrnl = np.where(chem_df.is_on_IRIS,chem_df.extrnl+'IRIS; ',chem_df.extrnl)
    
#     t = df_cas.groupby('bgCAS',as_index=False)['date'].min().rename({'date':'earliest_date',
#                                                                      'bgCAS':'just_cas'},axis=1)
#     chem_df = pd.merge(chem_df,t,on='just_cas',how='left')
#     chem_df = chem_df[['bgCAS',#'molecule',#'names',
#                        #'bgIngredientName','comm_name',
#                        'numRecords','numWithMass','calcMass',
#                        'extrnl','fingerprint','ref']].sort_values('numWithMass',ascending=False)
#     chem_df = chem_df.rename({'bgCAS':'Material',#'bgIngredientName':'Name',# 'comm_name':'Common Name',
#                               'numRecords':'Total\nnumber of records',
#                               'numWithMass':'Number of records with mass','calcMass':'Total mass used (lbs)',
#                               'extrnl':'Lists of Chemicals of Concern',
#                              'fingerprint':'ChemInformatics'},
#                              axis=1)    
#     return chem_df