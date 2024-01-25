import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from IPython.display import HTML, display

use_itables = True
if use_itables:
    from itables import init_notebook_mode
    init_notebook_mode(all_interactive=True)
    from itables import show as iShow
    import itables.options as opt
    opt.classes="display compact cell-border"
    opt.maxBytes = 0
    opt.maxColumns = 0
else:
    def iShow(df,maxBytes=0,classes=None): # dummy iShow
        display(df)

import openFF.common.handles as hndl
import openFF.common.nb_helper as nbh 
import openFF.common.file_handlers as fh
import openFF.common.mapping as maps 
# from openFF.common.display_tables import make_compact_chem_summary
import openFF.common.chem_list_summary as chemls
import openFF.common.text_handlers as th
import openFF.common.make_pdf_report as mpr
from ipywidgets import widgets


# handles to use in notebook
out_dir = hndl.sandbox_dir
df_url = hndl.full_url
df_fn = os.path.join(out_dir,'full_df.parquet')

##### execute the following on run 
nbh.make_sandbox(out_dir)
if hndl.curr_platform=='remote':
    df = fh.get_df_from_url(df_url,df_fn)
else:
    df = fh.get_df(df_fn)
    # df = pd.read_parquet(r"C:\MyDocs\OpenFF\src\testing\tmp\small_df.parquet")
df = df[df.in_std_filtered]
nbh.completed()

def show_lat_lon_input(latlon_str):
    style = {'description_width': 'initial'}
    lat_lon_input = widgets.Text(
                value=latlon_str,
                layout=widgets.Layout(width="500px"),
                description='Format: "lat,lon"',
                disabled=False,
                indent=True,
                style=style
            )
    return lat_lon_input

def process_lat_lon_input(lat_lon_input):
    try:
        lst = lat_lon_input.value.split(',')
        assert len(lst)==2
        lat = float(lst[0])
        assert lat>0,  'Latitude not within US range'
        lon = float(lst[1])
        assert lon<0,  'Longitude not within US range'
        nbh.completed()
        return lat,lon
    except:
        nbh.completed(False,'Something is wrong with your input.')
        
def show_radius_input():
    style = {'description_width': 'initial'}
    radius_input = widgets.Text(
                value='5280',
                layout=widgets.Layout(width="500px"),
                description='Enter radius of circle in feet: ',
                disabled=False,
                indent=True,
                style=style
            )
    return radius_input

def process_radius_input(radius_input):
    try:
        radius = float(radius_input.value)
        print(f'Selected radius is {radius} feet, or {radius/5280} miles')
        # completed()
        return radius
    except:
        nbh.completed(False,'Something is wrong with your input.')

def get_apis(df,lat,lon,radius_in_feet=5280):
    radius_m = radius_in_feet * 0.3048
    gdf = maps.make_as_well_gdf(df)
    return maps.find_wells_near_point(lat,lon,gdf,buffer_m=radius_m)

def make_disc_link(row):
    return th.getDisclosureLink(row.api10,row.DisclosureId,row.api10,use_remote=True)

def show_well_info(apis):
    t = df[df.api10.isin(apis)].copy()
    # save the full data set from these wells to allow users to download
    t.to_csv('all_data_for_selected_wells.csv')
    t.api10 = t.apply(lambda x: make_disc_link(x),axis=1)
    dgb = t.groupby(['DisclosureId'],as_index=False)[['date','api10','APINumber','WellName',
                                                      'OperatorName','TotalBaseWaterVolume','ingKeyPresent']].first()
    iShow(dgb[['date','OperatorName','api10','WellName','TotalBaseWaterVolume','ingKeyPresent']])
    return t, dgb

def show_water_used(dgb):
    from pylab import gca, mpl
    import seaborn as sns
    sns.set_style("whitegrid")
    sns.set_palette("deep")
    ax = dgb.plot('date','TotalBaseWaterVolume',style='o',alpha=0.75,legend=None,
                 # ylim=(0,24000000)
                 )
    ax.set_title('Water Volume (gal) used in separate fracking events',fontsize=14)
    ax = gca().yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.savefig('water_use.jpg')

def create_chem_summary(t):
    return chemls.ChemListSummary(t,summarize_by_chem=True, ignore_duplicates=True)

def show_chem_summary(c_obj):
    chem_df = c_obj.get_display_table(colset='colab_v1')
    iShow(chem_df.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}],
          paging=False)
    
def save_pdf_report(well_list):
    from reportlab.platypus import Paragraph, Image #, Table, TableStyle
    rgen = mpr.Report_gen(outfn = 'report_test.pdf',custom_title='Test title',
                          report_title='Summary of fracking chemicals disclosed')
    rgen.add_heading('Well List',"Heading1")
    well_list['Job End Date'] = well_list.date.dt.strftime('%Y-%m-%d')
    well_list = well_list.sort_values('date')
    rgen.add_table(well_list[['Job End Date','OperatorName','APINumber','WellName','TotalBaseWaterVolume']])
    rgen.add_spacer()
    rgen.add_heading('Water use',"Heading1")
    rgen.add_image(Image('water_use.jpg',width=400,height=300))

    rgen.create_doc()

# def save_chem_html_summary(c_obj):
#     chem_html = c_obj.get_html_table(colset='colab_v1')
#     nbh.compile_std_page('chem_summ.html',bodytext=[chem_html])
    

# def show_chem_summary(t):
#     # import intg_support.construct_tables_for_display as ctfd
#     chemObj = chemls.ChemListSummary(t,summarize_by_chem=True, ignore_duplicates=True)

#     cgb = t.groupby('bgCAS',as_index=False)['calcMass'].sum().sort_values('calcMass',ascending=False)
#     cgb1 = t.groupby('bgCAS',as_index=False)['epa_pref_name'].first()
#     mg = pd.merge(cgb,cgb1,on='bgCAS',how='left')
#     # mg[['bgCAS','epa_pref_name','calcMass']]

#     chem_df = make_compact_chem_summary(t)
#     # chem_df.to_excel('chemical_summary.xlsx')
# #     # save the summary data from these wells to allow users to download
# #     chem_df.to_csv('chemical_summary_for_selected_wells.csv')
    
#     # chem_df.sort_values('Total mass used (lbs)',ascending=False,inplace=True)
#     iShow(chem_df.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}])


