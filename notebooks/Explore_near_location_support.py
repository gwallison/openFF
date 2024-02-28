import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from IPython.display import HTML, display
from IPython.display import Markdown as md

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

# df_url = hndl.working_url
# df_fn = os.path.join(out_dir,'working_df.parquet')

##### execute the following on run 
nbh.make_sandbox(out_dir)
if hndl.curr_platform=='remote':
    df = fh.get_df_from_url(df_url,df_fn)
else:
    df = fh.get_df(df_fn)
    # below is used to create a test df
    # tmp = df[(df.bgStateName=='pennsylvania')&(df.bgCountyName=='westmoreland')]
    # tmp.to_parquet(r"C:\MyDocs\OpenFF\src\testing\tmp\small_df.parquet")
    #below is used to use the small test df
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

def show_report_name_input():
    style = {'description_width': 'initial'}
    name_input = widgets.Text(
                value='Enter name here',
                layout=widgets.Layout(width="500px"),
                description='',
                disabled=False,
                indent=True,
                style=style
            )
    return name_input

def get_report_name(report_name_input):
    name = report_name_input.value
    print(f'Selected report name is {name} ')
    return name

def save_pdf_report(name_input,well_list,c_obj,lat, lon, radius):
    from reportlab.platypus import Paragraph, Image, KeepTogether, PageBreak, HRFlowable
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    import requests
    from io import BytesIO
    desc = """This is a report summarizing the chemicals disclosed in FracFocus within a 
    defined radius around a focal point.  This report was generated by a Jupyter notebook developed
    by the Open-FF project with the intent of making the chemical disclosures of FracFocus more
    accessible to the public. """

    l = [] # list of flowables
    rgen = mpr.Report_gen(outfn = 'report_test.pdf',custom_title=get_report_name(name_input),
                          report_title='Fracking chemicals disclosed around a focal point',
                          description=desc)
    l.append(rgen.make_paragraph('Focal Location',"Heading1"))
    l.append(rgen.make_paragraph(f'Latitude:  {lat}'))
    l.append(rgen.make_paragraph(f'Longitude: {lon}'))
    l.append(rgen.make_paragraph(f'Search radius: {radius} feet'))
    l.append(rgen.make_spacer())
    l.append(rgen.make_paragraph('Disclosure List',"Heading1"))
    well_list['Job End Date'] = well_list.date.dt.strftime('%Y-%m-%d')
    well_list = well_list.sort_values('date')
    l.append(rgen.make_table(well_list[['Job End Date','OperatorName',
                               'APINumber','WellName',
                               'TotalBaseWaterVolume']]))
    l.append(rgen.make_spacer())
    items = []
    items.append(rgen.make_paragraph('Water use',"Heading1"))
    items.append(Image('water_use.jpg',width=400,height=300))
    l.append(KeepTogether(items))
    # now the chemical report
    l.append(rgen.make_paragraph('Reported Chemical use',"Heading1"))
    l.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    chemdf = c_obj.get_display_table(colset='pdf_report1')
    chemdf = chemdf.sort_values(['bgCAS'])
    chemdf.rq_lbs = chemdf.rq_lbs.fillna(' -- ')
    chemdf.coc_lists = chemdf.coc_lists.fillna(' none ')
    # print(chemdf.composite_id)
    for i,row in chemdf.iterrows():
        items = []
        # items.append(rgen.make_spacer())
        data = [[rgen.make_paragraph(row.bgCAS,"Heading1"),
                 rgen.make_paragraph(row.epa_pref_name,"Heading3")]]
        items.append(rgen.make_simple_row(data))
        # items.append(rgen.make_spacer())
        # items.append(rgen.make_paragraph(row.bgCAS,"Heading1"))
        # items.append(rgen.make_paragraph(row.epa_pref_name,"Heading3"))
        data = [['Number of records','records with mass','sum of mass (lbs)','Reportable quantity (lbs)'],
                [Paragraph(str(row.tot_records)),Paragraph(str(int(row.num_w_mass))),
                 Paragraph(str(row.tot_mass)),Paragraph(str(row.rq_lbs))]]
        items.append(rgen.make_table(data,convert=False))
        # items.append(rgen.make_paragraph('Is on these lists:<br/>'+row.coc_lists))
        # items.append(rgen.make_spacer())
        fp = rgen.getFingerprintImg_RL(row.bgCAS)
        # print(fp)
        data = [['ChemInformatics Fingerprint','Lists that include this chemical'],
                [fp, Paragraph(row.coc_lists)]]
        items.append(rgen.make_table(data,convert=False))
        items.append(HRFlowable(width="100%", thickness=2, color=colors.black))
        items.append(rgen.make_spacer())
        l.append(KeepTogether(items))
    l.append(PageBreak())
    rgen.add_list_to_story(l)
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


