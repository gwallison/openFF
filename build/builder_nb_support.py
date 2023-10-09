# -*- coding: utf-8 -*-
"""
Created on Fri May  5 18:26:56 2023

@author: garya

Used to guide the builder_nb notebook code.  
Most routine runs some steps for a cell to help make the notebook more
readable for non-coders, while still making the steps easily accessible
"""

# Preamble: run as soon as this module is imported

import os 
import shutil
import pandas as pd
from IPython.display import display
from IPython.display import Markdown as md

from common.file_handlers import store_df_as_csv, save_df, get_df

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
    def iShow(df,maxBytes=0,classes=None):
        display(df)

root_dir = ''
orig_dir = os.path.join(root_dir,'orig_dir')
work_dir = os.path.join(root_dir,'work_dir')
final_dir = os.path.join(root_dir,'final')
ext_dir = os.path.join(root_dir,'ext')
code_dir = os.path.join(root_dir,'intg_support')

repo_info_fn = os.path.join(work_dir,'repo_info.csv')


       
        
def clr_cell(txt='Cell Completed', color = '#669999'):
    import datetime    
    t = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    s = f"""<div style="background-color: {color}; padding: 10px; border: 1px solid green;">"""
    s+= f'<h3> {txt} </h3> {t}'
    s+= "</div>"
    display(md(s))

def completed(status=True,txt=''):
    if txt =='':
        if status:
            txt = 'This step completed normally.'
        else:
            txt ='Problems encountered in this cell! Resolve before continuing.' 
    if status:
        clr_cell(txt)
    else:
        clr_cell(txt,color='#ff6666')

def init_repo_info():
    if not os.path.exists(repo_info_fn):        
        with open(repo_info_fn,'w') as f:
            f.write('variable,value\n')
    else:
        print('\n** repo_info.csv already exists!  Not deleting! **')
        
        
def add_to_repo_info(var,val):
    print(f'in add_to_repo_info: {var},{val}')
    with open(repo_info_fn,'a') as f:
        f.write(f'{var},{val}\n')
        
def get_new_repo_info(variable='FF_archive_filename'):
    t = pd.read_csv(os.path.join(work_dir,'repo_info.csv'))
    #print(t)
    return t[t.variable==variable].iloc[0]['value']


def get_old_repo_info(variable='bulk_download_date'):
    t = pd.read_csv(os.path.join(orig_dir,'old_repo_info.csv'))
    return t[t.variable==variable].iloc[0]['value']


def get_raw_df(cols=None):
  """without a list of cols, whole df will be returned"""
  return pd.read_parquet(os.path.join(work_dir,'raw_flat.parquet'),
                         columns=cols)



def create_and_fill_folders(download_repo=True,
                            repo_root='https://storage.googleapis.com/open-ff-common/repos/current_repo'):   
    import urllib.request



    dirs = [orig_dir,work_dir,final_dir,ext_dir]
    for d in dirs:
        if os.path.isdir(d):
            print(f'Directory exists: {d}')
        else:
            print(f'Creating directory: {d}')
            os.mkdir(d)
        if d==final_dir:
            others = ['pickles','curation_files','CAS_ref_files','CompTox_ref_files','intg_support']
            for oth in others:   
                subdir = os.path.join(d,oth)
                if os.path.isdir(os.path.join(subdir)):
                    print(f'Directory exists: {subdir}')
                else:
                    print(f'Creating directory: {subdir}')
                    os.mkdir(subdir)
        if d==orig_dir:
            others = ['pickles','curation_files','CAS_ref_files','CompTox_ref_files']
            for oth in others:   
                subdir = os.path.join(d,oth)
                if os.path.isdir(os.path.join(subdir)):
                    print(f'Directory exists: {subdir}')
                else:
                    print(f'Creating directory: {subdir}')
                    os.mkdir(subdir)
        if d==work_dir:
            others = ['new_CAS_REF','new_COMPTOX_REF']
            for oth in others:   
                subdir = os.path.join(d,oth)
                if os.path.isdir(os.path.join(subdir)):
                    print(f'Directory exists: {subdir}')
                else:
                    print(f'Creating directory: {subdir}')
                    os.mkdir(subdir)
    
