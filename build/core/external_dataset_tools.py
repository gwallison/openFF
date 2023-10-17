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

def add_UVCB_list(df,sources):
    print('     -- processing TSCA UVCB list')
    reffn = ext_fn(ext_dir=sources,handle='uvcb_list')
    uvcb = pd.read_csv(reffn)
    cas = uvcb.CASRN.unique().tolist()
    df['is_on_UVCB'] = df.bgCAS.isin(cas)
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
    
def add_CompTox_refs(df,sources):
    
    ctfiles = {'CWA': 'cwa_list',
               'DWSHA' : 'dwsha_list',
               'AQ_CWA': 'aq_cwa_list',
               'HH_CWA': 'hh_cwa_list',
               'IRIS': 'iris_list',
               'PFAS_list': 'pfas_list',
               # 'volatile_list': 'Chemical List VOLATILOME-2022-04-01.csv'
               }
    compreffn = 'comptox_name_list.csv'
    for lst in ctfiles.keys():
        print(f'     -- processing {lst}')
        reffn = ext_fn(ext_dir=sources,handle=ctfiles[lst])
        ctdf = pd.read_csv(reffn,low_memory=False,
                           dtype={'CASRN':'str'})
        clst= ctdf.CASRN.unique().tolist()
        df['is_on_'+lst] = df.bgCAS.isin(clst)
        
    # now add the epa ref numbers and names
    refdf = pd.read_csv(os.path.join(sources,compreffn),quotechar='$',encoding='utf-8')
    # we currently use CASRN for bgIngredientName because of duplicate synonyms
    refdf = refdf[['CASRN','epa_preferred_name',
                   'DTXSID','iupac_name']]\
            .rename({'CASRN':'bgCAS','epa_preferred_name':'epa_pref_name'},axis=1)
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
    df = add_CompTox_refs(df,sources)
    df = add_NPDWR_list(df,sources)
    df = add_Prop65_ref(df,sources)
    df = add_TEDX_ref(df,sources)
    df = add_diesel_list(df)
    df = add_UVCB_list(df,sources)
    df = add_RQ_list(df,sources)
    df = add_ChemInfo_list(df,ci_source)
    return df

#################  PADUS shape files ############################
def process_PADUS(df,sources='./sources/external_refs/',
                         outdir='./outdir/'):
    """Find joins with the PADUS database.  Note that some wells may have
    more than one join.  This routine will add the boolean fields 
       bgFederalWells and
       bgNativeWells
    as well as a csv file with more details.
    concat geopandas: https://gis.stackexchange.com/questions/162659/joining-concat-list-of-similar-dataframes-in-geopandas
    """
    print(' -- searching for wells on Fed and Native lands')
    reffn = ext_fn(ext_dir=sources,handle='padus_pkl')
    # pkl_name = os.path.join(sources,'shape_files','padus.pkl')
    out_name = os.path.join(outdir,'PADUS_hits.csv')
    try:
        shdf = pd.read_pickle(reffn)
    except:
        print('  -- fetch PADUS from zip files')
        allshp = []
        # shp_fn = r"C:\MyDocs\OpenFF\data\external_refs\shape_files\PADUS3_0_Region_7_SHP.zip!PADUS3_0Combined_Region7.shp"
        for i in range(1,12):
            print(f'     PADUS {i} file processed')
            shp_fn = os.path.join(sources,'shape_files',
                                  f'PADUS3_0_Region_{i}_SHP.zip!PADUS3_0Combined_Region{i}.shp')
            shpdf = geopandas.read_file(shp_fn).to_crs(final_crs)
            allshp.append(shpdf)
    
        shdf = geopandas.GeoDataFrame(pd.concat(allshp,
                                                ignore_index=True), 
                                      crs=allshp[0].crs)
        shdf.to_pickle(reffn)
    
    t = df.groupby('UploadKey',as_index=False)[['bgLatitude','bgLongitude',
                                            'bgStateName','APINumber']].first()
    gdf = geopandas.GeoDataFrame(t,
                                 geometry= geopandas.points_from_xy(t.bgLongitude, 
                                                                    t.bgLatitude,
                                                                    crs=final_crs))

    hits = geopandas.sjoin(gdf,shdf,how='left')  
    fed = hits[hits.Own_Type=='FED'].UploadKey.unique().tolist()
    stat = hits[hits.Own_Type=='STAT'].UploadKey.unique().tolist()
    nat = hits[(hits.Mang_Type=='TRIB') | (hits.Des_Tp=='TRIBL')].UploadKey.unique().tolist()
    hits['bgFederalLand'] = hits.UploadKey.isin(fed)
    hits['bgStateLand'] = hits.UploadKey.isin(stat)
    hits['bgNativeAmericanLand'] = hits.UploadKey.isin(nat)
    df['bgFederalLand'] = df.UploadKey.isin(fed)
    df['bgStateLand'] = df.UploadKey.isin(stat)
    df['bgNativeAmericanLand'] = df.UploadKey.isin(nat)
    hits[hits.index_right.notna()].to_csv(out_name,quotechar='$',
                                          encoding='utf-8')
    return df