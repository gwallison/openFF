# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 17:01:07 2022

@author: Gary
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import openFF.common.text_handlers as th
# some defaults
final_crs = 4326 # WGS84
proj_crs = 3857 # convert to this when calculating distances
def_buffer = 1609.34 # one mile

def fix_county_names(df):
    trans = {'mckenzie':'mc kenzie',
             'dewitt':'de witt',
             'mcclain':'mc clain',
             'mcintosh':'mc intosh',
             'mckean':'mc kean',
             'mcmullen':'mc mullen'}
    for wrong in trans.keys():
        df.CountyName = np.where(df.CountyName==wrong,trans[wrong],df.CountyName)
    return df

def make_as_well_gdf(in_df,latName='bgLatitude',lonName='bgLongitude',
                in_crs=final_crs):
    # produce a gdf grouped by api10 (that is, by wells)
    # in_df['api10'] = in_df.APINumber.str[:10]

    gb = in_df.groupby('api10',as_index=False)[[latName,lonName,'DisclosureId']].first()
    gdf =  gpd.GeoDataFrame(gb, geometry= gpd.points_from_xy(gb[lonName], 
                                                             gb[latName],
                                                             crs=final_crs))
    return gdf
    

def find_disclosures_near_point(lat,lon,wellgdf,crs=final_crs,name='test',
                          buffer_m=def_buffer, bbnum=0.25):
    # use bounding box to shrink number of wells to check
    t = wellgdf.cx[lon-bbnum:lon+bbnum, lat-bbnum:lat+bbnum]
    t = t.to_crs(proj_crs)
    s = gpd.GeoSeries([Point(lon,lat)],crs=crs)
    s = s.to_crs(proj_crs)
    s = gpd.GeoDataFrame(geometry=s.geometry.buffer(buffer_m))
    s['name'] = name
    tmp = gpd.sjoin(t,s,how='inner')#,predicate='within')
    return tmp.DisclosureId.tolist()

def find_wells_near_point(lat,lon,wellgdf,crs=final_crs,name='test',
                          buffer_m=def_buffer, bbnum=0.25):
    # use bounding box to shrink number of wells to check
    t = wellgdf.cx[lon-bbnum:lon+bbnum, lat-bbnum:lat+bbnum]
    t = t.to_crs(proj_crs)
    s = gpd.GeoSeries([Point(lon,lat)],crs=crs)
    s = s.to_crs(proj_crs)
    s = gpd.GeoDataFrame(geometry=s.geometry.buffer(buffer_m))
    s['name'] = name
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

def show_simple_map_and_shape(lat,lon,clickable=False,include_shape=False,
                    area_df=None,zoom = 10,
                    width=600,height=400):
    import folium
    f = folium.Figure(width=width, height=height)

    mlst = [{'location': [lat,lon], 'color':'red', 'popup':'Focal point'}]
    map_center = [lat, lon] 
    m = folium.Map(tiles="openstreetmap", location=map_center, zoom_start=8).add_to(f)

    if include_shape:
        bounds = area_df.total_bounds

        sw = [bounds[1], bounds[0]]
        ne = [bounds[3], bounds[2]]
        
        m.fit_bounds([sw, ne])

        # The rest of your GeoJson plotting code is correct and can stay the same
        style = {'fillColor': '#00000000', 'color': '#0000FFFF'}
        folium.GeoJson(area_df,
                       style_function=lambda x: style,
                       smooth_factor=.2,
                       name='watershed'
                       ).add_to(m)

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
        
    # Add layer control to switch between base maps
    folium.LayerControl().add_to(m)

    return m
    

def show_simple_map(lat,lon,clickable=False,
                    width=600,height=400):
    import folium
    mlst = [{'location': [lat,lon], 'color':'red', 'popup':'Focal point'}]
    m = folium.Map(location=[lat, lon], zoom_start=12,width=width, height=height)

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