#    s_repo_name = os.path.join(orig_dir,'cloud_repo.zip')
    
    if download_repo:
        # first get file list
        url = repo_root+'/dir_list.csv'
        #print(url)
        dir_fn = os.path.join(orig_dir,'dir_list.csv')
        try:
            urllib.request.urlretrieve(url, dir_fn)
        except:
            completed(False,'Problem downloading file list from repository!')
        dir_df = pd.read_csv(dir_fn)
        # print(dir_df) 
        tocopy = ['CAS_ref_files','CompTox_ref_files','curation_files','pickles']
        print('\nFetching repository files:')
        for d in tocopy:
            print(f'  -- {d}')
            c = dir_df.directory==d
            for i,row in dir_df[c].iterrows():
                url = repo_root+'/'+d+'/'+row.filename
                # print(url)
                out_fn = os.path.join(orig_dir,d,row.filename)
                urllib.request.urlretrieve(url, out_fn)
        # get repo's info file
        url = repo_root+'/repo_info.csv'
        out_fn = os.path.join(orig_dir,'old_repo_info.csv')
        urllib.request.urlretrieve(url, out_fn)
        print(f'\nDate of downloaded (last) repo: {get_old_repo_info(variable="bulk_download_date")}')
         
    
    init_repo_info()
    completed()    


def get_external_files(download_ext=True):
    import urllib.request
    ext_name = os.path.join(ext_dir,'openff_ext_files.zip')
    if download_ext:
        try:
            print("This step may take several minutes. There are big files to transfer...")
            url = 'https://storage.googleapis.com/open-ff-common/openff_ext_files.zip'
            print(f'Downloading external files from {url}')
            urllib.request.urlretrieve(url, ext_name)
            print('Unpacking zip into "ext" directory')
            shutil.unpack_archive(ext_name,ext_dir)
            completed()
        except:
            completed(False,'Problem downloading external files!')
    else:
        completed(True,'Completed without new external download')

def download_raw_FF(download_FF=True):
    import intg_support.fetch_new_bulk_data as fnbd
    import datetime 
    today = datetime.datetime.today()

    
    if download_FF:
        res = fnbd.store_FF_bulk(newdir = work_dir,sources=orig_dir, archive=False, warn=True)
        if res:
            add_to_repo_info('bulk_download_date', today.strftime("%Y-%m-%d"))
            add_to_repo_info('FF_archive_filename', 'ff_archive_'+ today.strftime("%Y-%m-%d") + '.zip')
        completed(res)
    else:
        fn = os.path.join(work_dir,'testData.zip')
        if os.path.isfile(fn):
            completed(True,'Completed using existing FF download')
        else:
            completed(False,'Could not find "testData.zip" in work_dir\nFix this issue before proceeding')
            
def create_master_raw_df(create_raw=True):
    import intg_support.Bulk_data_reader as bdr
    if create_raw:
        rff = bdr.Read_FF(in_name='testData.zip', 
                          zipdir=work_dir,workdir = work_dir,
                          origdir=orig_dir,
                          flat_pickle = 'raw_flat.parquet')
        rff.import_raw()
        raw_df = get_raw_df(cols=['reckey'])
        # get number of records from old, repository data set
        # oldrecs = pd.read_pickle(os.path.join(orig_dir,'pickles','chemrecs.pkl'))
        oldrecs = get_df(os.path.join(orig_dir,'pickles','chemrecs.parquet'),
                        cols=['reckey'])
        if len(oldrecs)>len(raw_df):
            completed(False,'The old repository has MORE records than current download. Bad download??')
        else:
            completed(len(raw_df)>0)
    else:
        completed(True,'No action taken; new FF download skipped')
        
def update_upload_date_file():
    """this routine uses the previous upload_dates file to determine the new
    disclosures. It marks the previous ones as DONE - so they will not be included
    in the next "update".  """
    import datetime
    today = datetime.datetime.today()
    datefn= os.path.join(orig_dir,'curation_files','upload_dates.parquet')
    outdf = get_df(datefn)
    uklst = outdf.UploadKey.unique()
    
    df = get_raw_df(cols=['UploadKey','OperatorName'])
    ndf = df[~df.UploadKey.isin(uklst)].copy() # just the new ones
    
    gb = ndf.groupby('UploadKey',as_index=False)['OperatorName'].count()
    gb['date_added'] = today.strftime("%Y-%m-%d")
    gb.rename({'OperatorName':'num_records'}, inplace=True,axis=1)
    print(f'Number of new disclosures added to list: {len(gb)}')
    
    outdf.weekly_report = 'DONE'
    gb['weekly_report'] = 'NO'
    outdf = pd.concat([outdf,gb],sort=True)
    # outdf.to_csv(os.path.join(work_dir,'upload_dates.csv'),index=False)
    save_df(outdf,os.path.join(work_dir,'upload_dates.parquet'))    
    completed()
    
