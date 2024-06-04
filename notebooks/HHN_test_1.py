"""
This code is used to produce a report of the fracking activity around a
single point.  It is part of a HHN campaign to help connect health 
professionals to information that may useful to treating patients living
near fracking facilities.

The users input will come from a spreadsheet; each line will be a report request


The started code for this module is 
openFF/notebooks/Explore_near_location_support.py

"""
import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup
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

# import openFF.common.custom_data_set as cds
# from ipywidgets import widgets


inputfn = r"G:\My Drive\webshare\temp\HHN_2024_campaign\HHN_spike (Responses) - Form Responses 1.csv"

class Make_Reports():
    def __init__(self):
        self.reqfn = r"G:\My Drive\webshare\temp\HHN_2024_campaign\HHN_spike (Responses) - Form Responses 1.csv"
        self.get_requests()
        self.repobj = Report_Constructor()
        self.process_requests()

    def get_requests(self):
        self.reqdf = pd.read_csv(self.reqfn)
        print(f'Request spreadsheet length = {len(self.reqdf)}')
        
    def process_requests(self):
        for i,row in self.reqdf.iterrows():
            if row['Latitude Longitude'] != np.nan:
                s = row['Latitude Longitude']
                try:
                    lst = s.split(',')
                    if len(lst)==2:
                        lat = float(lst[0])
                        lon = float(lst[1])
                        # print(lat,lon)
                except:
                    print(f'Row: {i}: could not transform string to lat lon')
                    continue # skip to the next request
                
                try:
                    # lat lon in range?
                    assert lat>24, 'lat must be between 24 and 70'
                    assert lat<70, 'lat must be between 24 and 70'
                    assert lon>-153, 'lon must be between -66 and -153'
                    assert lon<-66, 'lat must be between -66 and -153'
                except:
                    print(f'Row: {i}: Lat/lon values are out of range: {lat, lon}')
                    continue
                print(f'\nworking on row {i}...')
                self.repobj.new_report(lat, lon)

    