def showWells(fulldf,flat,flon,apilst,def_buffer=def_buffer,
              width=600,height=400):
    """This shows a map with a focal point (flat,flon) and the wells in apilist."""
    import folium
    mlst = [{'location': [flat,flon], 'color':'red', 'popup':'Focal point'}]
    for api in apilst:
        t = fulldf[fulldf.api10==api].groupby('APINumber')[['bgLatitude','bgLongitude']].first()
        #print(api,t)
        locs = t.iloc[0].tolist()
        mlst.append({'location': locs, 'color':'blue', 'popup':f'APINumber: {api}'})
    m = folium.Map(location=[flat, flon], zoom_start=12,
                   width=width, height=height)

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

def showDisclosures(fulldf,flat,flon,disclst,def_buffer=def_buffer):
    """This shows a map with a focal point (flat,flon) and the wells in disclist."""
    import folium
    mlst = [{'location': [flat,flon], 'color':'red', 'popup':'Focal point'}]
    for disc in disclst:
        t = fulldf[fulldf.DisclosureId==disc].groupby('APINumber')[['bgLatitude','bgLongitude']].first()
        #print(api,t)
        locs = t.iloc[0].tolist()
        mlst.append({'location': locs, 'color':'blue', 'popup':f'DisclosureId: {disc}'})
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