def cas_curate_step1():
    import intg_support.CAS_master_list as casmaster
    newcas = casmaster.get_new_tentative_CAS_list(get_raw_df(cols=['CASNumber']),orig_dir=orig_dir,work_dir=work_dir)
    if len(newcas)>0:
        iShow(newcas)
        if len(newcas[newcas.tent_is_in_ref==False])>0:
            display(md('## Go to STEP B: Use SciFinder for `CASNumber`s not in reference already'))
        else:
            display(md('## Nothing to look up in SciFinder, but some curation necessary.  Skip to **Step XX**'))
    else:
        display(md('### No new CAS numbers to curate. '))
    completed() 
    
def cas_curate_step2():
    import intg_support.CAS_master_list as casmaster
    import intg_support.make_CAS_ref_files as mcrf
# This first part creates a new reference file that includes the new SciFinder data.
#   (we will run this again after we collect the CompTox data
    maker = mcrf.CAS_list_maker(orig_dir,work_dir)
    maker.make_partial_set()
    
    # Next we make a list of CAS records that need to be curated
    newcas = casmaster.get_new_tentative_CAS_list(get_raw_df(cols=['CASNumber']),orig_dir=orig_dir,work_dir=work_dir)
    casmaster.make_CAS_to_curate_file(newcas,ref_dir=orig_dir,work_dir=work_dir)    
    
def cas_curate_step3():
    import intg_support.CAS_master_list as casmaster
    flag = casmaster.is_new_complete(work_dir)
    if flag:
        completed()
    else:
        completed(False,"More CASNumbers remain to be curated. Don't proceed until corrected")

def update_CompTox_lists():
    import intg_support.make_CAS_ref_files as mcrf
    maker = mcrf.CAS_list_maker(orig_dir,work_dir)
    maker.make_full_package()
    t = get_df(os.path.join(work_dir,"comptox_lists_table.parquet"))

    print('\nThe following list is the list of recognized CompTox chemicals.')
    print('If your new chems are NOT on the list, but you were expecting them there, \nyou may have not saved the results file correctly.')
    iShow(t[['cas_number']])
    completed()
    
def casing_step1():
    import intg_support.CAS_2_build_casing as cas2
    import intg_support.IngName_curator as IngNc
    
    new_casing = cas2.make_casing(get_raw_df(cols=['CASNumber','IngredientName']),ref_dir=orig_dir,work_dir=work_dir) 
    t = new_casing[new_casing.first_date.isna()].copy()
    if len(t)>0:
        refdic = IngNc.build_refdic(ref_dir=work_dir)
        refdic = IngNc.summarize_refs(refdic)
        fsdf = IngNc.full_scan(t,refdic,pd.DataFrame(),work_dir)
        # print(fsdf.columns)
        fsdf = IngNc.analyze_fullscan(fsdf)
        # print(fsdf.columns)
        store_df_as_csv(fsdf,os.path.join(work_dir,'casing_TO_CURATE.csv'))
        fsdf = fsdf.reset_index()
        iShow(fsdf[['CASNumber', 'curatedCAS', 'IngredientName', 'recog_syn', 'synCAS',
               'match_ratio', 'n_close_match', 'source', 'bgCAS', 'rrank', 'picked']],
              maxBytes=0,classes="display compact cell-border")
        completed()
    else:
        # if no new, copy original casing_curated.csv to work_dir
        shutil.copy(os.path.join(orig_dir,'curation_files','casing_curated.parquet'),work_dir)
        completed(True,'No new CAS|Ing to process; skip next step')
        
def casing_step2():
    import datetime
    Today = datetime.datetime.today().strftime('%Y-%m-%d')
    try:
        modified = pd.read_csv(os.path.join(work_dir,'casing_modified.csv'))
        modified['first_date'] = 'D:'+f'{Today}'
        # print(modified.columns)
        oldcasing = get_df(os.path.join(orig_dir,'curation_files','casing_curated.parquet'))
        try: # works only on casing gerenated in non-cloud env. 
            oldcasing['synCAS'] = oldcasing.prospect_CAS_fromIng
            oldcasing['source'] = oldcasing.bgSource
        except:
            pass
        together = pd.concat([modified[modified.picked=='xxx'][['CASNumber','IngredientName','curatedCAS','recog_syn','synCAS',
                                                                'bgCAS','source','first_date','n_close_match']],
                              oldcasing[['CASNumber','IngredientName','curatedCAS','recog_syn','synCAS','bgCAS','source',
                                          'first_date','change_date','change_comment']] ],sort=True)
        together = together[['CASNumber','IngredientName','curatedCAS','recog_syn','synCAS','n_close_match',
                                                                'bgCAS','source','first_date','change_date','change_comment']]
        save_df(together,os.path.join(work_dir,'casing_curated.parquet'))
    except:
        display(md("#### casing_modified.csv not found in work_dir.<br>Assuming you mean to use repo version of casing_curated"))
        shutil.copy(os.path.join(orig_dir,'curation_files','casing_curated.parquet'),
                    os.path.join(work_dir,'casing_curated.parquet'))
        together = get_df(os.path.join(work_dir,'casing_curated.parquet'))
    
    completed()
    iShow(together,maxBytes=0,classes="display compact cell-border")
    
