# -*- coding: utf-8 -*-
"""
Created on Fri May  5 18:26:56 2023

@author: garya

Used to guide the builder_nb notebook code.  
Most routine runs some steps for a cell to help make the notebook more
readable for non-coders, while still making the steps easily accessible
"""

##### ------ Preamble: run as soon as this module is imported
import os 
import shutil
import pandas as pd
from IPython.display import display
from IPython.display import Markdown as md

from openFF.common.file_handlers import store_df_as_csv, save_df 
from openFF.common.file_handlers import get_df, get_ext_master_dic
from openFF.common.nb_helper import completed, make_sandbox
import openFF.common.handles as hndl
import openFF.build.core.fetch_archive_difference_set as fads


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

root_dir = 'sandbox'
orig_dir = os.path.join(root_dir,'orig_dir')
work_dir = os.path.join(root_dir,'work_dir')
final_dir = os.path.join(root_dir,'final')
ext_dir = os.path.join(root_dir,'ext')

# code_dir = os.path.join(root_dir,'intg_support')

repo_info_fn = os.path.join(work_dir,'repo_info.csv')

make_sandbox(root_dir)
completed()     
        
####  ------- Utilities called by other functions in this file 

def init_repo_info(repo_info_fn=repo_info_fn):
    if not os.path.exists(repo_info_fn):        
        with open(repo_info_fn,'w') as f:
            f.write('variable,value\n')
    else:
        print('\n** repo_info.csv already exists!  Not deleting! **')
        
        
def add_to_repo_info(var,val):
    print(f'in add_to_repo_info: {var},{val}')
    with open(repo_info_fn,'a') as f:
        f.write(f'{var},{val}\n')
        
def get_new_repo_info(variable='FF_archive_filename',work_dir=work_dir):
    t = pd.read_csv(os.path.join(work_dir,'repo_info.csv'))
    #print(t)
    return t[t.variable==variable].iloc[0]['value']


def get_old_repo_info(variable='bulk_download_date',orig_dir=orig_dir):
    t = pd.read_csv(os.path.join(orig_dir,'old_repo_info.csv'))
    return t[t.variable==variable].iloc[0]['value']


def get_raw_df(cols=None,work_dir=work_dir):
  """without a list of cols, whole df will be returned"""
  return pd.read_parquet(os.path.join(work_dir,'raw_flat.parquet'),
                         columns=cols)

def get_water_source_df(cols=None,work_dir=work_dir):
  """without a list of cols, whole df will be returned"""
  return pd.read_parquet(os.path.join(work_dir,'ws_flat.parquet'),
                         columns=cols)

####  ------ Functions called by the builder notebook

def create_and_fill_folders(download_repo=True,
                            repo_root='https://storage.googleapis.com/open-ff-common/repos/current_repo',
                            orig_dir=orig_dir,
                            work_dir=work_dir,
                            final_dir=final_dir,
                            ext_dir=ext_dir):   
    import urllib.request
    print(f'Using repo location **{repo_root}** as starting point.')
    dirs = [orig_dir,work_dir,final_dir,ext_dir]
    for d in dirs:
        if os.path.isdir(d):
            print(f'Directory exists: {d}')
        else:
            print(f'Creating directory: {d}')
            os.mkdir(d)
        if d==final_dir:
            others = ['pickles','curation_files','CAS_ref_files',
                      'CompTox_ref_files','ChemInfo_ref_files']
            for oth in others:   
                subdir = os.path.join(d,oth)
                if os.path.isdir(os.path.join(subdir)):
                    print(f'Directory exists: {subdir}')
                else:
                    print(f'Creating directory: {subdir}')
                    os.mkdir(subdir)
        if d==orig_dir:
            others = ['pickles','curation_files','CAS_ref_files',
                      'CompTox_ref_files','ChemInfo_ref_files']
            for oth in others:   
                subdir = os.path.join(d,oth)
                if os.path.isdir(os.path.join(subdir)):
                    print(f'Directory exists: {subdir}')
                else:
                    print(f'Creating directory: {subdir}')
                    os.mkdir(subdir)
        if d==work_dir:
            others = ['new_CAS_REF','new_COMPTOX_REF','new_CHEMINFO_REF']
            for oth in others:   
                subdir = os.path.join(d,oth)
                if os.path.isdir(os.path.join(subdir)):
                    print(f'Directory exists: {subdir}')
                else:
                    print(f'Creating directory: {subdir}')
                    os.mkdir(subdir)
    
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
        dir_df = dir_df[~(dir_df.filename.str[0] == '.')] # drop any "hidden" files
        # print(dir_df) 
        tocopy = ['CAS_ref_files','CompTox_ref_files','ChemInfo_ref_files',
                  'curation_files','pickles']
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
        print(f'\nLast downloaded bulk data: {get_old_repo_info(variable="FF_archive_filename")}')
         
    
    init_repo_info()
    completed()    