class Report_Constructor():
    def __init__(self):
        print('Reading full data set')
        self.df = pd.read_parquet(hndl.curr_data)
        print(f'len df = {len(self.df)}')
    
    def get_apis(self,radius_in_feet=5280):
        radius_m = radius_in_feet * 0.3048
        gdf = maps.make_as_well_gdf(self.df)
        return maps.find_wells_near_point(self.lat,self.lon,gdf,buffer_m=radius_m)

    def make_disc_link(self,row):
        return th.getDisclosureLink(row.api10,row.DisclosureId,row.api10,use_remote=True)
    
    def get_well_info(self):
        self.welldf = self.df[self.df.api10.isin(self.apis)].copy()
        # save the full data set from these wells to allow users to download
        # welldf.to_csv('all_data_for_selected_wells.csv')
        self.welldf['disc_link'] = self.welldf.apply(lambda x: self.make_disc_link(x),axis=1)
        self.disc_gb = self.welldf.groupby(['DisclosureId'],as_index=False)[['date','api10','APINumber','WellName',
                                                          'OperatorName','TotalBaseWaterVolume','ingKeyPresent']].first()
        # iShow(dgb[['date','OperatorName','api10','WellName','TotalBaseWaterVolume','ingKeyPresent']])
        # return t, dgb
    
    
    def show_water_used(self):
        from pylab import gca, mpl
        import seaborn as sns
        sns.set_style("whitegrid")
        sns.set_palette("deep")
        ax = self.disc_gb.plot('date','TotalBaseWaterVolume',style='o',alpha=0.75,legend=None,
                      # ylim=(0,24000000)
                      )
        ax.set_title('Water Volume (gal) used in separate fracking events',fontsize=14)
        ax = gca().yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        plt.savefig(os.path.join(hndl.sandbox_dir,'water_use.jpg'))
        
    def show_product_list(self):
        self.welldf['year'] = self.welldf.date.dt.year
        gb = self.welldf.groupby(['TradeName','Supplier'],as_index=False).IngredientName.apply(list)
        # return gb.drop('DisclosureId',axis=1)
        print(gb.columns)
        return gb
        
    # def list_to_paragraph(self,lst,rgen):
    #     s = ''
    #     for item in lst:
    #         s += item + '\n'
    #     return rgen.make_paragraph(s)
    
    def save_pdf_report(self,name_input,well_list,prod_df):#,c_obj,lat, lon, radius):
        from reportlab.platypus import Paragraph, Image, KeepTogether, PageBreak, HRFlowable
        # from reportlab.lib.units import inch
        from reportlab.lib import colors
        # import requests
        # from io import BytesIO
        desc = """This is a report summarizing the chemicals disclosed in FracFocus within a 
        defined radius around a focal point.  This report was generated by a Jupyter notebook developed
        by the Open-FF project with the intent of making the chemical disclosures of FracFocus more
        accessible to the public. """
    
        l = [] # list of flowables
        rgen = mpr.Report_gen(outfn = os.path.join(hndl.sandbox_dir,'report_test.pdf'),
                              custom_title=name_input,
                              report_title='Fracking chemicals disclosed around a focal point',
                              description=desc)
        l.append(rgen.make_spacer())
        l.append(rgen.make_paragraph('Disclosure List',"Heading1"))
        well_list['Job End Date'] = well_list.date.dt.strftime('%Y-%m-%d')
        well_list = well_list.sort_values('date')
        l.append(rgen.make_table(well_list[['Job End Date','OperatorName',
                                    'APINumber','WellName',
                                    'TotalBaseWaterVolume']]))
        # l.append(rgen.make_spacer())

        l.append(PageBreak())
        l.append(rgen.make_paragraph('Product List',"Heading1"))
        prod_df['Ingreds'] = prod_df.IngredientName.map(lambda x: self.list_to_paragraph(x,rgen))
        l.append(rgen.make_table(prod_df[['TradeName','Supplier',
                                          'Ingreds']]))
        l.append(rgen.make_spacer())
        items = []
        items.append(rgen.make_paragraph('Water use',"Heading1"))
        items.append(Image(os.path.join(hndl.sandbox_dir,'water_use.jpg'),
                           width=400,height=300))
        l.append(KeepTogether(items))
        # # now the chemical report
        # l.append(rgen.make_paragraph('Reported Chemical use',"Heading1"))
        # l.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        # chemdf = c_obj.get_display_table(colset='pdf_report1')
        # chemdf = chemdf.sort_values(['bgCAS'])
        # chemdf.rq_lbs = chemdf.rq_lbs.fillna(' -- ')
        # chemdf.coc_lists = chemdf.coc_lists.fillna(' none ')
        # # print(chemdf.composite_id)
        # for i,row in chemdf.iterrows():
        #     items = []
        #     # items.append(rgen.make_spacer())
        #     data = [[rgen.make_paragraph(row.bgCAS,"Heading1"),
        #               rgen.make_paragraph(row.epa_pref_name,"Heading3")]]
        #     items.append(rgen.make_simple_row(data))
        #     # items.append(rgen.make_spacer())
        #     # items.append(rgen.make_paragraph(row.bgCAS,"Heading1"))
        #     # items.append(rgen.make_paragraph(row.epa_pref_name,"Heading3"))
        #     data = [['Number of records','records with mass','sum of mass (lbs)','Reportable quantity (lbs)'],
        #             [Paragraph(str(row.tot_records)),Paragraph(str(int(row.num_w_mass))),
        #               Paragraph(str(row.tot_mass)),Paragraph(str(row.rq_lbs))]]
        #     items.append(rgen.make_table(data,convert=False))
        #     # items.append(rgen.make_paragraph('Is on these lists:<br/>'+row.coc_lists))
        #     # items.append(rgen.make_spacer())
        #     fp = rgen.getFingerprintImg_RL(row.bgCAS)
        #     # print(fp)
        #     data = [['ChemInformatics Fingerprint','Lists that include this chemical'],
        #             [fp, Paragraph(row.coc_lists)]]
        #     items.append(rgen.make_table(data,convert=False))
        #     items.append(HRFlowable(width="100%", thickness=2, color=colors.black))
        #     items.append(rgen.make_spacer())
        #     l.append(KeepTogether(items))
        l.append(PageBreak())
        rgen.add_list_to_story(l)
        rgen.create_doc()


    def new_report(self,lat,lon):        
        self.lat = lat
        self.lon = lon
        self.apis = self.get_apis()
        print(f'Number of wells found: {len(self.apis)}')
        # self.welldf = self.df[self.df.api10.isin(self.apis)].copy()
        # gb = t.groupby('api10')[['bgStateName','bgCountyName']].first()
        # print('\n',gb[['bgStateName','bgCountyName']].value_counts())
        self.get_well_info()
        # print(self.welldf[['date','OperatorName','api10',
        #               'WellName','TotalBaseWaterVolume']])
        prod_df = self.show_product_list()
        self.show_water_used()
        self.save_pdf_report(name_input='Test', well_list=self.disc_gb,
                             prod_df=prod_df)
        
    

        
        