def casing_step3():
    import intg_support.CAS_2_build_casing as cas2
    completed(cas2.is_casing_complete(get_raw_df(cols=['CASNumber','IngredientName']),work_dir))
    
def companies_step1():
    import intg_support.CompanyNames_make_list as complist
    companies = complist.add_new_to_Xlate(get_raw_df(['CASNumber','OperatorName',
                                                      'Supplier','UploadKey','year']),
                                          ref_dir=orig_dir,out_dir=work_dir)
    
    completed()
    iShow(companies.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}],
         classes="display compact cell-border", scrollX=True)  
    
def companies_step2():
    import intg_support.CompanyNames_make_list as complist
    completed(complist.is_company_complete(work_dir))
    
def location_step1():
    import intg_support.Location_cleanup as loc_clean
    locobj = loc_clean.Location_ID(get_raw_df(['api10','Latitude','Longitude',
                                              'Projection','UploadKey',
                                              'StateNumber','CountyNumber',
                                              'StateName','CountyName']),
                                   ref_dir=orig_dir,out_dir=work_dir,ext_dir=ext_dir)
    _ = locobj.clean_location()
    completed()
    
def location_step2():
    import intg_support.Location_cleanup as loc_clean
    locobj = loc_clean.Location_ID(get_raw_df(),ref_dir=orig_dir,out_dir=work_dir)
    completed(locobj.is_location_complete())
    
def carrier_step():
    import intg_support.Carrier_1_identify_in_new as car1
    
    carobj = car1.Carrier_ID(get_raw_df(cols=['CASNumber','IngredientName','UploadKey','APINumber',
                                              'PercentHFJob','TotalBaseWaterVolume','date',
                                              'Purpose','IngredientKey','TradeName','MassIngredient']),
                             ref_dir=orig_dir,out_dir=work_dir)
    completed(carobj.create_full_carrier_set())
    
def builder_step1():
    # get all the CAS and CompTox ref files
    cdir = os.path.join(orig_dir,'CAS_ref_files')
    fdir = os.path.join(final_dir,"CAS_ref_files")
    shutil.copytree(src=cdir,dst=fdir,dirs_exist_ok=True)
    
    cdir = os.path.join(orig_dir,'CompTox_ref_files')
    fdir = os.path.join(final_dir,"CompTox_ref_files")
    shutil.copytree(src=cdir,dst=fdir,dirs_exist_ok=True)
    
    cdir = os.path.join(work_dir,'new_CAS_REF')
    fdir = os.path.join(final_dir,"CAS_ref_files")
    shutil.copytree(src=cdir,dst=fdir,dirs_exist_ok=True)
    
    # get files from orig_dir
    files = [
             'missing_values.csv',
             'new_state_county_ref.csv',
             'IngName_non-specific_list.parquet'
     ]
    for fn in files:
        shutil.copy(os.path.join(orig_dir,'curation_files',fn),
                    os.path.join(final_dir,'curation_files',fn))
    # get the curation files from the working dir
    files = [
             'carrier_list_auto.parquet',
             'carrier_list_prob.parquet',
             'casing_curated.parquet',
             'CAS_curated.parquet',
             'CT_syn_backup.parquet',
             'comptox_list_meta.parquet',
             'comptox_lists_table.parquet',
             'comptox-chemical-lists-meta.xlsx',
             'master_cas_number_list.parquet',
             'master_synonym_list.parquet',
             'CAS_deprecated.parquet',
             'company_xlate.parquet',
             'location_curated.parquet',
             'uploadKey_ref.parquet', 
             'upload_dates.parquet']
    for fn in files:
        shutil.copy(os.path.join(work_dir,fn),
                    os.path.join(final_dir,'curation_files',fn))
        
