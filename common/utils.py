# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 18:54:59 2023

@author: garya

Utilites to help in the maintenance of the system
"""

import sys
import os
import shutil
import pandas as pd
import geopandas
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup


def make_upload_set_of_ext_data():
    from openFF.common.handles import ext_data, ext_data_master_list
    from openFF.common.nb_helper import make_sandbox
    from openFF.common.file_handlers import get_df
    
    make_sandbox('sandbox')
    outdir = os.path.join('sandbox','ext_file_xfer')
    if os.path.exists(outdir):
        # remove old version
        shutil.rmtree(outdir)
    try:
        os.mkdir(outdir)
    except:
        print('something wrong making the folder')
        assert 1==0
    
    df = get_df(ext_data_master_list)
    lst = df[df.inc_remote=='Yes'].filename.tolist()
    for fn in lst:
        assert fn.find(' ') == -1 ,'Filename should not have spaces!'
        shutil.copy(os.path.join(ext_data,fn),outdir)
        print(f'copying {fn}')
    
  
def make_padus_pickle(source=r"C:\MyDocs\OpenFF\data\external_refs\shape_files"):
    # used to make the pickle of the giant padus geopandas dataframe
    final_crs = 4326 # EPSG value for bgLat/bgLon; 4326 for WGS84: Google maps

    print('  -- fetch PADUS from zip files')
    allshp = []
    for i in range(1,12):
        print(f'     PADUS {i} file processed')
        shp_fn = os.path.join(source,
                              f'PADUS3_0_Region_{i}_SHP.zip!PADUS3_0Combined_Region{i}.shp')
        shpdf = geopandas.read_file(shp_fn).to_crs(final_crs)
        allshp.append(shpdf)

    shdf = geopandas.GeoDataFrame(pd.concat(allshp,
                                            ignore_index=True), 
                                  crs=allshp[0].crs)
    fn = os.path.join(source,'new_padus.pkl')
    print(f'Saving pickle file to {fn}')
    shdf.to_pickle(fn)
     
    
    
if __name__ == '__main__':
    # make_padus_pickle()
    make_upload_set_of_ext_data()