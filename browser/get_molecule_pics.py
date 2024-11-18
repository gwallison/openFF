# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 20:23:03 2022

@author: Gary
"""
import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup
import openFF.common.file_handlers as fh 
import openFF.common.handles as hndl 
import openFF.common.chem_info_tools as cit

import os
import time
import requests


pic_dir = hndl.pic_dir


def make_pic_dir(caslst=['50-00-0']):
    try:
        lst = os.listdir(pic_dir)
    except:
        print('Creating new pic directory')
        os.mkdir(pic_dir)
    for cas in caslst:
        d = os.path.join(pic_dir,cas)
        if not os.path.exists(d):
            print(f'making dir: {cas}')
            os.mkdir(d)
            
#  ChemID has been deprecated. PubChem instead and images are fetched manually    
# def fetch_chem_id_pic(cas):
#     url = f"https://chem.nlm.nih.gov/chemidplus/structure/{cas}" 
#     rq = requests.get(url,timeout=100)
#     if rq.status_code==200:
#         print(f'ChemID: {cas} - got it!')
#         with open(os.path.join(pic_dir,cas,'chemid.png'),'wb') as f:
#             f.write(rq.content)
#     else:
#         if rq.status_code==404:
#             with open(os.path.join(pic_dir,cas,'chemid.png'),'wb') as f:
#                 f.write(b'')
#             print(f'{cas} - 404')
#         else:
#             print(f'{cas} {rq.status_code}: what happened?')
            
######################
## Bug requires the following code from: 
##   https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
#####################
import urllib3
import ssl

class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session
###########
## end imported code
###########

def fetch_comptox_pic(cas,dtxsid):
    url = f"https://comptox.epa.gov/dashboard-api/ccdapp1/chemical-files/image/by-dtxsid/{dtxsid}"    
    with get_legacy_session() as s: 
        rq = s.get(url) 
          
    # rq = requests.get(url,timeout=1000)
    if rq.status_code==200:
        print(f'Comptox: {cas} - found it!')
        path = os.path.join(pic_dir,cas,'comptoxid.png')
        with open(path,'wb') as f:
            f.write(rq.content)
        if os.path.getsize(path)==0: # empty files returned when they don't exist
            print('... but it is empty')
            #os.remove(path)  # KEEP empty file as signal

    else:
        if rq.status_code==404:
            print(f'{cas} - 404')
        else:
            print(f'{cas} {rq.status_code}: what happened?')
    

## depending on empty file to signal no image at comptox, to prevent searching
##   every time.  Don't use cleanup regularly!!

# def cleanup_dirs(caslst):
#     for cas in caslst:
#         path = os.path.join(pic_dir,cas,'comptoxid.png')
#         if os.path.exists(path):
#             if os.path.getsize(path) == 0:
#                 print(f'removing empty file for {cas}')
#                 os.remove(path)
                
def show_chemID_only(caslst):
    """finds and lists those cas numbers that don't have comptox images"""
    for cas in caslst:
        ctpath = os.path.join(pic_dir,cas,'comptoxid.png')
        cidpath = os.path.join(pic_dir,cas,'chemid.png')
        if not os.path.exists(ctpath):
            if os.path.exists(cidpath):
                print(cas)
    
if __name__ == '__main__':
    caslst = fh.get_cas_list()        
    dtxdf = fh.get_comptox_df()
    # print(dtxdf.columns)
    make_pic_dir(caslst=caslst)
    #show_chemID_only(caslst)

    # for cas in caslst:
    #     if not os.path.exists(os.path.join(pic_dir,cas,'chemid.png')):
    #         #print(f'<<{cas}>>')
    #         fetch_chem_id_pic(cas)
    #         time.sleep(8)
    # work first on chemical image from EPA
    for i,row in dtxdf.iterrows():
        #print(row.DTXSID)
        if not os.path.exists(os.path.join(pic_dir,row.bgCAS,'comptoxid.png')):
            print(f'trying to fetch: {row.bgCAS}, {row.DTXSID}')
            if row.DTXSID[:3]=='DTX':
                fetch_comptox_pic(row.bgCAS, row.DTXSID)
                time.sleep(5)
    # now build fingerprints for new chem
    hazdf = cit.get_all_excel()
    for cas in caslst:
        if cas in cit.cas_ignore:
            continue
        if not os.path.exists(os.path.join(pic_dir,cas,'haz_fingerprint.png')):
            print(f'tryiing to create fingerprint for: {cas}')
            try:
                cit.make_fingerprint(hazdf,cas)
            except:
                print(f'Error making {cas}; ignoring...')

      
    