def builder_step2():
    # data_set_constructor
    import intg_support.Data_set_constructor as dsc
    
    dataobj = dsc.Data_set_constructor(get_raw_df(),final_dir,final_dir,ext_dir)
    _ = dataobj.create_full_set()
    completed()  
    
def builder_step3():
    # create parquet data set andn run tests
    import intg_support.Analysis_set as a_set
    import intg_support.Tests_of_final as tof

    # ana_set = a_set.Full_set(sources=final_dir,outdir=final_dir)
    # print('Fetching full data set')
    # df = ana_set.get_set(verbose=False)
    df = a_set.make_full_set_file(sources=final_dir,outdir=final_dir)
    # run tests
    print('Performing tests')
    tests = tof.final_test(df)
    tests.run_all_tests()
    completed()
    
# def make_repository():
#     import shutil
#     repo_name = 'cloud_repo_new'
#     repodir = os.path.join(final_dir,repo_name)
    
#     try:
#         os.mkdir(repodir)
#     except:
#         print(f'{repodir} already exists?')
#     pickledir = os.path.join(repodir,'pickles')
#     try:
#         os.mkdir(pickledir)
#     except:
#         print(f'{pickledir} already exists?')
#     curdir = os.path.join(repodir,'curation_files')
#     try:
#         os.mkdir(curdir)
#     except:
#         print(f'{curdir} already exists?')
            
#     # copy CAS and CompTox reference files
#     cdir = os.path.join(repodir,'CAS_ref_files')
#     sdir = os.path.join(final_dir,"CAS_ref_files")
#     shutil.copytree(sdir,cdir,dirs_exist_ok=True)
    
#     cdir = os.path.join(repodir,'CompTox_ref_files')
#     sdir = os.path.join(final_dir,"CompTox_ref_files")
#     shutil.copytree(sdir,cdir,dirs_exist_ok=True)
    
#     # copy curation files
#     cdir = os.path.join(repodir,'curation_files')
#     sdir = os.path.join(final_dir,"curation_files")
#     shutil.copytree(sdir,cdir,dirs_exist_ok=True)
    
#     # copy pickles
#     cdir = os.path.join(repodir,'pickles')
#     sdir = os.path.join(final_dir,"pickles")
#     shutil.copytree(sdir,cdir,dirs_exist_ok=True)
    
#     # Other files to copy
#     shutil.copy(os.path.join(final_dir,'full_df.parquet'),repodir)
    
#     print('Making archive...')
#     completed(shutil.make_archive(repodir, 'zip', repodir))
    
def make_repository(create_zip=False):
    directories = []
    filenames = []
    import shutil
    repo_name = 'cloud_repo_new'
    repodir = os.path.join(final_dir,repo_name)
    
    try:
        os.mkdir(repodir)
    except:
        print(f'{repodir} already exists or other problem creating directory')

    dirs = ['CAS_ref_files','CompTox_ref_files','curation_files','pickles']

    for d in dirs:
        # ndir = os.path.join(repodir,d)         
        # try:
        #     os.mkdir(ndir)
        # except:
        #     print(f'{ndir} already exists?')
        # now copy all files
        cdir = os.path.join(repodir,d)
        sdir = os.path.join(final_dir,d)
        shutil.copytree(sdir,cdir,dirs_exist_ok=True)
        dlst = os.listdir(cdir)
        for item in dlst:
            directories.append(d)
            filenames.append(item)

    # get a copy of the code used
    cdir = os.path.join(repodir,'intg_support')
    shutil.copytree(code_dir,cdir,dirs_exist_ok=True)
    dlst = os.listdir(cdir)
    for item in dlst:
        directories.append('intg_support')
        filenames.append(item)
            

    # Other files to copy
    shutil.copy(os.path.join(work_dir,'repo_info.csv'),repodir)
    directories.append('')
    filenames.append('repo_info.csv')

    shutil.copy(os.path.join(final_dir,'full_df.parquet'),repodir)
    directories.append('')
    filenames.append('full_df.parquet')
    
    arcv_fn =  get_new_repo_info(variable='FF_archive_filename')
    shutil.copy(os.path.join(work_dir,'testData.zip'),
                os.path.join(repodir, arcv_fn))    
    directories.append('')
    filenames.append(arcv_fn)
    
    dir_df = pd.DataFrame({'directory':directories,'filename':filenames})
    dir_df.to_csv(os.path.join(repodir,'dir_list.csv'))
    
    if create_zip:
        print('Making zip archive...')
        completed(shutil.make_archive(repodir, 'zip', repodir)) 
    else:
        print('Skipping zip zrchive creation')
        completed()