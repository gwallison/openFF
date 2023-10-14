# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 09:32:29 2019

@author: Gary
"""
import pandas as pd
import numpy as np
import os
import geopandas
final_crs = 4326 # EPSG value for bgLat/bgLon; 4326 for WGS84: Google maps


    
def add_TEDX_ref(df,sources='./sources/',
                 tedx_fn = 'TEDX_EDC_trimmed.xls'):
    #print('Adding TEDX link to CAS table')
    tedxdf = pd.read_excel(os.path.join(sources,tedx_fn))
    tedx_cas = tedxdf.CAS_Num.unique().tolist()
    df['is_on_TEDX'] = df.bgCAS.isin(tedx_cas)
    return df
    
def add_Prop65_ref(df,sources='./sources/',
                 p65_fn = 'p65list12182020.csv'):
    #print('Adding California Prop 65 to CAS table')
    p65df = pd.read_csv(os.path.join(sources,p65_fn),encoding='iso-8859-1')
    p65_cas = p65df['CAS No.'].unique().tolist()
    df['is_on_prop65'] = df.bgCAS.isin(p65_cas)
    return df

def add_diesel_list(df):
    print('     -- processing epa diesel list')
    cas = ['68334-30-5','68476-34-6','68476-30-2','68476-31-3','8008-20-6']
    df['is_on_diesel'] = df.bgCAS.isin(cas)
    return df

def add_UVCB_list(df,sources='./sources/'):
    print('     -- processing TSCA UVCB list')
    uvcb = pd.read_csv(os.path.join(sources,'TSCA_UVCB_202202.csv'))
    cas = uvcb.CASRN.unique().tolist()
    df['is_on_UVCB'] = df.bgCAS.isin(cas)
    return df

def add_NPDWR_list(df,sources='./sources/'):
    # add list curated by Angelica
    print('     -- processing NPDWR list')
    npdwr = pd.read_csv(os.path.join(sources,'NationalPrimaryDrinkingWaterRegulations_machine_readable_NOV2022.csv'))
    cas = npdwr[npdwr.CASRN.notna()].CASRN.unique().tolist()
    df['is_on_NPDWR'] = df.bgCAS.isin(cas)
    return df

def add_RQ_list(df,sources='./sources/'):
    # variable added to some bgCAS is 'rq_lbs'
    print('     -- processing Reportable Quantity list')
    rq = pd.read_csv(os.path.join(sources,'RQ_final.csv'),quotechar='$',encoding='utf-8')
    df = pd.merge(df,rq,on='bgCAS',how='left')
    return df
    
def add_CompTox_refs(df,sources='./sources/'):
    
    ctfiles = {'CWA': 'Chemical List CWA311HS-2022-03-31.csv',
               'DWSHA' : 'Chemical List EPADWS-2022-03-31.csv',
               'AQ_CWA': 'Chemical List WATERQUALCRIT-2022-03-31.csv',
               'HH_CWA': 'Chemical List NWATRQHHC-2022-03-31.csv',
               'IRIS': 'Chemical List IRIS-2022-03-31.csv',
               'PFAS_list': 'Chemical List PFASMASTER-2022-04-01.csv',
               'volatile_list': 'Chemical List VOLATILOME-2022-04-01.csv'}
    reffn = 'comptox_name_list.csv'
    for lst in ctfiles.keys():
        print(f'     -- processing {lst}')
        ctdf = pd.read_csv(os.path.join(sources,ctfiles[lst]),low_memory=False,
                           dtype={'CASRN':'str'})
        clst= ctdf.CASRN.unique().tolist()
        df['is_on_'+lst] = df.bgCAS.isin(clst)
        
    # now add the epa ref numbers and names
    refdf = pd.read_csv(os.path.join(sources,reffn),quotechar='$',encoding='utf-8')
    # we currently use CASRN for bgIngredientName because of duplicate sysnonyms
    refdf = refdf[['CASRN','epa_preferred_name',
                   'DTXSID','iupac_name']]\
            .rename({'CASRN':'bgCAS','epa_preferred_name':'epa_pref_name'},axis=1)
    refdf = refdf[~refdf.bgCAS.duplicated()] # get rid of double callouts
    df = pd.merge(df,refdf[['bgCAS','DTXSID','epa_pref_name','iupac_name']],
                  how='left',on='bgCAS')
    return df
       
    
def add_all_bgCAS_tables(df,sources='./sources/external_refs/',
                         outdir='./outdir/'):
    df = add_CompTox_refs(df,sources)
    df = add_NPDWR_list(df,sources)
    df = add_Prop65_ref(df,sources)
    df = add_TEDX_ref(df,sources)
    df = add_diesel_list(df)
    df = add_UVCB_list(df,sources)
    df = add_RQ_list(df,sources)
    return df

#################  PADUS shape files ############################
def process_PADUS(df,sources='./sources/external_refs/',
                         outdir='./outdir/',
                         use_pkl=True):
    """Find joins with the PADUS database.  Note that some wells may have
    more than one join.  This routine will add the boolean fields 
       bgFederalWells and
       bgNativeWells
    as well as a csv file with more details.
    concat geopandas: https://gis.stackexchange.com/questions/162659/joining-concat-list-of-similar-dataframes-in-geopandas
    """
    print(' -- searching for wells on Fed and Native lands')
    pkl_name = os.path.join(sources,'shape_files','padus.pkl')
    out_name = os.path.join(outdir,'PADUS_hits.csv')
    if use_pkl:
        try:
            shdf = pd.read_pickle(pkl_name)
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
            shdf.to_pickle(pkl_name)
    
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