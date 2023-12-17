import pandas as pd
import numpy as np
import os

from itables import init_notebook_mode
init_notebook_mode(all_interactive=True)
from itables import show as iShow
import itables.options as opt
opt.classes="display compact cell-border"
opt.maxBytes = 0
opt.maxColumns = 0

from openFF.common.handles import sandbox_dir, full_url
from openFF.common.nb_helper import make_sandbox, completed
from openFF.common.file_handlers import get_df_from_url
from openFF.common.mapping import find_wells_near_point, show_simple_map, showWells, make_as_well_gdf
from openFF.common.display_tables import make_compact_chem_summary

# handles to use in notebook
out_dir = sandbox_dir
df_url = full_url
df_fn = os.path.join(out_dir,'full_df.parquet')

##### execute the following on run 
make_sandbox(out_dir)
df = get_df_from_url(df_url,df_fn)
df = df[df.in_std_filtered]
completed()

def get_apis(df,lat,lon,radius_in_feet=5280):
    radius_m = radius_in_feet * 0.3048
    gdf = make_as_well_gdf(df)
    return find_wells_near_point(lat,lon,gdf,buffer_m=radius_m)


def show_well_info(apis):
    t = df[df.api10.isin(apis)].copy()
    # t = t[t.date.dt.year>2022]
    dgb = t.groupby(['UploadKey'],as_index=False)[['date','api10','OperatorName','TotalBaseWaterVolume','ingKeyPresent']].first()
    iShow(dgb[['date','OperatorName','api10','TotalBaseWaterVolume','ingKeyPresent']])
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
    
def show_chem_summary(t):
    # import intg_support.construct_tables_for_display as ctfd

    cgb = t.groupby('bgCAS',as_index=False)['calcMass'].sum().sort_values('calcMass',ascending=False)
    cgb1 = t.groupby('bgCAS',as_index=False)['epa_pref_name'].first()
    mg = pd.merge(cgb,cgb1,on='bgCAS',how='left')
    # mg[['bgCAS','epa_pref_name','calcMass']]

    chem_df = make_compact_chem_summary(t)
    # chem_df.sort_values('Total mass used (lbs)',ascending=False,inplace=True)
    iShow(chem_df.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}])


