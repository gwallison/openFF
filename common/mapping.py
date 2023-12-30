# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 17:01:07 2022

@author: Gary
"""

#import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

final_crs = 4326 # WGS84
proj_crs = 3857 # convert to this when calculating distances
def_buffer = 1609.34 # one mile


def make_as_well_gdf(in_df,latName='bgLatitude',lonName='bgLongitude',
                in_crs=final_crs):
    # produce a gdf grouped by api10 (that is, by wells)
    # in_df['api10'] = in_df.APINumber.str[:10]
    gb = in_df.groupby('api10',as_index=False)[[latName,lonName]].first()
    gdf =  gpd.GeoDataFrame(gb, geometry= gpd.points_from_xy(gb[lonName], 
                                                             gb[latName],
                                                             crs=final_crs))
    return gdf
    

def find_wells_near_point(lat,lon,wellgdf,crs=final_crs,name='test',
                          buffer_m=def_buffer, bbnum=0.25):
    # use bounding box to shrink number of wells to check
    t = wellgdf.cx[lon-bbnum:lon+bbnum, lat-bbnum:lat+bbnum]
    t = t.to_crs(proj_crs)
    s = gpd.GeoSeries([Point(lon,lat)],crs=crs)
    s = s.to_crs(proj_crs)
    s = gpd.GeoDataFrame(geometry=s.geometry.buffer(buffer_m))
    s['name'] = name
    # tmp = gpd.sjoin(t,s,how='inner',predicate='within') Causing error after full update
    tmp = gpd.sjoin(t,s,how='inner')#,predicate='within')
    return tmp.api10.tolist()

def find_wells_within_area(gdf,wellgdf,crs=final_crs,name='test',
                          buffer_m=def_buffer): #, bbnum=0.25):
    # lat = center_lat_lon[0]
    # lon = center_lat_lon[1]
    t = wellgdf#.cx[lon-bbnum:lon+bbnum, lat-bbnum:lat+bbnum]
    t = t.to_crs(proj_crs)
    s = gdf.to_crs(proj_crs)
    # s = gpd.GeoDataFrame(geometry=s.geometry.buffer(buffer_m))
    # s['name'] = name
    #print(len(s), len(t))
    tmp = gpd.sjoin(t,s,how='inner')#,predicate='within')
    return tmp.api10.tolist()

def show_simple_map(lat,lon,clickable=False):
    import folium
    mlst = [{'location': [lat,lon], 'color':'red', 'popup':'Focal point'}]
    m = folium.Map(location=[lat, lon], zoom_start=12)

    markers = mlst
    # Add the markers to the map
    for marker in markers:
        folium.Marker(
            location=marker['location'],
            icon=folium.Icon(color=marker['color']),
            popup=marker['popup']
        ).add_to(m)
        # Display the map
           
    # Add a tile layer with satellite imagery
    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3']
    ).add_to(m)
    
    if clickable:
        folium.features.ClickForLatLng().add_to(m)
        
    # Add layer control to switch between base maps
    folium.LayerControl().add_to(m)

    return m
    

def showWells(fulldf,flat,flon,apilst,def_buffer=def_buffer):
    """This shows a map with a focal point (flat,flon) and the wells in apilist."""
    import folium
    mlst = [{'location': [flat,flon], 'color':'red', 'popup':'Focal point'}]
    for api in apilst:
        t = fulldf[fulldf.api10==api].groupby('APINumber')[['bgLatitude','bgLongitude']].first()
        #print(api,t)
        locs = t.iloc[0].tolist()
        mlst.append({'location': locs, 'color':'blue', 'popup':f'APINumber: {api}'})
    m = folium.Map(location=[flat, flon], zoom_start=12)

    markers = mlst
    # Add the markers to the map
    for marker in markers:
        folium.Marker(
            location=marker['location'],
            icon=folium.Icon(color=marker['color']),
            popup=marker['popup']
        ).add_to(m)
        # Display the map
        
    # add circle around focal point
    folium.Circle(radius=def_buffer,location=[flat,flon],
                  color='crimson',fill=True).add_to(m)
    
    # Add a tile layer with satellite imagery
    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3']
    ).add_to(m)

    # Add layer control to switch between base maps
    folium.LayerControl().add_to(m)

    return m

def showWells_in_area(fulldf,area_df,apilst):
    """Shows the wells in apilist as well as the area(s) in area_df. This was first used to show census tracts."""
    import folium
    mlst = []
    for api in apilst:
        t = fulldf[fulldf.api10==api].groupby('APINumber')[['bgLatitude','bgLongitude']].first()
        #print(api,t)
        locs = t.iloc[0].tolist()
        mlst.append({'location': locs, 'color':'blue', 'popup':f'APINumber: {api}'})

    location=[area_df.centroid.geometry.y.iloc[0],area_df.centroid.geometry.x.iloc[0]]
    m = folium.Map(location=location, zoom_start=10,width='50%',height='50%')

    markers = mlst
    # Add the markers to the map
    for marker in markers:
        folium.Marker(
            location=marker['location'],
            icon=folium.Icon(color=marker['color']),
            popup=marker['popup']
        ).add_to(m)
        # Display the map
        
    # show area
    style = {'fillColor': '#00000000', 'color': '#0000FFFF'}
    folium.GeoJson(area_df,
                   style_function=lambda x: style,
                   smooth_factor=.2
    ).add_to(m)

    # Add a tile layer with satellite imagery
    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3']
    ).add_to(m)

    # Add layer control to switch between base maps
    folium.LayerControl().add_to(m)

    return m
