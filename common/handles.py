# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:40:16 2023

@author: garya

Handles for file and url locations used throughout Open-FF


"""


from datetime import datetime

import os
import platform

locals = ['Dell_2023_Gary','M2','NucBoxM4']

# repo_name = 'openFF_data_2024_03_21'
repo_name = 'openFF_data_2025_07_07'
bulkdata_date = 'July 7, 2025'

curr_platform = ''
if not platform.node() in locals:
    curr_platform = 'remote'
else:
    curr_platform = platform.node()

if curr_platform=='remote':
    # simple structure, very local within env.
    root_code = "openFF"
    root_data = ""
    curr_data = "full_df.parquet"

else:     
    # root_code = r"C:\MyDocs\integrated\openFF"
    # root_data = r"C:\MyDocs\integrated"
    root_code = r"C:\MyDocs\integrated\openFF"
    root_data = r"G:\My Drive\production"

    curr_data = os.path.join(root_data,'repos',repo_name,"full_df.parquet")
    
repo_dir = os.path.join(root_data,'repos')
curr_repo_dir = os.path.join(repo_dir,repo_name)
curr_repo_pkl_dir = os.path.join(curr_repo_dir,'pickles')
ext_data = os.path.join(root_data,'ext_data')
ext_data_master_list = os.path.join(ext_data,'ext_data_master_list.csv')
sandbox_dir = os.path.join(root_code,'sandbox')
local_includes = os.path.join(root_code,'includes')
browser_root = "https://storage.googleapis.com/open-ff-browser/"
# browser_root = "https://storage.googleapis.com/browser-beta/"
# browser_root = r"C:\MyDocs\integrated\disc_browser_spike\browser_out"
repo_root_url = "https://storage.googleapis.com/open-ff-common/repos/current_repo/"
repo_pickles_url = repo_root_url+'pickles/'
pickle_list = ['disclosures','chemrecs','bgCAS','cas_ing','companies','water_source']
archive_diff_pkl = os.path.join(curr_repo_dir,'curation_files','archive_diff_dict.pkl')

full_url = repo_root_url+"full_df.parquet"

working_df_cols = ['DisclosureId', 'JobEndDate', 'JobStartDate', 'OperatorName', 'APINumber',
                   'TotalBaseWaterVolume', 'TotalBaseNonWaterVolume', 'FFVersion', 'TVD',
                    'WellName', 'FederalWell', 'IndianWell', 'bgOperatorName', 'StateName', 'bgStateName',
                    'CountyName', 'bgCountyName', 'Latitude', 'bgLatitude', 'Longitude', 'bgLongitude',
                    'bgLocationSource', 'latlon_too_coarse', 'loc_name_mismatch', 'loc_within_state', 'loc_within_county',
                    'date','ws_perc_total', 'no_chem_recs', 'is_duplicate', 'primarySupplier',
                    'MI_inconsistent', 'IngredientsId', 'CASNumber', 'IngredientName', 'PercentHFJob', 'Supplier', 'Purpose', 
                    'TradeName', 'PercentHighAdditive', 'MassIngredient', 'ingKeyPresent', 'reckey',
                    'bgCAS', 'ingredCommonName', 'bgSupplier', 'dup_rec', 'cleanMI', 'calcMass', 'massComp', 'massCompFlag',
                    'massSource', 'mass', 'bgIngredientName', 'is_on_CWA', 'is_on_DWSHA', 'is_on_AQ_CWA', 'is_on_HH_CWA', 
                    'eh_Class_L1','eh_Class_L2',
                    'is_on_IRIS', 'is_on_PFAS_list', 'epa_pref_name', 'is_on_NPDWR', 'is_on_prop65', 'is_on_TEDX', 'is_on_diesel', 
                    'is_on_UVCB', 'rq_lbs', 'in_std_filtered']

skinny_df_cols = ['bgLatitude','bgLongitude','date','api10','bgCAS',
                  'mass','bgOperatorName','DisclosureId','in_std_filtered']
# full_url = "https://storage.googleapis.com/open-ff-common/repos/current_repo/full_df.parquet"
# full_url = "https://storage.googleapis.com/open-ff-common/repos/current_repo_FFV4/full_df.parquet"

######################  for Browser generation #######
# catalog_ver = 'beta for FFV4'
data_source = 'bulk'  # can be 'bulk', 'FFV1_scrape' or 'SkyTruth'
                                    # or 'NM_scrape_2022_05'
cat_creation_date = datetime.now()

browser_nb_dir = os.path.join(root_code,'browser','notebooks')
 # output folder is outside of main code repo
browser_out_dir = os.path.join(root_data,"browser_out")
browser_inc_dir = os.path.join(browser_out_dir,"includes")
# note that within "states" other specific dirs are created in gen_states.py
browser_states_dir = os.path.join(browser_out_dir,"states")
browser_operators_dir = os.path.join(browser_out_dir,"operators")
browser_flaws_dir = os.path.join(browser_out_dir,"flaws")
browser_disclosures_dir = os.path.join(browser_out_dir,"disclosures")
browser_api_links_dir = os.path.join(browser_out_dir,"api_links")
#browser_api_links_dir = r"D:\tmp\api_links"
browser_scope_dir = os.path.join(browser_out_dir,"scope")
browser_image_dir = os.path.join(browser_out_dir,"images")


ref_fn = os.path.join(sandbox_dir,'ref.csv')

# wells_in_dist_fn = './work/FFwells_in_school_districts.csv'

#####################  Image locations

image_dir = os.path.join(root_code,'images')

# molecule images and cheminformatics fingerprint images
pic_dir = os.path.join(image_dir,'pic_dir') 

# images used in the notebooks of the browser and other notebooks
nb_images_dir = os.path.join(image_dir,'nb_images') 
 
# regularly updated images that go into blog
blog_im_dir = os.path.join(image_dir,'blog_images')

# logos and favicons
logos_dir = os.path.join(image_dir,'logos')

# images used in the documents section (not in the image dir)
docs_images = os.path.join(root_code,'docs','images') 

################### ChemInformatics handles
ci_source = os.path.join(curr_repo_dir,"ChemInfo_ref_files")
ci_summ_fn = 'CI_sdf_summary.parquet'

###################  Scrape handles
sci_finder_scrape_dir = r"G:\My Drive\webshare\scrape_data\SciFinder_chem_pages"
chatGPT_eh_scrape_dir = r"G:\My Drive\webshare\scrape_data\chatGPT_ehClasses"


##################  FF_issues handles
ff_issues_dir = os.path.join(root_data,'FF_issues')
watchlist_dir = os.path.join(ff_issues_dir,'watchlist_dir')
