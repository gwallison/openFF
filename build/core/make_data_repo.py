# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 12:57:54 2021
This version used openFF-build version as template in March 2023

@author: Gary

Used to create a full set of data, code and documentation that can be
the source of any use of the Open-FF products.  It is meant to
create an anchor that anyone working on the data can refer to.

Provided in the repository are: 
    - data table pickles (for recreating analysis sets)
    - zips of the full set 
    - copies of the curation filed used to create the database
    - a readme file that explains things like when the data were downloaded,
      when the data were compiled, what code version was used to create it,
      etc.
    - a csv file of hashes for most of the files in the repo.  These can 
      be used to verify that the files have not been changed since creation.
"""

import os, shutil
from pathlib import Path
from hashlib import sha256
import pandas as pd
import datetime

repo_name = 'v16_2023_03_18'

def make_repo(repo_name,ref_dir='./ref_dir',out_dir='./out_dir'):
    repo_dir = os.path.join(out_dir,'repo_dir')
    pklsource = os.path.join(ref_dir,'pickles')

    descriptive_notes = f""" This is an OpenFF data repository for the 
bulk download of FracFocus from March 18, 2023

Created {datetime.date.today()}
CodeOcean version: 16
Since the version 16 release, this beta version incorporates:
 - added bgFederalWell and bgNativeAmericanWell that is derived from
    the PADUS-3 data set.


Description of files:

    'CAS_curated.csv' - curation translation file for each unique CASNumber

    'casing_curated.csv' - curation translation file for each unique 
                            CASNumber/IngredientName pair

    'company_xlate.csv' - curation translation file for each unique company
                           name, either Supplier or OperatorName.
                           
    'ING_curated.csv',
    'CAS_synonyms.csv',
    'CAS_synonyms_CompTox.csv',
    'CAS_ref_and_names.csv',
    'upload_dates.csv',
    'missing_values.csv',
    'carrier_list_auto.csv',
    #'carrier_list_curated.csv',
    'carrier_list_prob.csv'
"""

    print(f'Starting creation of new Data Repo set: {repo_name}')
    # create new directory
    try:
        os.mkdir(repo_dir)
    except:
        print(f'\nCreation of Directory <{repo_dir}> not allowed;  already created?')
    
    # create and store README
    with open(repo_dir+'/README.txt','w') as f:
        f.write(descriptive_notes+'\n')

    # copy pickles
    pickledir = repo_dir+'/pickles'
    try:
        os.mkdir(pickledir)
    except:
        print(f'\nDirectory <{pickledir}> not created;  already created?')
    flst = os.listdir(pklsource)
    for fn in flst:
        if fn[-4:]=='.pkl':
            if not (fn[-7:]=='_df.pkl'):  # ignore pickled analysis sets
                shutil.copyfile(pklsource+'/'+fn, pickledir+'/'+fn)
                print(f'copied {fn}')


    # copy curation files
    files = ['CAS_curated.csv',
             'casing_curated.csv','company_xlate.csv','ST_api_without_pdf.csv',
             'ING_curated.csv','CAS_synonyms.csv',
             'CAS_synonyms_CompTox.csv','CAS_ref_and_names.csv',
             'tripwire_summary.csv','upload_dates.csv',
             'missing_values.csv',
             'carrier_list_auto.csv',
             #'carrier_list_curated.csv',
             'carrier_list_prob.csv']

    cdir = os.path.join(out_dir,'staging')
    os.mkdir(cdir) # made in the cwd.
    
    for fn in files:
        print(f'  - zipping {fn}')
        shutil.copy(os.path.join(ref_dir,fn),cdir)
# for fn in cfiles:
#     print(f'  - zipping {fn}')
#     shutil.copy(trans_dir+f'{data_source}/{fn}',cdir)
    shutil.make_archive(os.path.join(repo_dir,cdir),'zip',cdir)
    shutil.rmtree(cdir)         

# copy CAS and CompTox reference files

cdir = 'CAS_ref_files'
sdir = r"C:\MyDocs\OpenFF\data\external_refs\CAS_ref_files"

cdir = 'CompTox_ref_files'
sdir = r"C:\MyDocs\OpenFF\data\external_refs\CompTox_ref_files"
shutil.make_archive(os.path.join(repo_dir,cdir),'zip',sdir)

# now create hashfile
#  this is a pandas df with all files (except the hashfile) in the "filename"
#  field and the sha256 hash of the file in the "sha256" field.
#  These hashes can be used to verify that the data is in the original state and
#  has not been modified.

print('\nMaking file hashes for validation')

to_hash = ['pickles/bgCAS.pkl',
           'pickles/cas_ing.pkl',
           'pickles/chemrecs.pkl', 
           'pickles/companies.pkl',
           'pickles/disclosures.pkl',
           'curation_files.zip',                                        
           'CAS_ref_files.zip',
           'CompTox_ref_files.zip',
           'README.txt',
           'standard_filtered.zip',
           'full_no_filter.zip',
           'catalog_set.zip']

fnout = []; fnhash = []
for fn in to_hash:
    path = Path(os.path.join(repo_dir,fn))
    if path.is_file():
        print('  -- '+fn)
        fnout.append(fn)
        with open(path,'rb') as f:
            fnhash.append(sha256(f.read()).hexdigest())
    else:
        print(f'  >> file not in repo: {fn} <<')
pd.DataFrame({'filename':fnout,'filehash':fnhash}).to_csv(repo_dir+'/filehash.csv',
                                                          index=False)

print(f'Repo creation completed: {repo_dir}')