def showWells_in_area(fulldf,area_df,apilst,width=600,height=400):
    """Shows the wells in apilist as well as the area(s) in area_df. This was first used to show census tracts."""
    import folium
    mlst = []
    for api in apilst:
        t = fulldf[fulldf.api10==api].groupby('APINumber')[['bgLatitude','bgLongitude']].first()
        #print(api,t)
        locs = t.iloc[0].tolist()
        mlst.append({'location': locs, 'color':'blue', 'popup':f'APINumber: {api}'})

    # location=[area_df.centroid.geometry.y.iloc[0],area_df.centroid.geometry.x.iloc[0]]
    m = folium.Map(width=width,height=height)
    
    bounds = area_df.total_bounds

    sw = [bounds[1], bounds[0]]
    ne = [bounds[3], bounds[2]]
    
    m.fit_bounds([sw, ne])


    markers = mlst
    # Add the markers to the map
    for marker in markers:
        folium.Marker(
            location=marker['location'],
            icon=folium.Icon(color=marker['color']),
            name='well markers',
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

def create_point_map(data,include_mini_map=False,inc_disc_link=True,include_shape=False,area_df=None,
                     fields=['APINumber','TotalBaseWaterVolume','year','OperatorName','ingKeyPresent'],
                     aliases=['API Number','Water Volume','year','Operator','has chem recs'],
                     width=600,height=400):
    # only the first item of the area df is used.  Meant to be a simple outline, like a county line
    import folium
    from folium import plugins
    f = folium.Figure(width=width, height=height)
    if include_shape:
        #print('including shape!')
        area = [area_df.centroid.geometry.y.iloc[0],area_df.centroid.geometry.x.iloc[0]] # just first one
        m = folium.Map(tiles="openstreetmap",location=area, zoom_start=10).add_to(f)
        
        # show area
        style = {'fillColor': '#00000000', 'color': '#0000FFFF'}
        folium.GeoJson(area_df,
                       style_function=lambda x: style,
                       smooth_factor=.2,
                       name= 'target area'
                       ).add_to(m)


    else:
        m = folium.Map(tiles="openstreetmap").add_to(f)
    locations = list(zip(data.bgLatitude, data.bgLongitude))
    cluster = plugins.MarkerCluster(locations=locations,
                                   name='cluster markers')#,                     
    m.add_child(cluster)
    
    sw = data[['bgLatitude', 'bgLongitude']].min().values.tolist()
    ne = data[['bgLatitude', 'bgLongitude']].max().values.tolist()
    m.fit_bounds([sw, ne]) 

    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.bgLongitude,
                                                            data.bgLatitude),
                           crs=final_crs)
    folium.features.GeoJson(
            data=gdf,
            name='information marker',
            show=False,
            smooth_factor=2,
            style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
            popup=folium.features.GeoJsonPopup(
                fields=fields,
                aliases=aliases, 
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: #F0EFEF;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """,
                max_width=800,),
                    highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
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

    if include_mini_map:
        minimap = plugins.MiniMap()
        m.add_child(minimap)
        

    # display(f)
    return f

def create_integrated_point_map(data,include_mini_map=False,inc_disc_link=True,
                                include_shape=False,area_df=None,
                                include_filled_shape=False,filled_area_df=None,
                                
                     fields=['APINumber','TotalBaseWaterVolume','year','OperatorName','ingKeyPresent'],
                     aliases=['API Number','Water Volume','year','Operator','has chem recs'],
                     use_remote=False,
                     width=600,height=400):
    """ClusterMarker and GeoJsonPopup dont work together, so we do it by hand"""
    # only the first item of the area df is used.  Meant to be a simple outline, like a county line
    import folium
    from folium import plugins
    from IPython.display import Markdown as md
    from IPython.display import display, HTML

    f = folium.Figure(width=width, height=height)
    if include_shape | include_filled_shape:
        #print('including shape!')
        area = [area_df.centroid.geometry.y.iloc[0],area_df.centroid.geometry.x.iloc[0]] # just first one
        m = folium.Map(tiles="openstreetmap",location=area, zoom_start=7).add_to(f)
        
        if include_shape:
            # show area
            style = {'fillColor': '#00000000', 'color': '#0000FFFF'}
            folium.GeoJson(area_df,
                           style_function=lambda x: style,
                           smooth_factor=.2,
                           name= 'target area'
                           ).add_to(m)

        if include_filled_shape:
            # show area
            filled_style = {'fillColor': 'blue', 'color': 'red'}
            folium.GeoJson(filled_area_df,
                           style_function=lambda x: filled_style,
                           smooth_factor=.2,
                           name= 'filled area'
                           ).add_to(m)


    else:
        m = folium.Map(tiles="openstreetmap").add_to(f)

    sw = data[['bgLatitude', 'bgLongitude']].min().values.tolist()
    ne = data[['bgLatitude', 'bgLongitude']].max().values.tolist()
    m.fit_bounds([sw, ne]) 

    
    cluster = plugins.MarkerCluster(name='cluster markers')
    m.add_child(cluster)
    
    # import ipywidgets as widgets
    # import markdown
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.bgLongitude,
                                                            data.bgLatitude),
                           crs=final_crs)
    for i,row in gdf.iterrows():
        name = []
        val = []
        for j,field in enumerate(fields):
            name.append(f"{aliases[j]}:")
            val.append(f'{row[field]}')
        tmpdf = pd.DataFrame({'value':val},index=name)
        html = tmpdf.to_html(header=False,
                             classes="table table-striped table-hover table-condensed table-responsive")
        if inc_disc_link:
            html += '<h5>Click for details from:</h5>'
            html += '-- '+ th.getFFLink(row,'FracFocus')
            html += '<br>-- '+ th.getDisclosureLink(row.APINumber,row.DisclosureId,'Open-FF',
                                                    use_remote=use_remote)
            

        popup = folium.Popup(html)
        folium.Marker(
            location=[row.bgLatitude,row.bgLongitude],
            popup = popup,                
        ).add_to(cluster)
    
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

    return f


# single layer, with popups
def create_state_choropleth(data,
                            start_loc=[40, -96],start_zoom = 4,
                            custom_scale = [], plotlog = True,
                            legend_name = 'Test legend',
                            fields = ['StateName','orig_value'],
                            aliases = ['State: ','data: '],
                            width=600,height=400):
    import folium
    from IPython.display import display, HTML
    fn = r"C:\MyDocs\OpenFF\data\non-FF\georef-united-states-of-america-state.geojson"
    geojson = gpd.read_file(fn)
    data['orig_value'] = data.value
    # data['state_link'] = f'https://open-FF.org/{data.StateName}.html'

    geojson['StateName'] = geojson.ste_name.str.lower()
    geojson = geojson[['StateName','ste_code','geometry']]
    #     geojson.drop(['ste_name'],axis=1,inplace=True)
    f = folium.Figure(width=width, height=height)
    m = folium.Map(location= start_loc, tiles="openstreetmap",
                    zoom_start=start_zoom).add_to(f)
