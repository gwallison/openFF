# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 09:32:29 2019

@author: Gary
"""
import pandas as pd
# import numpy as np
import os
import geopandas
from openFF.common.file_handlers import get_df, ext_fn

final_crs = 4326 # EPSG value for bgLat/bgLon; 4326 for WGS84: Google maps

    
def add_TEDX_ref(df,sources):
    #print('Adding TEDX link to CAS table')
    reffn = ext_fn(ext_dir=sources,handle='tedx_list')
    tedxdf = pd.read_excel(reffn)
    tedx_cas = tedxdf.CAS_Num.unique().tolist()
    df['is_on_TEDX'] = df.bgCAS.isin(tedx_cas)
    return df
    
def add_Prop65_ref(df,sources):
    reffn = ext_fn(ext_dir=sources,handle='prop65_list')
    p65df = pd.read_csv(reffn,encoding='iso-8859-1')
    p65_cas = p65df['CAS No.'].unique().tolist()
    df['is_on_prop65'] = df.bgCAS.isin(p65_cas)
    return df

def add_diesel_list(df):
    print('     -- processing epa diesel list')
    cas = ['68334-30-5','68476-34-6','68476-30-2','68476-31-3','8008-20-6']
    df['is_on_diesel'] = df.bgCAS.isin(cas)
    return df

def add_Elsner_list(df,sources):
    print('     -- processing Elsner and Hoelzer list')
    reffn = ext_fn(ext_dir=sources,handle='eh_master_list')
    ehdf = pd.read_csv(reffn,quotechar='$')
    ehdf = ehdf[['eh_Class_L1', 'eh_Class_L2','eh_CAS',
                 'eh_subs_class','eh_function']]
    ehdf = ehdf.rename({'eh_CAS':'bgCAS'},axis=1)
    
    df = pd.merge(df,ehdf,on='bgCAS',how='left')
    df[['eh_Class_L1', 'eh_Class_L2',
       'eh_subs_class','eh_function']] = df[['eh_Class_L1', 
                                             'eh_Class_L2',
                                             'eh_subs_class',
                                             'eh_function']].fillna('') 

    return df
    
    
# def add_UVCB_list(df,sources):
#     print('     -- processing TSCA UVCB list')
#     reffn = ext_fn(ext_dir=sources,handle='uvcb_list')
#     uvcb = pd.read_csv(reffn)
#     cas = uvcb.CASRN.unique().tolist()
#     df['is_on_UVCB'] = df.bgCAS.isin(cas)
#     return df

def add_TSCA_list(df,sources):
    print('     -- processing TSCA list')
    reffn = ext_fn(ext_dir=sources,handle='tsca_list')
    tsca = pd.read_csv(reffn)
    # first get uvcbs
    cas = tsca[tsca.UVCB=='UVCB'].CASRN.unique().tolist()
    df['is_on_UVCB'] = df.bgCAS.isin(cas)
    
    # create is_on_TSCA flag
    cas = tsca.CASRN.unique().tolist()
    df['is_on_TSCA'] = df.bgCAS.isin(cas)
    
    # next get_commercial activity status
    tsca['bgCAS'] = tsca.CASRN
    df = df.merge(tsca[['bgCAS','ACTIVITY']],on='bgCAS',how='left')
    df = df.rename({'ACTIVITY':'commercial_status'},axis=1)
    df.commercial_status = df.commercial_status.fillna('not on TSCA list')

    # get EPA regulatory flags
    df = df.merge(tsca[['bgCAS','FLAG']],on='bgCAS',how='left')
    df = df.rename({'FLAG':'epa_reg_flag'},axis=1)
    df.epa_reg_flag = df.epa_reg_flag.fillna(' ')
    
    # get TSCA DEF (chem subs definition)
    df = df.merge(tsca[['bgCAS','DEF']],on='bgCAS',how='left')
    df = df.rename({'DEF':'tsca_chem_definition'},axis=1)
    
    return df

def add_NPDWR_list(df,sources):
    # add list curated by Angelica
    print('     -- processing NPDWR list')
    reffn = ext_fn(ext_dir=sources,handle='npdwr_list')
    npdwr = pd.read_csv(reffn)
    cas = npdwr[npdwr.CASRN.notna()].CASRN.unique().tolist()
    df['is_on_NPDWR'] = df.bgCAS.isin(cas)
    return df

def add_RQ_list(df,sources):
    # variable added to some bgCAS is 'rq_lbs'
    print('     -- processing Reportable Quantity list')
    reffn = ext_fn(ext_dir=sources,handle='rq_list')
    rq = pd.read_csv(reffn,quotechar='$',encoding='utf-8')
    df = pd.merge(df,rq,on='bgCAS',how='left')
    return df

def add_PFAS_lists(df,sources):
    # need to concatenate to lists, PFASDEV and PFASSTRUCT
    print('     -- processing EPA PFAS lists')
    # first the STRUCT list
    reffn = ext_fn(ext_dir=sources,handle='pfasstruct_list')
    pfasstruct = pd.read_csv(reffn)
    cas1 = pfasstruct[pfasstruct.CASRN.notna()].CASRN.unique().tolist()
    
    # next the DEV list (has non-cas ids)
    reffn = ext_fn(ext_dir=sources,handle='pfasdev_list')
    pfasdev = pd.read_csv(reffn)
    cas2 = pfasdev[pfasdev.CASRN.notna()].CASRN.unique().tolist()
    allcas = cas1+cas2
    df['is_on_PFAS_list'] = df.bgCAS.isin(allcas)
    return df
    
    
def add_CompTox_refs(df,sources,ci_source):
    
    ctfiles = {'CWA': 'cwa_list',
               'DWSHA' : 'dwsha_list',
               'AQ_CWA': 'aq_cwa_list',
               'HH_CWA': 'hh_cwa_list',
               'IRIS': 'iris_list',
               # 'PFAS_list': 'pfas_list',
               # 'volatile_list': 'Chemical List VOLATILOME-2022-04-01.csv'
               }
    # compreffn = 'comptox_name_list.csv'
    compreffn = 'master_cas_number_list.parquet'
    for lst in ctfiles.keys():
        print(f'     -- processing {lst}')
        reffn = ext_fn(ext_dir=sources,handle=ctfiles[lst])
        ctdf = pd.read_csv(reffn,low_memory=False,
                           dtype={'CASRN':'str'})
        clst= ctdf.CASRN.unique().tolist()
        df['is_on_'+lst] = df.bgCAS.isin(clst)
        
    df = add_PFAS_lists(df, sources)
        
    # now add the epa ref numbers and names
    # refdf = pd.read_csv(os.path.join(sources,compreffn),quotechar='$',encoding='utf-8')
    refdf = pd.read_parquet(os.path.join(ci_source,compreffn))
    # we currently use CASRN for bgIngredientName because of duplicate synonyms
    refdf = refdf[['cas_number','epa_preferred_name',
                   'DTXSID','iupac_name']]\
            .rename({'cas_number':'bgCAS','epa_preferred_name':'epa_pref_name'},axis=1)
    refdf = refdf[~refdf.bgCAS.duplicated()] # get rid of double callouts
    df = pd.merge(df,refdf[['bgCAS','DTXSID','epa_pref_name','iupac_name']],
                  how='left',on='bgCAS')
    return df
 
def add_ChemInfo_list(df,ci_source):
    print('     -- processing ChemInformatics list')
    cidf = get_df(os.path.join(ci_source,'CI_sdf_summary.parquet'))
    caslst = cidf.CAS.unique().tolist()
    df['chemInfo_available'] = df.bgCAS.isin([caslst])
    return df
    
    
def add_all_bgCAS_tables(df,sources,ci_source):
    df = add_CompTox_refs(df,sources,ci_source)
    df = add_NPDWR_list(df,sources)
    df = add_Prop65_ref(df,sources)
    df = add_TEDX_ref(df,sources)
    df = add_diesel_list(df)
    df = add_TSCA_list(df,sources)
    df = add_RQ_list(df,sources)
    df = add_ChemInfo_list(df,ci_source)
    df = add_Elsner_list(df, sources)
    return df

#################  PADUS shape files ############################
# def process_PADUS(df,sources='./sources/external_refs/',
#                          outdir='./outdir/'):
#     """Find joins with the PADUS database.  Note that some wells may have
#     more than one join.  This routine will add the boolean fields 
#        bgFederalWells and
#        bgNativeWells
#     as well as a csv file with more details.
#     concat geopandas: https://gis.stackexchange.com/questions/162659/joining-concat-list-of-similar-dataframes-in-geopandas
#     """
#     print(' -- searching for wells on Fed and Native lands')
#     reffn = ext_fn(ext_dir=sources,handle='padus_pkl')
#     # pkl_name = os.path.join(sources,'shape_files','padus.pkl')
#     out_name = os.path.join(outdir,'PADUS_hits.csv')
#     try:
#         shdf = pd.read_pickle(reffn)
#     except:
#         print('  -- fetch PADUS from zip files')
#         allshp = []
#         # shp_fn = r"C:\MyDocs\OpenFF\data\external_refs\shape_files\PADUS3_0_Region_7_SHP.zip!PADUS3_0Combined_Region7.shp"
#         for i in range(1,12):
#             print(f'     PADUS {i} file processed')
#             shp_fn = os.path.join(sources,'shape_files',
#                                   f'PADUS3_0_Region_{i}_SHP.zip!PADUS3_0Combined_Region{i}.shp')
#             shpdf = geopandas.read_file(shp_fn).to_crs(final_crs)
#             allshp.append(shpdf)
    
