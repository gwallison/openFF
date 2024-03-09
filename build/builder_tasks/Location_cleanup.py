# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 10:34:50 2019

@author: GAllison

Location_cleanup updates for version 15:
    - Use shapefiles to confirm that reported lat/lon data are in the reported
      geographical entities.  Flag when they are not.
    - bgLat and bgLon will all be converted and stored in WGS84 (EPSG:4326); 
      however converting to other projections is simple when they are consistent.
    - removing some previous location flags; keeping latlon_too_coarse (but changing
      it to less than 7 decimal digits - still in the "privacy" range.)
"""
# from geopy.distance import geodesic
import pandas as pd
import numpy as np
import geopandas
import os
import shutil
from openFF.common.file_handlers import store_df_as_csv, get_csv, save_df, get_df
from openFF.common.file_handlers import ext_fn
final_crs = 4326 # EPSG value for bgLat/bgLon; 4326 for WGS84: Google maps


class Location_ID():
    def __init__(self,input_df,ref_dir='./ref_dir',out_dir='./out_dir',
                 ext_dir='./ext/'):
        self.df = input_df
        self.df['StateNumber'] = self.df.api10.str[:2].astype('int64')
        self.df['CountyNumber'] = self.df.api10.str[2:5].astype('int64')
        #print(self.df.head())
        self.ref_dir = ref_dir
        self.out_dir = out_dir
        self.ext_dir = ext_dir
    
        self.cur_tab_old = os.path.join(ref_dir,'curation_files','location_curated.csv')
        self.cur_tab = os.path.join(ref_dir,'curation_files','location_curated.parquet')
        self.api_code_ref = os.path.join(ref_dir,'curation_files','new_state_county_ref.csv')
        # self.upload_ref_fn = os.path.join(self.out_dir,'uploadKey_ref.parquet')

        self.disclosureId_ref_fn = os.path.join(self.out_dir,'disclosureId_ref.parquet')

    def get_cur_table(self):
        return get_df(self.cur_tab)
        
    def add_state_location_data(self,df):
         """used to import state-derived latlon data into dataframe
         see get_state_data directory for updating the master data file"""
         print('  -- importing state-derived location data')
         gb = df.groupby('api10',as_index=False)['DisclosureId'].first()
         gb = gb[['api10']] # don't want UploadKey
         # ext_latlon = pd.read_csv(os.path.join(self.ext_dir,
         #                                       # 'curation_files',
         #                                       'state_latlon.csv'),
         #                          dtype={'api10':str},low_memory=False,
         #                          quotechar='$',encoding='utf-8')
         # ext_latlon = get_df(os.path.join(self.ext_dir,
         #                                  'state_latlon.parquet'))
         latlonfn = ext_fn(self.ext_dir,'state_latlon')
         ext_latlon = get_df(latlonfn)

         mg = pd.merge(gb,ext_latlon[['api10','stLatitude','stLongitude']],
                       on='api10',how='left',validate='1:1')
         out = pd.merge(df,mg,on='api10',how='left',validate='m:1')
         return out

    def fetch_clean_loc_names(self,latlon_df):
        latlon_df.StateName = latlon_df.StateName.fillna('missing')
        latlon_df.CountyName = latlon_df.CountyName.fillna('missing')
        old = self.get_cur_table()
        # print(f'old: {old.columns}')
        # print(f'latlon: {latlon_df.columns}')    
        mg = pd.merge(latlon_df,old[['StateName','StateNumber',
                                      'CountyName','CountyNumber']],
                       on=['StateName','StateNumber','CountyName','CountyNumber'],
                       how='left',indicator=True)
        # print(mg.head())
        new = mg[mg._merge=='left_only'].groupby(['StateName','StateNumber',
                                                  'CountyName','CountyNumber'],
                                                 as_index=False)['DisclosureId'].count()
        print(f'Number of new locations: {len(new)}')
        newlen = len(new)
        if newlen>0:    
            # fetch reference
            ref = get_df(self.api_code_ref)
            #print(ref.head())
            
            # merge them
            mg = pd.merge(new,ref,
                          on=['StateNumber','CountyNumber'],
                          how='left')
            mg['st_ok'] = mg.StateName.str.lower()==mg.REF_StateName
            mg['ct_ok'] = mg.CountyName.str.lower()==mg.REF_CountyName
            mg['loc_name_mismatch'] = ~(mg.st_ok & mg.ct_ok)
            mg.drop(['ct_ok','st_ok'],inplace=True,axis=1)
            mg.rename({'REF_StateName':'bgStateName',
                       'REF_CountyName':'bgCountyName'},inplace=True,axis=1)
            final = pd.concat([mg,old],sort=True)

            # SAVE IT AS A file to curate
            store_df_as_csv(df =final[['StateName','bgStateName','CountyName','bgCountyName',
                                       'StateNumber','CountyNumber','loc_name_mismatch',
                                       'first_date','change_date','change_comment']],
                            fn =os.path.join(self.out_dir,'location_curated_NEW.csv'))

            return newlen,final
        else: # if no new, save original into working dir and leave
            shutil.copy(os.path.join(self.ref_dir,'curation_files','location_curated.parquet'),
                        self.out_dir)
        return newlen,old # if no new


    def reproject(self,df):
        # creates bgLat/lon that is standardized to WGS84
        print('  -- re-projecting location points')
        df['epsg'] = 4267 #nad27
        df.epsg = np.where(df.Projection.str.lower()=='nad83',4269,df.epsg)
        df.epsg = np.where(df.Projection.str.lower()=='wgs84',4326,df.epsg)
    
        crs_types = df.epsg.unique().tolist()
        # print(f'Types of EPSG in input frame: {crs_types}')
        dfs = []
        # It appears that FF v4 drops invalid lat and lon, but leaves them empty, which disrupts reprojecting
        # For now, replace na lat and lons with dummy values
        for in_epsg in crs_types:
            t = df[df.epsg==in_epsg].copy()
            t.Latitude = t.Latitude.fillna(0)
            t.Longitude = t.Longitude.fillna(0)
            # print(f'{in_epsg}, Num na in lat: {t[t.Latitude.isna()].api10.tolist()}, tot: {len(t)}')
            t = geopandas.GeoDataFrame(t, geometry= geopandas.points_from_xy(t.Longitude, t.Latitude,crs=in_epsg))
            if in_epsg != final_crs:
                t.to_crs(final_crs,inplace=True)
            dfs.append(t)
        new = pd.concat(dfs)
        new['bgLatitude'] = new.geometry.y
        new['bgLongitude'] = new.geometry.x
    
        df.drop('epsg',axis=1,inplace=True)
        df = pd.merge(df,new[['DisclosureId','bgLatitude','bgLongitude']],
                      on='DisclosureId',how='left') 
        return df

    def fetch_shapefiles(self):
        print('  -- fetching shapefiles')
        # url = 'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_500k.zip'
        # url = os.path.join(self.ext_dir,'shape_files','cb_2018_us_state_500k.zip')


        # states = geopandas.read_file(url).rename({'NAME':'StateName'},axis=1)
        stfn = ext_fn(self.ext_dir,'state_shape')
        states = geopandas.read_file(stfn).rename({'NAME':'StateName'},axis=1)
        states.StateName = states.StateName.str.lower()

        # url = 'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_500k.zip'
        # url = os.path.join(self.ext_dir,'shape_files','cb_2018_us_county_500k.zip')
        # counties = geopandas.read_file(url).rename({'NAME':'CountyName'},axis=1)
        ctyfn = ext_fn(self.ext_dir,'county_shape')
        counties = geopandas.read_file(ctyfn).rename({'NAME':'CountyName'},axis=1)
        counties.CountyName = counties.CountyName.str.lower()
        # get StateName into counties
        counties = pd.merge(counties,states[['StateName','STATEFP']],
                            on='STATEFP',how='left')
    
        return states,counties

    def get_matching_county_name(self,bgCounty,bgState,geolst):
        # some of the county names have spaces that the shapefile names don't
        # this routine finds a matching shapefile name
        if (bgState,bgCounty) in geolst:
            return bgCounty
        if ' ' in bgCounty:
            tCounty = bgCounty.replace(' ','')
            if (bgState,tCounty) in geolst:
                print(f'   found match for: {bgState},{bgCounty}')
                return tCounty
        print(f'   No match: {bgState}: {bgCounty}')
        return bgCounty
    

    def check_against_shapefiles(self,locdf):
        #print(f'Number of empty bgStateName: {locdf.bgStateName.isna().sum()}')
        #locdf[locdf.bgStateName.isna()].to_csv('./tmp/temp.csv')
        
        # first check states
        states,counties = self.fetch_shapefiles()
        states.to_crs(final_crs,inplace=True)
        counties.to_crs(final_crs,inplace=True)
        gb = counties.groupby(['StateName','CountyName'],as_index=False)['COUNTYFP'].first()
        glst = []
        for i,row in gb.iterrows():
            glst.append((row.StateName,row.CountyName))
        st_collect = []
        ct_collect = []
        st_ct_lst = locdf.groupby(['bgStateName','bgCountyName'],as_index=False)\
                     ['DisclosureId'].count()
    
        print('  -- checking against shapefiles')
        for i,row in st_ct_lst.iterrows():
            #print(f'    -- {row.bgStateName} : {row.bgCountyName}')
            gCountyName = self.get_matching_county_name(row.bgCountyName,
                                                   row.bgStateName,
                                                   glst)
            state_geo = states[states.StateName==row.bgStateName]
            county_geo = counties[(counties.StateName==row.bgStateName)&\
                                  (counties.CountyName==gCountyName)]
    
            t = locdf[(locdf.bgStateName==row.bgStateName)&\
                      (locdf.bgCountyName==row.bgCountyName)]\
                .groupby('DisclosureId',as_index=False)\
                [['bgLatitude','bgLongitude']].first()
            gdf = geopandas.GeoDataFrame(t,
                                         geometry= geopandas.points_from_xy(t.bgLongitude, 
                                                                            t.bgLatitude,
                                                                            crs=final_crs))
            points_in_st = geopandas.sjoin(gdf,state_geo,how='left')  
            points_in_st['loc_within_state'] = np.where(points_in_st.STATEFP.isna(),'NO','YES')
            st_collect.append(points_in_st[['DisclosureId','loc_within_state']])
            points_in_ct = geopandas.sjoin(gdf,county_geo,how='left')  
            points_in_ct['loc_within_county'] = np.where(points_in_ct.STATEFP.isna(),'NO','YES')
            ct_collect.append(points_in_ct[['DisclosureId','loc_within_county']])
    
        state_flag = pd.concat(st_collect,sort=True)
        final = pd.merge(locdf,state_flag,on='DisclosureId',how='left')
        county_flag = pd.concat(ct_collect,sort=True)
        final = pd.merge(final,county_flag,on='DisclosureId',how='left')
    
        final.loc_within_state = final.loc_within_state.fillna('unknown')        
        final.loc_within_county = final.loc_within_county.fillna('unknown')        
        return final
        

    # def get_upload_ref_orig(self):
    #     return pd.read_csv(self.upload_ref_fn,quotechar='$',encoding='utf-8',
    #                        low_memory=False)
    
    # def get_upload_ref(self):
    #     return get_df(self.upload_ref_fn)
    
    def get_disclosureId_ref(self):
        return get_df(self.disclosureId_ref_fn)
    
    # def save_upload_ref(self,df):
    #     """save the data frame that serves as an uploadKey reference; in particular
    #     best guesses on location data """
    
    #     # df[['UploadKey','StateName','bgStateName','CountyName','bgCountyName',
    #     #     'Latitude','bgLatitude','stLatitude',
    #     #     'Longitude','bgLongitude','stLongitude',
    #     #     'bgLocationSource',
    #     #     'latlon_too_coarse','loc_name_mismatch',
    #     #     'loc_within_state','loc_within_county']]\
    #     #         .to_csv(self.upload_ref_fn,quotechar='$',
    #     #                                  encoding='utf-8',
    #     #                                  index=False)
    #     save_df(df[['UploadKey','StateName','bgStateName','CountyName','bgCountyName',
    #                 'Latitude','bgLatitude','stLatitude',
    #                 'Longitude','bgLongitude','stLongitude',
    #                 'bgLocationSource',
    #                 'latlon_too_coarse','loc_name_mismatch',
    #                 'loc_within_state','loc_within_county']],               
    #             self.upload_ref_fn)
        
    def save_disclosureId_ref(self,df):
        """save the data frame that serves as a disclosureId reference; in particular
        best guesses on location data """
    
        save_df(df[['DisclosureId','StateName','bgStateName','CountyName','bgCountyName',
                    'Latitude','bgLatitude','stLatitude',
                    'Longitude','bgLongitude','stLongitude',
                    'bgLocationSource',
                    'latlon_too_coarse','loc_name_mismatch',
                    'loc_within_state','loc_within_county']],               
                self.disclosureId_ref_fn)
        

    def get_decimal_len(self,s):
        """used to find the length of the decimal part of  lan/lon"""
        t = str(s)
        for c in t:
            if c not in '-.0123456789':
                return -1
        if '.' not in t:
            return 0
        while '.' in t:
            try:
                t = t[1:]
            except:
                pass
        return len(t)

    def get_latlon_df(self,rawdf):
        rawdf = self.add_state_location_data(rawdf)
        return rawdf.groupby('DisclosureId',as_index=False)\
                                    [['Latitude','Longitude',
                                      'stLatitude','stLongitude',
                                      'Projection','api10',
                                      'StateNumber','CountyNumber',
                                      'StateName','CountyName']].first()
    
    def find_latlon_problems(self,locdf):
        print('Make list of disclosures whose lat/lons are not specific enough')
        locdf['latdeclen'] = locdf.Latitude.map(lambda x: self.get_decimal_len(x))
        locdf['londeclen'] = locdf.Longitude.map(lambda x: self.get_decimal_len(x))
        locdf['latlon_too_coarse'] = (locdf.londeclen+locdf.latdeclen)<7
        # flag empty  or obviously wrong lat/lon     
        return locdf.drop(['latdeclen','londeclen'],axis=1)


    def check_for_new(self):
        print('Starting check for un-curated locations')
        #rawdf = add_state_location_data(rawdf)
        locdf = self.get_latlon_df(self.df)
        rawlen = len(locdf)
        assert locdf.DisclosureId.duplicated().sum()==0
        locdf = self.find_latlon_problems(locdf)
        assert len(locdf)== rawlen
        
        newlen,clean_names = self.fetch_clean_loc_names(locdf)
        return newlen        

    def is_location_complete(self):
        t = self.get_disclosureId_ref()
        f1 = len(t)==len(self.df.DisclosureId.unique())
        f2 = t.bgStateName.isna().sum()==0
        f3 = t.bgCountyName.isna().sum()==0
        
        try:
            curtab = get_csv(os.path.join(self.out_dir,'location_curated_modified.csv'))
            f4 = curtab.first_date.isna().sum()==0
            save_df(curtab,os.path.join(self.out_dir,'location_curated.parquet'))
        except:
            print('No location_curated_modified.csv found.  Using curation from repo.')
            shutil.copy(os.path.join(self.ref_dir,'curation_files','location_curated.parquet'),
                        os.path.join(self.out_dir,'location_curated.parquet'))
            f4 = True
        return (f1&f2&f3&f4)

    ##########  Main script ###########
    def clean_location(self):   
        print('Starting Location cleanup')
        #rawdf = add_state_location_data(rawdf)
        locdf = self.get_latlon_df(self.df)
        rawlen = len(locdf)
        assert locdf.DisclosureId.duplicated().sum()==0
        locdf = self.find_latlon_problems(locdf)
        assert len(locdf)== rawlen
        
        newlen,clean_names = self.fetch_clean_loc_names(locdf)
    
        reproj_df = self.reproject(locdf)
        assert reproj_df.DisclosureId.duplicated().sum()==0
        assert len(reproj_df)== rawlen
    
        # merge them
        locdf = pd.merge(reproj_df,
                          clean_names[['StateName','CountyName',
                                       'StateNumber','CountyNumber',
                                       'bgStateName','bgCountyName',
                                       'loc_name_mismatch']],
                          on=['StateName','CountyName','StateNumber','CountyNumber'],
                          how='left')
        assert locdf.DisclosureId.duplicated().sum()==0
        assert len(locdf)== rawlen
        final = self.check_against_shapefiles(locdf)
        final['bgLocationSource'] = 'FF'
        # use state latlon if errors found
        c = (final.loc_within_county=='NO')|(final.latlon_too_coarse==True)
        c1 = final.stLatitude.notna() & c
        print(f'Number of location errors: {c.sum()}; replacable: {(c&c1).sum()}')
        final.bgLatitude = np.where(c1,final.stLatitude,final.bgLatitude)
        final.bgLongitude = np.where(c1,final.stLongitude,final.bgLongitude)
        final.bgLocationSource = np.where(c1,"state data",final.bgLocationSource)
        
        assert final.DisclosureId.duplicated().sum()==0
        assert len(final)== rawlen
    
        self.save_disclosureId_ref(final)
        return newlen
    