#     fg1 = folium.FeatureGroup(name=legend_name,overlay=False).add_to(m)
    
    geojson = pd.merge(geojson,data,on=['StateName'],how='left')
    #geojson.value.fillna(0,inplace=True)
    if plotlog:
        geojson.value = np.log10(geojson.value+1)
        legend_name = legend_name + ' (log transformed)'
    geojson.orig_value.fillna('no data',inplace=True)
    #print(geojson[['StateName','value']])
    
    if custom_scale==[]:
        custom_scale = (geojson['value'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
    folium.Choropleth(
                geo_data=fn,
                data=geojson,
                columns=['ste_code', 'value'],  #Here we tell folium to get the fips and plot values for each state
                key_on='feature.properties.ste_code',
                threshold_scale=custom_scale, #use the custom scale we created for legend
                fill_color='YlOrRd',
                nan_fill_color="gainsboro", #Use white color if there is no data available for the area
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight=0.3,
                legend_name= legend_name, #title of the legend
                highlight=True,
                line_color='black').add_to(m) 
    
    folium.features.GeoJson(
                data=geojson,
                name='',
                smooth_factor=2,
                style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
                tooltip=folium.features.GeoJsonTooltip(
                    fields=fields,
                    aliases=aliases, 
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,),
                        highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                    ).add_to(m)   

    display(f)

# single layer, with popups and links
def create_master_state_choropleth(data,
                            start_loc=[40, -96],start_zoom = 4.5,
                            custom_scale = [], plotlog = True,
                            legend_name = 'Test legend',
                            fields = ['StateName','orig_value'],
                            aliases = ['State: ','data: '],
                            width=500,height=400):
    import folium
    from IPython.display import display, HTML
    fn = r"C:\MyDocs\OpenFF\data\non-FF\georef-united-states-of-america-state.geojson"
    geojson = gpd.read_file(fn)
    data['orig_value'] = data.value
    # url = f'https://storage.googleapis.com/open-ff-browser/states/{data.StateName.replace(" ","_")}.html'
    data['state_link'] = data.StateName.map(lambda x: th.getBlogStateLink(x))
    # disable links to non-FF states
    data.state_link = np.where(data.orig_value.isna(),'not available',
                               data.state_link)
    geojson['StateName'] = geojson.ste_name.str.lower()
    geojson = geojson[['StateName','ste_code','geometry']]
    #     geojson.drop(['ste_name'],axis=1,inplace=True)
    f = folium.Figure(width=width, height=height)
    m = folium.Map(location= start_loc, tiles="openstreetmap",
                    zoom_start=start_zoom).add_to(f)
#     fg1 = folium.FeatureGroup(name=legend_name,overlay=False).add_to(m)
    
    geojson = pd.merge(geojson,data,on=['StateName'],how='left')
    #geojson.value.fillna(0,inplace=True)
    if plotlog:
        geojson.value = np.log10(geojson.value+1)
        legend_name = legend_name + ' (log transformed)'
    geojson.orig_value.fillna('no data',inplace=True)
    #print(geojson[['StateName','value']])
    
    if custom_scale==[]:
        custom_scale = (geojson['value'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
    folium.Choropleth(
                geo_data=fn,
                data=geojson,
                columns=['ste_code', 'value'],  #Here we tell folium to get the fips and plot values for each state
                key_on='feature.properties.ste_code',
                threshold_scale=custom_scale, #use the custom scale we created for legend
                fill_color='YlOrRd',
                nan_fill_color="gainsboro", #Use white color if there is no data available for the area
                fill_opacity=0.4,
                line_opacity=0.4,
                line_weight=0.3,
                legend_name= legend_name, #title of the legend
                highlight=True,
                line_color='black').add_to(m) 
    
    folium.features.GeoJson(
                data=geojson,
                name='',
                smooth_factor=2,
                style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
                popup=folium.features.GeoJsonPopup(
                    fields=fields,
                    aliases=aliases, 
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,),
                        highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                    ).add_to(m)   

    return f

def create_county_choropleth(data,
                             start_loc=[40, -96],start_zoom = 6,
                             include_shape=False,area_df=None,
                             custom_scale = [], plotlog = True,
                             legend_name = 'Test legend',
                             show_only_data_states=True,
                             #popup_enabled=True, tooltip_enabled=False,
                             fields = ['CountyName','orig_value'],
                             aliases = ['County: ','data: ']):
    import folium
    from IPython.display import display, HTML
    fn = r"C:\MyDocs\OpenFF\data\non-FF\georef-united-states-of-america-county.geojson"
    if len(data)<1:
        print('No mappable data')
        return
    geojson = gpd.read_file(fn)
    data['orig_value'] = data.value
    data['county_link'] = data.apply(lambda x: th.getBlogCountyLink(x),axis=1)
    # disable links to non-FF counties
    data.county_link = np.where(data.orig_value.isna(),'not available',
                               data.county_link)

    geojson['StateName'] = geojson.ste_name.str.lower()
    geojson['CountyName'] = geojson.coty_name.str.lower()
    geojson = fix_county_names(geojson)
    working = geojson[['StateName','CountyName','coty_code','geometry']]
    #geojson = geojson.to_crs(5070)
    working = pd.merge(working,data,on=['StateName','CountyName'],how='left')
    #print(geojson.info())
    if start_loc==[]:
        start_loc = [geojson.geometry.centroid.x.mean(),geojson.geometry.centroid.y.mean()]
    f = folium.Figure(width=600, height=400)

    if include_shape:
        #print('including shape!')
        area = [area_df.centroid.geometry.y.iloc[0],area_df.centroid.geometry.x.iloc[0]] # just first one
        m = folium.Map(tiles="openstreetmap",location=area, 
                       zoom_start=start_zoom).add_to(f)
        
        # show area
        style = {'fillColor': '#00000000', 'color': '#0000FFFF'}
        folium.GeoJson(area_df,
                       style_function=lambda x: style,
                       smooth_factor=.2,
                       name= 'target area'
                       ).add_to(m)


    else:
        m = folium.Map(location= start_loc,tiles="openstreetmap",
                       zoom_start=start_zoom).add_to(f)
    
    # m = folium.Map(location= start_loc, tiles="openstreetmap",
    #                zoom_start=start_zoom).add_to(f)
    if plotlog:
        working.value = np.log10(working.value+1)
        legend_name = legend_name + ' (log transformed)'
    working.orig_value.fillna('no data',inplace=True)
    
    if custom_scale==[]:
        custom_scale = (working['value'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
    if show_only_data_states:
        gb = data.groupby(['StateName','CountyName'],as_index=False)['value'].first()
        datalst = []
        for i,row in gb.iterrows():
            datalst.append((row.StateName,row.CountyName))
        wlst = []
        working['tup'] = list(zip(working.StateName.tolist(),working.CountyName.tolist()))
        geojson['tup'] = list(zip(geojson.StateName.tolist(),geojson.CountyName.tolist()))
        
        working = working[working.tup.isin(datalst)]
        geojson = geojson[geojson.tup.isin(datalst)]
    working.StateName = working.StateName.str.title()
    working.CountyName = working.CountyName.str.title()
    #print(f'States in geojson: {working.StateName.unique().tolist()}')
    folium.Choropleth(
                geo_data=geojson,
                data=working,
                columns=['coty_code', 'value'],  #Here we tell folium to get the fips and plot values for each state
                key_on='feature.properties.coty_code',
                threshold_scale=custom_scale, #use the custom scale we created for legend
                fill_color='YlOrRd',
                nan_fill_color="gainsboro", #Use white color if there is no data available for the area
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight=0.4,
                legend_name= legend_name, #title of the legend
                highlight=True,
                line_color='black').add_to(m) 
    
    folium.features.GeoJson(
                data=working,
                name='',
                smooth_factor=2,
                style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
                popup=folium.features.GeoJsonPopup(
                    fields=fields,
                    aliases=aliases, 
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,),
                        highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                    ).add_to(m)   
    display(f)
    return f

# def create_watershed_choropleth(data,
#                              start_loc=[40, -96],start_zoom = 6,
#                              include_shape=False,area_df=None,
#                              include_state=False,state_df=None,
#                              custom_scale = [], plotlog = True,
#                              legend_name = 'Test legend',
#                              show_only_data_states=True,
#                              #popup_enabled=True, tooltip_enabled=False,
#                              fields = ['huc8_name','huc8','orig_value','watershed_link'],
#                              aliases = ['Watershed name:',
#                                         'Watershed code',
#                                         'Num disclosures: ',
#                                         '']):
#     import folium
#     from IPython.display import display, HTML
#     # fn = r"C:\MyDocs\OpenFF\data\non-FF\georef-united-states-of-america-county.geojson"
#     # if len(data)<1:
#     #     print('No mappable data')
#     #     return
#     geojson = area_df
#     data['orig_value'] = data.value
#     data['watershed_link'] = data.apply(lambda x: th.getBlogWatershedLink(x),axis=1)
#     working = geojson[['huc8','huc8_name','geometry']]
#     working = pd.merge(working,data,on='huc8',how='left')
#     # print(geojson.info())
#     if start_loc==[]:
#         start_loc = [geojson.geometry.centroid.x.mean(),geojson.geometry.centroid.y.mean()]
#     f = folium.Figure(width=600, height=400)

    
#     m = folium.Map(location= start_loc, tiles="openstreetmap",
#                    zoom_start=start_zoom).add_to(f)
#     if plotlog:
#         working.value = np.log10(working.value+1)
#         legend_name = legend_name + ' (log transformed)'
#     working.orig_value.fillna('no data',inplace=True)
    
#     if custom_scale==[]:
#         custom_scale = (working['value'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
#     folium.Choropleth(
#                 geo_data=geojson,
#                 data=working,
#                 columns=['huc8', 'value'],  #Here we tell folium to get the fips and plot values for each state
#                 key_on='feature.properties.huc8',
#                 threshold_scale=custom_scale, #use the custom scale we created for legend
#                 fill_color='YlOrRd',
#                 nan_fill_color="gainsboro", #Use white color if there is no data available for the area
#                 fill_opacity=0.4,
#                 line_opacity=0.2,
#                 line_weight=0.2,
#                 legend_name= legend_name, #title of the legend
#                 highlight=True,
#                 line_color='black').add_to(m) 
    
#     if include_state:
#         state_style = {'fillColor': '#00000000', 'color': 'blue'}
#         folium.GeoJson(state_df,
#                        style_function=lambda x: state_style,
#                        smooth_factor=.2,
#                        name= 'state area'
#                        ).add_to(m)

#     folium.features.GeoJson(
#                 data=working,
#                 name='',
#                 smooth_factor=2,
#                 style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
#                 popup=folium.features.GeoJsonPopup(
#                     fields=fields,
#                     aliases=aliases, 
#                     localize=True,
#                     sticky=False,
#                     labels=True,
#                     style="""
#                         background-color: #F0EFEF;
#                         border: 2px solid black;
#                         border-radius: 3px;
#                         box-shadow: 3px;
#                     """,
#                     max_width=800,),
#                         highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
#                     ).add_to(m)  

#     # Add layer control to switch between base maps
#     folium.LayerControl().add_to(m)

#     display(f)
#     return f

def create_watershed_choropleth(data,
                                start_loc=[40, -96], start_zoom=6,
                                include_shape=False, area_df=None,
                                include_state=False, state_df=None,
                                custom_scale=[], plotlog=True,
                                legend_name='Test legend',
                                show_only_data_states=True,
                                fields=['huc8_name', 'huc8', 'orig_value', 'watershed_link'],
                                aliases=['Watershed name:',
                                         'Watershed code',
                                         'Num disclosures: ',
                                         ''],
                                # NEW PARAMETER to control the level of simplification in meters
                                simplification_tolerance=500):
    import folium
    import numpy as np
    import pandas as pd
    from IPython.display import display, HTML

    # ---- START: GEOMETRY SIMPLIFICATION ----
    # We will work with a copy of the area_df to avoid changing the original object
    geojson = area_df.copy()

    # Apply simplification if a positive tolerance value is provided
    if simplification_tolerance and simplification_tolerance > 0:
        print(f"Applying simplification with tolerance: {simplification_tolerance} meters")
        # Reproject to a projected CRS (meters) for accurate simplification
        geojson = geojson.to_crs(epsg=3857)
        
        # Apply the simplification method
        geojson['geometry'] = geojson.geometry.simplify(
            tolerance=simplification_tolerance,
            preserve_topology=True
        )
        
        # Reproject back to the standard geographic CRS for folium
        geojson = geojson.to_crs(epsg=4326)
    # ---- END: GEOMETRY SIMPLIFICATION ----

    data['orig_value'] = data.value
    # Assuming 'th' is defined elsewhere in your code
    data['watershed_link'] = data.apply(lambda x: th.getBlogWatershedLink(x), axis=1)

    # This 'working' DataFrame will now inherit the simplified geometries from 'geojson'
    working = geojson[['huc8', 'huc8_name', 'geometry']]
    working = pd.merge(working, data, on='huc8', how='left')

    if not start_loc:
        # Note: Centroid calculation is more accurate in a projected CRS, but this is fine for a starting view
        start_loc = [geojson.geometry.centroid.y.mean(), geojson.geometry.centroid.x.mean()]

    f = folium.Figure(width=600, height=400)
    m = folium.Map(location=start_loc, tiles="openstreetmap",
                   zoom_start=start_zoom).add_to(f)
                   
    if plotlog:
        working['value'] = np.log10(working['value'] + 1)
        legend_name = legend_name + ' (log transformed)'
    working['orig_value'].fillna('no data', inplace=True)

    if not custom_scale:
        custom_scale = (working['value'].quantile((0, 0.2, 0.4, 0.6, 0.8, 1))).tolist()

    folium.Choropleth(
        # Pass the simplified geojson data here
        geo_data=geojson,
        data=working,
        columns=['huc8', 'value'],
        key_on='feature.properties.huc8',
        threshold_scale=custom_scale,
        fill_color='YlOrRd',
        nan_fill_color="gainsboro",
        fill_opacity=0.4,
        line_opacity=0.2,
        line_weight=0.2,
        legend_name=legend_name,
        highlight=True,
        line_color='black').add_to(m)

    if include_state:
        state_style = {'fillColor': '#00000000', 'color': 'blue'}
        folium.GeoJson(state_df,
                       style_function=lambda x: state_style,
                       smooth_factor=.2,
                       name='state area'
                       ).add_to(m)

    # This layer provides the popups and also uses the simplified 'working' DataFrame
    folium.features.GeoJson(
        data=working,
        name='',
        smooth_factor=2,
        style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 0.5},
        popup=folium.features.GeoJsonPopup(
            fields=fields,
            aliases=aliases,
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800, ),
        highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
    ).add_to(m)

    folium.LayerControl().add_to(m)

    display(f)
    return f

def orig_create_county_choropleth(data,
                             start_loc=[40, -96],start_zoom = 6,
                             include_shape=False,area_df=None,
                             custom_scale = [], plotlog = True,
                             legend_name = 'Test legend',
                             show_only_data_states=True,
                             #popup_enabled=True, tooltip_enabled=False,
                             fields = ['CountyName','orig_value'],
                             aliases = ['County: ','data: ']):
    import folium
    from IPython.display import display, HTML
    fn = r"C:\MyDocs\OpenFF\data\non-FF\georef-united-states-of-america-county.geojson"
    if len(data)<1:
        print('No mappable data')
        return
    geojson = gpd.read_file(fn)
    data['orig_value'] = data.value

    geojson['StateName'] = geojson.ste_name.str.lower()
    geojson['CountyName'] = geojson.coty_name.str.lower()
    geojson = fix_county_names(geojson)
    working = geojson[['StateName','CountyName','coty_code','geometry']]
    #geojson = geojson.to_crs(5070)
    working = pd.merge(working,data,on=['StateName','CountyName'],how='left')
    #print(geojson.info())
    if start_loc==[]:
        start_loc = [geojson.geometry.centroid.x.mean(),geojson.geometry.centroid.y.mean()]
    f = folium.Figure(width=600, height=400)

    if include_shape:
        #print('including shape!')
        area = [area_df.centroid.geometry.y.iloc[0],area_df.centroid.geometry.x.iloc[0]] # just first one
        m = folium.Map(tiles="openstreetmap",location=area, 
                       zoom_start=start_zoom).add_to(f)
        
        # show area
        style = {'fillColor': '#00000000', 'color': '#0000FFFF'}
        folium.GeoJson(area_df,
                       style_function=lambda x: style,
                       smooth_factor=.2,
                       name= 'target area'
                       ).add_to(m)


    else:
        m = folium.Map(location= start_loc,tiles="openstreetmap",
                       zoom_start=start_zoom).add_to(f)
    
    # m = folium.Map(location= start_loc, tiles="openstreetmap",
    #                zoom_start=start_zoom).add_to(f)
    if plotlog:
        working.value = np.log10(working.value+1)
        legend_name = legend_name + ' (log transformed)'
    working.orig_value.fillna('no data',inplace=True)
    
    if custom_scale==[]:
        custom_scale = (working['value'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
    if show_only_data_states:
        gb = data.groupby(['StateName','CountyName'],as_index=False)['value'].first()
        datalst = []
        for i,row in gb.iterrows():
            datalst.append((row.StateName,row.CountyName))
        wlst = []
        working['tup'] = list(zip(working.StateName.tolist(),working.CountyName.tolist()))
        geojson['tup'] = list(zip(geojson.StateName.tolist(),geojson.CountyName.tolist()))
        
#         working = working[working.StateName.isin(data.StateName.unique().tolist())]
#         geojson = geojson[geojson.StateName.isin(data.StateName.unique().tolist())]
#         c1 = working.CountyName.isin(data.CountyName.unique().tolist())
#         c2 = working.StateName.isin(data.StateName.unique().tolist())
#         c3 = geojson.CountyName.isin(data.CountyName.unique().tolist())
#         c4 = geojson.StateName.isin(data.StateName.unique().tolist())
        working = working[working.tup.isin(datalst)]
        geojson = geojson[geojson.tup.isin(datalst)]
    working.StateName = working.StateName.str.title()
    working.CountyName = working.CountyName.str.title()
    #print(f'States in geojson: {working.StateName.unique().tolist()}')
    folium.Choropleth(
                geo_data=geojson,
                data=working,
                columns=['coty_code', 'value'],  #Here we tell folium to get the fips and plot values for each state
                key_on='feature.properties.coty_code',
                threshold_scale=custom_scale, #use the custom scale we created for legend
                fill_color='YlOrRd',
                nan_fill_color="gainsboro", #Use white color if there is no data available for the area
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight=0.4,
                legend_name= legend_name, #title of the legend
                highlight=True,
                line_color='black').add_to(m) 
    
    folium.features.GeoJson(
                data=working,
                name='',
                smooth_factor=2,
                style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
                popup=folium.features.GeoJsonPopup(
                    fields=fields,
                    aliases=aliases, 
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,),
                        highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                    ).add_to(m)   
    display(f)
    return f
