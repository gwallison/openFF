# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:40:16 2023

@author: garya

Handles for file and url locations used throughout Open-FF

"""
import os
import platform
locals = ['Dell_2023_Gary']

curr_platform = ''
if not platform.node() in locals:
    curr_platform = 'remote'
else:
    curr_platform = platform.node()

if curr_platform=='remote':
    root_code = "openFF"
    root_data = ""
    curr_data = "https://storage.googleapis.com/open-ff-common/repos/current_repo/full_df.parquet"

else:     
    root_code = r"C:\MyDocs\integrated\openFF"
    root_data = r"C:\MyDocs\integrated"
    curr_data = r"C:\MyDocs\integrated\repos\current_repo\full_df.parquet"
    
repo_dir = os.path.join(root_data,'repos')

curr_data
######################  for Browser generation #######
repo_name = 'cloud_repo_2023_09_20'
data_source = 'bulk'  # can be 'bulk', 'FFV1_scrape' or 'SkyTruth'
                                    # or 'NM_scrape_2022_05'
bulkdata_date = 'September 20, 2023'

 # output folder is outside of main code repo
browser_out_dir = os.path.join(root_data,"browser_out")

wells_in_dist_fn = './work/FFwells_in_school_districts.csv'