if __name__ == '__main__':
    mrobj = Make_Reports()
    
    
        
# # handles to use in notebook
# out_dir = hndl.sandbox_dir
# nbh.completed()

# def show_state_name_input():
#     style = {'description_width': 'initial'}
#     name_input = widgets.Text(
#                 value='Pennsylvania',
#                 layout=widgets.Layout(width="500px"),
#                 description='',
#                 disabled=False,
#                 indent=True,
#                 style=style
#             )
#     return name_input

# # display this on loading
# state_name_input = show_state_name_input()
# display(md("### Enter target state name below"))
# display(state_name_input)


# def get_state_name(state_name_input):
#     name = state_name_input.value
#     # print(f'Selected state name is {name} ')
#     return name.strip().lower()

# def make_working_data_set(state_name_input):
#     statename = get_state_name(state_name_input)
#     newfilt = {'bgStateName':[statename]}
#     nbh.make_sandbox(out_dir)
#     custom = cds.Custom_Data_Set(force_refresh=False)
#     custom.make_final_data_set(filters=newfilt)

#     # set up the next step
#     display(md("### Latitude, Longitude entry:"))
#     lat_lon_input = show_lat_lon_input('40.38415163662122, -79.62416933177497') # default is pa well pad
#     display(lat_lon_input)

#     return custom.final_df, lat_lon_input


# def show_lat_lon_input(latlon_str):
#     style = {'description_width': 'initial'}
#     lat_lon_input = widgets.Text(
#                 value=latlon_str,
#                 layout=widgets.Layout(width="500px"),
#                 description='Format: "lat,lon"',
#                 disabled=False,
#                 indent=True,
#                 style=style
#             )
#     return lat_lon_input

# def process_lat_lon_input(lat_lon_input):
#     try:
#         lst = lat_lon_input.value.split(',')
#         assert len(lst)==2
#         lat = float(lst[0])
#         assert lat>0,  'Latitude not within US range'
#         lon = float(lst[1])
#         assert lon<0,  'Longitude not within US range'
#         nbh.completed()
#         return lat,lon
#     except:
#         nbh.completed(False,'Something is wrong with your input.')
        
# def show_radius_input():
#     style = {'description_width': 'initial'}
#     radius_input = widgets.Text(
#                 value='5280',
#                 layout=widgets.Layout(width="500px"),
#                 description='Enter radius of circle in feet: ',
#                 disabled=False,
#                 indent=True,
#                 style=style
#             )
#     return radius_input