def get_external_files(download_ext=True,ext_dir=ext_dir):
    import urllib.request
    root = "https://storage.googleapis.com/open-ff-common/ext_data/"
    masterfn = "https://storage.googleapis.com/open-ff-common/ext_data/ext_data_master_list.csv"
    df = get_df(masterfn)
    verb = 'Connecting'
    if download_ext:
        verb = 'Transferring'
    for i,row in df[df.inc_remote=='Yes'].iterrows():
        print(f'{verb} {row.filename} as {row.ref_handle}')
        if download_ext:
            url = root+row.filename
            urllib.request.urlretrieve(url, os.path.join(ext_dir,row.filename))
        # pgm = f'{row.ref_handle} = r"{os.path.join(ext_dir,row.filename)}"'
        # exec(pgm)       
    completed()    
    # return get_ext_master_dic(masterfn)  

def download_raw_FF(download_FF=True,work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.core.fetch_new_bulk_data as fnbd
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
            
def fetch_FF_archive_files(fetch_FF_flag=False,work_dir=work_dir):
    import ff_archive_tools.archive_handler as ah

    if fetch_FF_flag:
        fn = ah.get_most_recent_archive(work_dir)
        completed(True,f'Using found file: {fn}')
        add_to_repo_info('FF_archive_filename', fn)
        return fn
    else:
        lst = os.listdir(work_dir)
        for fn in lst:
            if 'ff_archive' in fn:
                completed(True,f'using {fn} that is already saved in {work_dir}')
                add_to_repo_info('FF_archive_filename', fn)
                return fn
        completed(False,'No archive file found in work dir')
        

def create_master_raw_df(create_raw=True,in_name='testData.zip',
                         work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.core.Bulk_data_reader as bdr
    if create_raw:
        rff = bdr.Read_FF(in_name=in_name, 
                          zipdir=work_dir,workdir = work_dir,
                          origdir=orig_dir,
                          flat_pickle = 'raw_flat.parquet')
        rff.import_water_source()
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
        
def update_upload_date_file(work_dir=work_dir,orig_dir=orig_dir):
    """this routine uses the previous upload_dates file to determine the new
    disclosures. It marks the previous ones as DONE - so they will not be included
    in the next "update".  """
    import datetime
    today = datetime.datetime.today()
    datefn= os.path.join(orig_dir,'curation_files','upload_dates.parquet')
    outdf = get_df(datefn)
    # uklst = outdf.UploadKey.unique()
    disclst = outdf.DisclosureId.unique()
    
    df = get_raw_df(cols=['DisclosureId','OperatorName'])
    c = ~df.DisclosureId.isin(disclst)
    ndf = df[c].copy() # just the new ones
    
    gb = ndf.groupby('DisclosureId',as_index=False)['OperatorName'].count()
    gb['date_added'] = today.strftime("%Y-%m-%d")  # note that date_added is no longer used in pub_delay
    gb.rename({'OperatorName':'num_records'}, inplace=True,axis=1)
    print(f'Number of new disclosures added to list: {len(gb)}')
    
    outdf.weekly_report = 'DONE'
    gb['weekly_report'] = 'NO'
    outdf = pd.concat([outdf,gb],sort=True)
    # outdf.to_csv(os.path.join(work_dir,'upload_dates.csv'),index=False)
    save_df(outdf,os.path.join(work_dir,'upload_dates.parquet'))    
    
def create_difference_pickle(work_dir=work_dir, orig_dir=orig_dir):
    import pickle
    output = fads.get_difference_set(os.path.join(orig_dir,
                                                       'curation_files',
                                                       'raw_flat.parquet'),
                                          os.path.join(work_dir,
                                                       'raw_flat.parquet'))
    with open(os.path.join(work_dir,'archive_diff_dict.pkl'),'wb') as f:
        pickle.dump(output,f)
    completed()
    
    
def cas_curate_step1():
    import openFF.build.builder_tasks.CAS_master_list as casmaster
    newcas = casmaster.get_new_tentative_CAS_list(get_raw_df(cols=['CASNumber','APINumber']),
                                                  orig_dir=orig_dir,work_dir=work_dir)
    if len(newcas)>0:
        iShow(newcas)
        if len(newcas[newcas.tent_is_in_ref==False])>0:
            display(md('## Go to STEP B: Use SciFinder for `CASNumber`s not in reference already'))
        else:
            display(md('## Nothing to look up in SciFinder, but some curation necessary.  Skip to **Step XX**'))
    else:
        display(md('### No new CAS numbers to curate. '))
    completed() 
    
def cas_curate_step2(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.builder_tasks.CAS_master_list as casmaster
    import openFF.build.core.make_CAS_ref_files as mcrf
# This first part creates a new reference file that includes the new SciFinder data.
#   (we will run this again after we collect the CompTox data
    maker = mcrf.CAS_list_maker(orig_dir,work_dir)
    maker.make_partial_set()
    
    # Next we make a list of CAS records that need to be curated
    newcas = casmaster.get_new_tentative_CAS_list(get_raw_df(cols=['CASNumber','APINumber']),orig_dir=orig_dir,work_dir=work_dir)
    casmaster.make_CAS_to_curate_file(newcas,ref_dir=orig_dir,work_dir=work_dir)    
    
def cas_curate_step3(work_dir=work_dir):
    import openFF.build.builder_tasks.CAS_master_list as casmaster
    flag = casmaster.is_new_complete(work_dir)
    if flag:
        completed()
    else:
        completed(False,"More CASNumbers remain to be curated. Don't proceed until corrected")

def update_CompTox_lists(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.core.make_CAS_ref_files as mcrf
    maker = mcrf.CAS_list_maker(orig_dir,work_dir)
    maker.make_full_package()
    t = get_df(os.path.join(work_dir,"comptox_lists_table.parquet"))

    print('\nThe following list is the list of recognized CompTox chemicals.')
    print('If your new chems are NOT on the list, but you were expecting them there, \nyou may have not saved the results file correctly.')
    iShow(t[['cas_number']])
    completed()
    
def update_ChemInformatics(work_dir=work_dir,orig_dir=orig_dir):
    "generate summary file from EPA's ChemInformatics modules"
    from openFF.common.chem_info_tools import sdf_extract
    
    ci_dir = os.path.join(work_dir,'new_CHEMINFO_REF')
    lst = os.listdir(ci_dir)
    if len(lst)==0:     # if work_dir does not have CI files, copy them from orig_dir
        print(f'no files in {ci_dir}\nUsing files from current repo')
        orig_ci = os.path.join(orig_dir,'ChemInfo_ref_files')
        olst = os.listdir(orig_ci)
        for fn in olst:
            shutil.copy(os.path.join(orig_ci,fn),ci_dir)
    sdf_extract(ci_source=ci_dir,out_dir=work_dir)
    
def casing_step1(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.builder_tasks.CAS_2_build_casing as cas2
    import openFF.build.builder_tasks.IngName_curator as IngNc
    
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
        
def casing_step2(work_dir=work_dir,orig_dir=orig_dir):
    import datetime
    Today = datetime.datetime.today().strftime('%Y-%m-%d')
    try:
        modified = pd.read_csv(os.path.join(work_dir,'casing_modified.csv'),
                               keep_default_na=False)
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
    
def casing_step3(work_dir=work_dir):
    import openFF.build.builder_tasks.CAS_2_build_casing as cas2
    completed(cas2.is_casing_complete(get_raw_df(cols=['CASNumber','IngredientName']),work_dir))
    
def companies_step1(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.builder_tasks.CompanyNames_make_list as complist
    companies = complist.add_new_to_Xlate(get_raw_df(['CASNumber','OperatorName',
                                                      'Supplier','DisclosureId','year']),
                                          ref_dir=orig_dir,out_dir=work_dir)
    
    completed()
    iShow(companies.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}],
         classes="display compact cell-border", scrollX=True)  
    
def companies_step2(work_dir=work_dir):
    import openFF.build.builder_tasks.CompanyNames_make_list as complist
    completed(complist.is_company_complete(work_dir))

def purposes_step1(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.builder_tasks.Purpose_make_list as purplist
    purposes = purplist.add_new_to_Xlate(get_raw_df(['CASNumber','Purpose',
                                                      'DisclosureId','year']),
                                          ref_dir=orig_dir,out_dir=work_dir)
    
    completed()
    iShow(purposes.reset_index(drop=True),maxBytes=0,columnDefs=[{"width": "100px", "targets": 0}],
         classes="display compact cell-border", scrollX=True)  
    
def purposes_step2(work_dir=work_dir):
    import openFF.build.builder_tasks.Purpose_make_list as purplist
    completed(purplist.is_purpose_complete(work_dir))
 
def location_step1(work_dir=work_dir,orig_dir=orig_dir,ext_dict=''):
    import openFF.build.builder_tasks.Location_cleanup as loc_clean
    locobj = loc_clean.Location_ID(get_raw_df(['api10','Latitude','Longitude',
                                              'Projection','DisclosureId',
                                            #   'StateNumber','CountyNumber',
                                              'StateName','CountyName']),
                                   ref_dir=orig_dir,out_dir=work_dir,ext_dir=ext_dir)
    _ = locobj.clean_location()
    completed()
    
def location_step2(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.builder_tasks.Location_cleanup as loc_clean
    locobj = loc_clean.Location_ID(get_raw_df(),ref_dir=orig_dir,out_dir=work_dir)
    completed(locobj.is_location_complete())
    
def carrier_step(work_dir=work_dir,orig_dir=orig_dir):
    import openFF.build.builder_tasks.Carrier_1_identify_in_new as car1
    
    carobj = car1.Carrier_ID(get_raw_df(cols=['CASNumber','IngredientName','DisclosureId','APINumber',
                                              'PercentHFJob','TotalBaseWaterVolume','date',
                                              'Purpose','IngredientsId','TradeName','MassIngredient']),
                             ref_dir=orig_dir,out_dir=work_dir)
    completed(carobj.create_full_carrier_set())
    
def builder_step1(final_dir=final_dir,work_dir=work_dir,orig_dir=orig_dir):
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
    
    cdir = os.path.join(work_dir,'new_CHEMINFO_REF')
    fdir = os.path.join(final_dir,"ChemInfo_ref_files")
    shutil.copytree(src=cdir,dst=fdir,dirs_exist_ok=True)
    
    # get files from orig_dir
    files = [
             'missing_values.csv',
             'new_state_county_ref.csv',
             'IngName_non-specific_list.parquet',
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
             'purpose_xlate.parquet',
             'location_curated.parquet',
             'disclosureId_ref.parquet', 
             'upload_dates.parquet',
             'CI_sdf_summary.parquet',
             'ws_flat.parquet',
             'raw_flat.parquet',
             'archive_diff_dict.pkl',
             'pub_delay_df.parquet'
             ]
    for fn in files:
        shutil.copy(os.path.join(work_dir,fn),
                    os.path.join(final_dir,'curation_files',fn))
        
def builder_step2(final_dir=final_dir,ext_dir=ext_dir,ext_dict=''):
    # data_set_constructor
    import openFF.build.core.Data_set_constructor as dsc
    
    dataobj = dsc.Data_set_constructor(rawdf=get_raw_df(),
                                       waterdf=get_water_source_df(),
                                       ref_dir=final_dir,
                                       out_dir=final_dir,
                                       extdir=ext_dir)
    _ = dataobj.create_full_set()
    completed()  
    
def builder_step3(final_dir=final_dir):
    # create parquet data set and run tests
    import openFF.build.core.Analysis_set as a_set
    import openFF.build.core.Tests_of_final as tof

    df = a_set.make_full_set_file(sources=final_dir,outdir=final_dir)

    # run tests
    print('Performing tests')
    tests = tof.final_test(df)
    tests.run_all_tests()
    completed()

    
def create_issues_data_set(final_dir=final_dir):
    import FF_issues.flag_issues as fi
    import numpy as np

    print('assembling tables of FracFocus flaws')
    df = get_df(os.path.join(final_dir,'full_df.parquet'))
    cas_curated = get_df(os.path.join(final_dir,'curation_files','cas_curated.parquet'))

    obj = fi.Flag_issues(df=df,cas_curated=cas_curated,
                         out_dir=final_dir)
    obj.detect_all_issues()
    print(' -- issues detected, now compiling flag fields')
    obj.add_summary_fields()

    print(' -- merging flag fields with full data set.')
    disc_df = pd.read_parquet(os.path.join(final_dir,'disclosure_issues.parquet'))
    dwarn = disc_df.d_flags.unique().tolist()
    warn_df = obj.get_max_warning_as_df(dwarn)

    df = df.merge(disc_df[['DisclosureId','d_flags']],on='DisclosureId',how='left',validate='m:1')
    df = df.merge(warn_df[['flag_combo','max_level']],left_on='d_flags',right_on='flag_combo',
                  how='left',validate='m:1')
    df = df.rename({'max_level':'max_d_warning'},axis =1)

    df.d_flags = df.d_flags.fillna('')
    df.max_d_warning = df.max_d_warning.fillna('')
    df = df.drop('flag_combo',axis=1)

  
    rec_df = pd.read_parquet(os.path.join(final_dir,'record_issues.parquet'))
    rwarn = rec_df.r_flags.unique().tolist()
    warn_df = obj.get_max_warning_as_df(rwarn)

    df = df.merge(rec_df[['reckey','r_flags']],on='reckey',how='left',validate='m:1')
    df = df.merge(warn_df[['flag_combo','max_level']],left_on='r_flags',right_on='flag_combo',
                  how='left',validate='m:1')
    df = df.rename({'max_level':'max_r_warning'},axis =1)

    df.r_flags = df.r_flags.fillna('')
    df.max_r_warning = df.max_r_warning.fillna('')
    df = df.drop('flag_combo',axis=1)

    df.to_parquet(os.path.join(final_dir,'full_df.parquet'))
    
def make_repository(create_zip=False,final_dir=final_dir):
    directories = []
    filenames = []
    import shutil
    repo_name = 'final_repo_new'
    repodir = os.path.join(final_dir,repo_name)
    
    try:
        os.mkdir(repodir)
    except:
        print(f'{repodir} already exists or other problem creating directory')

    dirs = ['CAS_ref_files','CompTox_ref_files','ChemInfo_ref_files',
            'curation_files','pickles']

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
            if item[0]=='.':  # ignore caches
                continue
            directories.append(d)
            filenames.append(item)

    # # get a copy of the code used
    # cdir = os.path.join(repodir,'intg_support')
    # shutil.copytree(code_dir,cdir,dirs_exist_ok=True)
    # dlst = os.listdir(cdir)
    # for item in dlst:
    #     directories.append('intg_support')
    #     filenames.append(item)
            

    # Other files to copy
    shutil.copy(os.path.join(work_dir,'repo_info.csv'),repodir)
    directories.append('')
    filenames.append('repo_info.csv')

    shutil.copy(os.path.join(work_dir,'raw_flat.parquet'),repodir)
    directories.append('')
    filenames.append('raw_flat.parquet')

    shutil.copy(os.path.join(final_dir,'full_df.parquet'),repodir)
    directories.append('')
    filenames.append('full_df.parquet')
    
    shutil.copy(os.path.join(final_dir,'working_df.parquet'),repodir)
    directories.append('')
    filenames.append('working_df.parquet')

    shutil.copy(os.path.join(final_dir,'disclosure_issues.parquet'),repodir)
    directories.append('')
    filenames.append('disclosure_issues.parquet')

    shutil.copy(os.path.join(final_dir,'record_issues.parquet'),repodir)
    directories.append('')
    filenames.append('record_issues.parquet')

    arcv_fn =  get_new_repo_info(variable='FF_archive_filename')
    shutil.copy(os.path.join(work_dir,arcv_fn),
                os.path.join(repodir, arcv_fn))    
    directories.append('')
    filenames.append(arcv_fn)
    
    dir_df = pd.DataFrame({'directory':directories,'filename':filenames})
    dir_df.to_csv(os.path.join(repodir,'dir_list.csv'))
    
    if create_zip:
        print('Making zip archive...')
        completed(shutil.make_archive(repodir, 'zip', repodir)) 
    else:
        print('Skipping zip archive creation')
        completed()