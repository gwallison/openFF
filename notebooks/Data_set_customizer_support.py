#import pandas as pd
#import numpy as np
import os

from openFF.common.handles import sandbox_dir, full_url
from openFF.common.nb_helper import make_sandbox, completed
from openFF.common.file_handlers import get_df_from_url, store_df_as_csv

# handles to use in notebook
out_dir = sandbox_dir
df_url = full_url
df_fn = os.path.join(out_dir,'full_df.parquet')



##### execute the following on run 
make_sandbox(out_dir)
df = get_df_from_url(df_url,df_fn)
completed()

##### filtering routines

# states
import ipywidgets as widgets
def prep_states():
    st_lst = df.bgStateName.unique().tolist()
    st_lst.sort()
    st_lst.insert(0,'All states')
    states = widgets.SelectMultiple(
                    options=st_lst,
                    value=['All states'],
                    #rows=10,
                    description='Select State(s)',
                    disabled=False
                )
    completed()
    return states

def filter_by_statelist(df,states):
    if states.value[0]!='All states':
        df = df[df.bgStateName.isin(list(states.value))]
    print(f"The current filtered data frame's shape (rows,cols): {df.shape}")
    completed()
    return df

def show_inc_chem_checkbox():
    include_chem = widgets.Checkbox(
                        value=True,
                        description='Include chemical data',
                        disabled=False,
                        indent=True
                    )
    return include_chem

def show_chem_set(inc_chk_box):
    if not inc_chk_box.value:
        completed('No chemical records to be included. Skip to "Select columns"')
        chem_set = None
    else:
        chem_set = widgets.Dropdown(
        options=[('All','all'),
                 ('Custom','custom'),
                 ('Clean Water Act','cwa'),
                 ('Safe Drinking Water Act','dwsha'),
                 ('UVCB','uvcb'),
                 ('Sand and water','sand'),
                 ('Trade secrets','proprietary')],
        value='all',
        description='Chemical Set:',
        disabled=False,
        )
    return chem_set

def check_for_custom_list(chem_set,inc_chk_box):
    if inc_chk_box.value==False:
        return None
    if chem_set.value=='custom':
        df.epa_pref_name.fillna(' ??? ',inplace=True)
        gb = df.groupby('bgCAS',as_index=False)['epa_pref_name'].first()
        caslst = []
        # create a list of tuples to use in widget
        for i,row in gb.iterrows():
            caslst.append((row.bgCAS +' - '+row.epa_pref_name,row.bgCAS))
        #print(len(caslst))
        cus_chem= widgets.SelectMultiple(
            options=caslst,
            value=[caslst[0][1]],
            rows=25,
            description='choose:',
            disabled=False
            )
    else:
        cus_chem=None
        print('No custom chemical list; continue to next step')
    return cus_chem



def filter_by_chem_set(df,chem_set,cus_chem):
    # now process selected chemicals
    if chem_set == None: # only metadata
        return df
    if chem_set.value != 'all':
        if chem_set.value == 'uvcb':
            caslst = df[df.is_on_UVCB].bgCAS.unique().tolist()
        if chem_set.value == 'cwa':
            caslst = df[df.is_on_CWA].bgCAS.unique().tolist()
        if chem_set.value == 'dwsha':
            caslst = df[df.is_on_DWSHA].bgCAS.unique().tolist()
        if chem_set.value == 'sand':
            caslst = ['14808-60-7','7732-18-5']
        if chem_set.value == 'proprietary':
            caslst = ['proprietary']
        if chem_set.value == 'custom':
            caslst = cus_chem.value
        df = df[df.bgCAS.isin(caslst)]
    print(f'Number of chemicals selected: {len(df.bgCAS.unique())}')
    print(f"The current filtered data frame's shape (rows,cols): {df.shape}")    
    completed()
    return df

def show_col_set():
    col_set = widgets.Dropdown(
                        options=['Full','Standard'],
                        value='Standard',
                        description='Column Set:',
                        disabled=False,
                    )
    return col_set

def filter_by_col_set(df,col_set,inc_chk_box):
    std_set_meta = ['StateName','CountyName','Latitude','Longitude',
                   'OperatorName','WellName','UploadKey','date','APINumber',
                   'bgStateName','bgCountyName','bgLatitude','bgLongitude',
                   'TotalBaseWaterVolume','TotalBaseNonWaterVolume','TVD','bgOperatorName','primarySupplier',
                   'carrier_status','no_chem_recs']

    std_set_chem = ['CASNumber','IngredientName','Supplier','bgCAS','calcMass','categoryCAS',
                    'PercentHFJob','Purpose','TradeName','bgSupplier',
                    'is_valid_cas','bgIngredientName']
    
    lst = std_set_meta
    if inc_chk_box.value:
        lst = lst + std_set_chem
    else: # take only meta
        df = df.groupby('UploadKey',as_index=False)[df.columns.tolist()].first()
        
    if col_set.value == 'Standard':
        df = df[df.in_std_filtered].filter(lst,axis=1)
    print(f"The current filtered data frame's shape (rows,cols): {df.shape}")
    completed()
    return df

def show_formats():
    format_type = widgets.ToggleButtons(
                        options=['parquet', 'CSV', 'Excel'],
                        description='Select:',
                        disabled=False,
                        button_style='', # 'success', 'info', 'warning', 'danger' or ''
                        #icons=['check'] * 3
                    )
    return format_type

def make_output_file(df,format_type):
    if format_type.value=='CSV':
        # make the CSV file
        outfn = os.path.join(out_dir,"my_output.csv")
        store_df_as_csv(df,outfn)

    if format_type.value=='Excel':
        # make the Excel
        outfn = os.path.join(out_dir,"my_output.xlsx")
        df.to_excel(outfn)

    if format_type.value=='parquet':
        outfn = os.path.join(out_dir,"my_output.parquet")
        df.to_parquet(outfn)

    file_size = os.path.getsize(outfn)
    print("File Size is :", file_size, "bytes")
    print(f'Output saved at: {outfn}, size: {file_size:,} bytes') 
    completed()