# def process_radius_input(radius_input):
#     try:
#         radius = float(radius_input.value)
#         print(f'Selected radius is {radius} feet, or {radius/5280} miles')
#         # completed()
#         return radius
#     except:
#         nbh.completed(False,'Something is wrong with your input.')

# def get_apis(df,lat,lon,radius_in_feet=5280):
#     radius_m = radius_in_feet * 0.3048
#     # print(df.columns)
#     gdf = maps.make_as_well_gdf(df)
#     return maps.find_wells_near_point(lat,lon,gdf,buffer_m=radius_m)

# def make_disc_link(row):
#     return th.getDisclosureLink(row.api10,row.DisclosureId,row.api10,use_remote=True)

# def show_well_info(apis,df):
#     t = df[df.api10.isin(apis)].copy()
#     # save the full data set from these wells to allow users to download
#     t.to_csv('all_data_for_selected_wells.csv')
#     t.api10 = t.apply(lambda x: make_disc_link(x),axis=1)
#     dgb = t.groupby(['DisclosureId'],as_index=False)[['date','api10','APINumber','WellName',
#                                                       'OperatorName','TotalBaseWaterVolume','ingKeyPresent']].first()
#     iShow(dgb[['date','OperatorName','api10','WellName','TotalBaseWaterVolume','ingKeyPresent']])
#     return t, dgb

# def show_water_used(dgb):
#     from pylab import gca, mpl
#     import seaborn as sns
#     sns.set_style("whitegrid")
#     sns.set_palette("deep")
#     ax = dgb.plot('date','TotalBaseWaterVolume',style='o',alpha=0.75,legend=None,
#                  # ylim=(0,24000000)
#                  )
#     ax.set_title('Water Volume (gal) used in separate fracking events',fontsize=14)
#     ax = gca().yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
#     plt.savefig('water_use.jpg')

# def create_chem_summary(t):
#     return chemls.ChemListSummary(t,summarize_by_chem=True, ignore_duplicates=True,
#                                   use_remote=True)

# def show_chem_summary(c_obj):
#     chem_df = c_obj.get_display_table(colset='colab_v1')
#     iShow(chem_df.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}],
#           paging=False)

# def show_report_name_input():
#     style = {'description_width': 'initial'}
#     name_input = widgets.Text(
#                 value='Enter report title here',
#                 layout=widgets.Layout(width="500px"),
#                 description='',
#                 disabled=False,
#                 indent=True,
#                 style=style
#             )
#     return name_input

# def get_report_name(report_name_input):
#     name = report_name_input.value
#     print(f'Selected report name is {name} ')
#     return name

# def save_pdf_report(name_input,well_list,c_obj,lat, lon, radius):
#     from reportlab.platypus import Paragraph, Image, KeepTogether, PageBreak, HRFlowable
#     from reportlab.lib.units import inch
#     from reportlab.lib import colors
#     import requests
#     from io import BytesIO
#     desc = """This is a report summarizing the chemicals disclosed in FracFocus within a 
#     defined radius around a focal point.  This report was generated by a Jupyter notebook developed
#     by the Open-FF project with the intent of making the chemical disclosures of FracFocus more
#     accessible to the public. """