#         shdf = geopandas.GeoDataFrame(pd.concat(allshp,
#                                                 ignore_index=True), 
#                                       crs=allshp[0].crs)
#         shdf.to_pickle(reffn)
    
#     t = df.groupby('DisclosureId',as_index=False)[['bgLatitude','bgLongitude',
#                                             'bgStateName','APINumber']].first()
#     gdf = geopandas.GeoDataFrame(t,
#                                  geometry= geopandas.points_from_xy(t.bgLongitude, 
#                                                                     t.bgLatitude,
#                                                                     crs=final_crs))

#     hits = geopandas.sjoin(gdf,shdf,how='left')  
#     fed = hits[hits.Own_Type=='FED'].DisclosureId.unique().tolist()
#     stat = hits[hits.Own_Type=='STAT'].DisclosureId.unique().tolist()
#     nat = hits[(hits.Mang_Type=='TRIB') | (hits.Des_Tp=='TRIBL')].DisclosureId.unique().tolist()
#     hits['bgFederalLand'] = hits.DisclosureId.isin(fed)
#     hits['bgStateLand'] = hits.DisclosureId.isin(stat)
#     hits['bgNativeAmericanLand'] = hits.DisclosureId.isin(nat)
#     df['bgFederalLand'] = df.DisclosureId.isin(fed)
#     df['bgStateLand'] = df.DisclosureId.isin(stat)
#     df['bgNativeAmericanLand'] = df.DisclosureId.isin(nat)
#     hits[hits.index_right.notna()].to_csv(out_name,quotechar='$',
#                                           encoding='utf-8')
#     return df