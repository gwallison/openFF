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

# handles to use in notebook
out_dir = 'sandbox'
df_url = "https://storage.googleapis.com/open-ff-common/repos/current_repo/full_df.parquet"
df_fn = os.path.join(out_dir,'full_df.parquet')

from openFF.common.nb_helper import make_sandbox, get_df_from_file, show_done
from openFF.common.map_fracks import show_simple_map, show_wells

##### execute the following on run 
make_sandbox(out_dir)
df = get_df_from_file(df_url,df_fn)
df = df[df.in_std_filtered]
show_done()


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
    import intg_support.construct_tables_for_display as ctfd

    cgb = t.groupby('bgCAS',as_index=False)['calcMass'].sum().sort_values('calcMass',ascending=False)
    cgb1 = t.groupby('bgCAS',as_index=False)['epa_pref_name'].first()
    mg = pd.merge(cgb,cgb1,on='bgCAS',how='left')
    # mg[['bgCAS','epa_pref_name','calcMass']]

    chem_df = ctfd.make_compact_chem_summary(t)
    # chem_df.sort_values('Total mass used (lbs)',ascending=False,inplace=True)
    iShow(chem_df.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}])

# # Preamble: run as soon as this module is imported

# import os 
# import shutil
# import pandas as pd
# from IPython.display import display
# # from IPython.display import Markdown as md
# from intg_support.file_handlers import  get_df
# from intg_support.common import completed
# from intg_support.fetch_files import fetch_repo_full_df
# import intg_support.geo_tools as gt

# use_itables = True

# # root_dir = ''
# # orig_dir = os.path.join(root_dir,'orig_dir')
# # work_dir = os.path.join(root_dir,'work_dir')
# # final_dir = os.path.join(root_dir,'final')
# # ext_dir = os.path.join(root_dir,'ext')


# if use_itables:
#     from itables import init_notebook_mode
#     init_notebook_mode(all_interactive=True)
#     from itables import show as iShow
#     import itables.options as opt
#     opt.classes="display compact cell-border"
#     opt.maxBytes = 0
#     opt.maxColumns = 0
# else:
#     def iShow(df,maxBytes=0,classes=None):
#         display(df)
       
        
# # def clr_cell(txt='Cell Completed', color = '#cfc'):
# #     import datetime    
# #     t = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
# #     s = f"""<div style="background-color: {color}; padding: 10px; border: 1px solid green;">"""
# #     s+= f'<h3> {txt} </h3> {t}'
# #     s+= "</div>"
# #     display(md(s))

# # def completed(status=True,txt=''):
# #     if txt =='':
# #         if status:
# #             txt = 'This step completed normally.'
# #         else:
# #             txt ='Problems encountered in this cell! Resolve before continuing.' 
# #     if status:
# #         clr_cell(txt)
# #     else:
# #         clr_cell(txt,color='pink')

# # def get_raw_df(cols=None):
# #   """without a list of cols, whole df will be returned"""
# #   return pd.read_parquet(os.path.join(work_dir,'raw_flat.parquet'),
# #                          columns=cols)

# def get_fulldf(work_dir='./tmp'):
#     fetch_repo_full_df(outdir = work_dir)
#     return get_df(os.path.join(work_dir,'full_df.parquet'))
    
# # def create_and_fill_folders(download_repo=True,unpack_to_orig=True):
# #     import urllib.request
# #     dirs = [orig_dir,work_dir,final_dir,ext_dir]
# #     for d in dirs:
# #         if os.path.isdir(d):
# #             print(f'Directory exists: {d}')
# #         else:
# #             print(f'Creating directory: {d}')
# #             os.mkdir(d)
# #         if d==final_dir:
# #             others = ['pickles','curation_files','CAS_ref_files','CompTox_ref_files']
# #             for oth in others:   
# #                 subdir = os.path.join(d,oth)
# #                 if os.path.isdir(os.path.join(subdir)):
# #                     print(f'Directory exists: {subdir}')
# #                 else:
# #                     print(f'Creating directory: {subdir}')
# #                     os.mkdir(subdir)
# #         if d==work_dir:
# #             others = ['new_CAS_REF','new_COMPTOX_REF']
# #             for oth in others:   
# #                 subdir = os.path.join(d,oth)
# #                 if os.path.isdir(os.path.join(subdir)):
# #                     print(f'Directory exists: {subdir}')
# #                 else:
# #                     print(f'Creating directory: {subdir}')
# #                     os.mkdir(subdir)
    
# #     s_repo_name = os.path.join(orig_dir,'cloud_repo.zip')
    
# #     if download_repo:
# #         url = 'https://storage.googleapis.com/open-ff-common/repos/cloud_repo.zip'
# #         print(url)
# #         try:
# #           urllib.request.urlretrieve(url, s_repo_name)
# #         except:
# #           completed(False,'Problem downloading repository!')
# #           print('Continuing without downloading fresh copy of repository')
        
# #     if unpack_to_orig:
# #         print(' -- Unpacking existing repository into "orig" directory')
# #         shutil.unpack_archive(s_repo_name,orig_dir)
# #     completed()    

# # def get_external_files(download_ext=True):
# #     import urllib.request
# #     ext_name = os.path.join(ext_dir,'openff_ext_files.zip')
# #     if download_ext:
# #         try:
# #             print("This step may take several minutes. There are big files to transfer...")
# #             url = 'https://storage.googleapis.com/open-ff-common/openff_ext_files.zip'
# #             print(f'Downloading external files from {url}')
# #             urllib.request.urlretrieve(url, ext_name)
# #             print('Unpacking zip into "ext" directory')
# #             shutil.unpack_archive(ext_name,ext_dir)
# #             completed()
# #         except:
# #             completed(False,'Problem downloading external files!')
# #     else:
# #         completed(True,'Completed without new external download')