#     l = [] # list of flowables
#     rgen = mpr.Report_gen(outfn = 'report_test.pdf',custom_title=get_report_name(name_input),
#                           report_title='Fracking chemicals disclosed around a focal point',
#                           description=desc)
#     l.append(rgen.make_paragraph('Focal Location',"Heading1"))
#     l.append(rgen.make_paragraph(f'Latitude:  {lat}'))
#     l.append(rgen.make_paragraph(f'Longitude: {lon}'))
#     l.append(rgen.make_paragraph(f'Search radius: {radius} feet'))
#     l.append(rgen.make_spacer())
#     l.append(rgen.make_paragraph('Disclosure List',"Heading1"))
#     well_list['Job End Date'] = well_list.date.dt.strftime('%Y-%m-%d')
#     well_list = well_list.sort_values('date')
#     l.append(rgen.make_table(well_list[['Job End Date','OperatorName',
#                                'APINumber','WellName',
#                                'TotalBaseWaterVolume']]))
#     l.append(rgen.make_spacer())
#     items = []
#     items.append(rgen.make_paragraph('Water use',"Heading1"))
#     items.append(Image('water_use.jpg',width=400,height=300))
#     l.append(KeepTogether(items))
#     # now the chemical report
#     l.append(rgen.make_paragraph('Reported Chemical use',"Heading1"))
#     l.append(HRFlowable(width="100%", thickness=1, color=colors.black))
#     chemdf = c_obj.get_display_table(colset='pdf_report1')
#     chemdf = chemdf.sort_values(['bgCAS'])
#     chemdf.rq_lbs = chemdf.rq_lbs.fillna(' -- ')
#     chemdf.coc_lists = chemdf.coc_lists.fillna(' none ')
#     # print(chemdf.composite_id)
#     for i,row in chemdf.iterrows():
#         items = []
#         # items.append(rgen.make_spacer())
#         data = [[rgen.make_paragraph(row.bgCAS,"Heading1"),
#                  rgen.make_paragraph(row.epa_pref_name,"Heading3")]]
#         items.append(rgen.make_simple_row(data))
#         # items.append(rgen.make_spacer())
#         # items.append(rgen.make_paragraph(row.bgCAS,"Heading1"))
#         # items.append(rgen.make_paragraph(row.epa_pref_name,"Heading3"))
#         data = [['Number of records','records with mass','sum of mass (lbs)','Reportable quantity (lbs)'],
#                 [Paragraph(str(row.tot_records)),Paragraph(str(int(row.num_w_mass))),
#                  Paragraph(str(row.tot_mass)),Paragraph(str(row.rq_lbs))]]
#         items.append(rgen.make_table(data,convert=False))
#         # items.append(rgen.make_paragraph('Is on these lists:<br/>'+row.coc_lists))
#         # items.append(rgen.make_spacer())
#         fp = rgen.getFingerprintImg_RL(row.bgCAS)
#         # print(fp)
#         data = [['ChemInformatics Fingerprint','Lists that include this chemical'],
#                 [fp, Paragraph(row.coc_lists)]]
#         items.append(rgen.make_table(data,convert=False))
#         items.append(HRFlowable(width="100%", thickness=2, color=colors.black))
#         items.append(rgen.make_spacer())
#         l.append(KeepTogether(items))
#     l.append(PageBreak())
#     rgen.add_list_to_story(l)
#     rgen.create_doc()

# # def save_chem_html_summary(c_obj):
# #     chem_html = c_obj.get_html_table(colset='colab_v1')
# #     nbh.compile_std_page('chem_summ.html',bodytext=[chem_html])
    

# # def show_chem_summary(t):
# #     # import intg_support.construct_tables_for_display as ctfd
# #     chemObj = chemls.ChemListSummary(t,summarize_by_chem=True, ignore_duplicates=True)

# #     cgb = t.groupby('bgCAS',as_index=False)['calcMass'].sum().sort_values('calcMass',ascending=False)
# #     cgb1 = t.groupby('bgCAS',as_index=False)['epa_pref_name'].first()
# #     mg = pd.merge(cgb,cgb1,on='bgCAS',how='left')
# #     # mg[['bgCAS','epa_pref_name','calcMass']]

# #     chem_df = make_compact_chem_summary(t)
# #     # chem_df.to_excel('chemical_summary.xlsx')
# # #     # save the summary data from these wells to allow users to download
# # #     chem_df.to_csv('chemical_summary_for_selected_wells.csv')
    
# #     # chem_df.sort_values('Total mass used (lbs)',ascending=False,inplace=True)
# #     iShow(chem_df.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}])


