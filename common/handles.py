# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:40:16 2023

@author: garya

Handles for file and url locations used throughout Open-FF

"""

# in this version, repo data is fetched from the directory "current_repo"

import os
import platform
locals = ['Dell_2023_Gary','M2']

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
ext_data = os.path.join(root_data,'ext_data')
ext_data_master_list = os.path.join(ext_data,'ext_data_master_list.csv')
sandbox_dir = os.path.join(root_code,'sandbox')
local_includes = os.path.join(root_code,'includes')


######################  for Browser generation #######
repo_name = 'current_repo'
data_source = 'bulk'  # can be 'bulk', 'FFV1_scrape' or 'SkyTruth'
                                    # or 'NM_scrape_2022_05'

browser_nb_dir = os.path.join(root_code,'browser','notebooks')
 # output folder is outside of main code repo
browser_out_dir = os.path.join(root_data,"browser_out")
browser_inc_dir = os.path.join(browser_out_dir,"includes")

# wells_in_dist_fn = './work/FFwells_in_school_districts.csv'

#####################  Image locations

image_dir = os.path.join(root_code,'images')

# molecule images and cheminformatics fingerprint images
pic_dir = os.path.join(image_dir,'pic_dir') 

# images used in the notebooks of the browser and other notebooks
nb_images_dir = os.path.join(image_dir,'nb_images') 
 
# regularly updated images that go into blog
blog_im_dir = os.path.join(image_dir,'blog_images')

# images used in the documents section (not in the image dir)
docs_images = os.path.join(root_code,'docs','images') 

