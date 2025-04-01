""" """

import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import shutil, os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import openFF.common.handles as hndl 
import openFF.common.file_handlers as fh 
import openFF.common.text_handlers as th 
import openFF.common.nb_helper as nbh

import openFF.browser.gen_disclosures as gen_disc
import openFF.browser.gen_disc_links as gen_disc_links
import openFF.browser.gen_chemicals as gen_chem
import openFF.browser.gen_states as gen_states
import openFF.browser.gen_operators as gen_operators
import openFF.browser.gen_flaws as gen_flaws
import openFF.browser.gen_misc_nb as gen_misc_nb
import openFF.browser.gen_scope as gen_scope

####
testing_mode = False
remake_workingdf = True
use_archive_diff = True # when True, only builds pages that have changed since last build
arc_diff = hndl.archive_diff_pkl
####

def erase_output_space(dir = hndl.browser_out_dir):
    # CAREFUL: This removes everything the the browser_out_dir!
    shutil.rmtree(dir,ignore_errors=True)
    os.mkdir(dir)

def init_output_space(dir = hndl.browser_out_dir):
    dirs = [hndl.browser_inc_dir,hndl.browser_states_dir,
            hndl.browser_operators_dir,hndl.browser_flaws_dir,
            hndl.browser_disclosures_dir,hndl.browser_api_links_dir,
            # hndl.browser_image_dir
            ]
    erase_output_space(dir)
    for dir in dirs:
        os.mkdir(dir)
    # try:
    shutil.copytree(hndl.pic_dir, hndl.browser_image_dir)
    # except:
    #     print('image directory not copied, already exists?')
            # shutil.copyfile(self.css_fn,
            #                 os.path.join(self.outdir,'style.css'))

    
def prep_working_df(testing_mode=testing_mode, remake_workingdf=remake_workingdf):
    if remake_workingdf:        
        if testing_mode:
            if remake_workingdf:
                print('-- creating new test workingdf')
                df = fh.get_df(os.path.join(hndl.curr_repo_dir,'full_df.parquet'))
                c3 = df.bgCAS.isin(['1319-33-1','50-00-0'])#,'proprietary','7732-18-5','71-43-2','non_chem_record','ambiguousID'])
                c2 = df.bgCountyName == 'monroe'
                c1 = df.bgStateName == 'ohio'
                c4 = df.bgOperatorName.isin(['antero','eclipse resources'])
                df = df[c1 & c2 & c4]
                # df = df[c4 & c1]
                df.to_parquet(os.path.join(hndl.sandbox_dir,'test_df.parquet'))
            workdf = fh.get_df(os.path.join(hndl.sandbox_dir,'test_df.parquet'))
        else:
            workdf = fh.get_df(os.path.join(hndl.curr_repo_dir,'full_df.parquet'))
        ########## Lots of add-ins...
        # percent of valid cas that are proprietary (disclosure level)
        workdf['is_proprietary'] = workdf.bgCAS=='proprietary'
        gb1 = workdf.groupby('DisclosureId',as_index=False)[['is_proprietary','is_valid_cas']].sum()
        gb1.fillna(0,inplace=True)
        gb1['perc_proprietary'] = gb1.is_proprietary/gb1.is_valid_cas *100
        workdf = workdf.merge(gb1[['DisclosureId','perc_proprietary']],
                            on='DisclosureId',how='left',validate='m:1')
        # add easy to use links
        gb2 = workdf.groupby('APINumber', as_index=False).size()
        gb2['FF_disc'] = gb2.apply(lambda x: th.getFFLink(x),axis=1)
        workdf = workdf.merge(gb2[['APINumber','FF_disc']], on='APINumber',
                              how='left',validate='m:1')

      
        fh.save_df(workdf,(os.path.join(hndl.sandbox_dir,'workdf.parquet'))) # for the indexes
    else:
        workdf = fh.get_df(os.path.join(hndl.sandbox_dir,'workdf.parquet'))
    return workdf


if __name__ == '__main__':
    c = input("Enter 'erase' to clear the output dir before starting, otherwise <enter> > ")
    if c == 'erase':
        print(f'Initializing {hndl.browser_out_dir}')
        init_output_space()
    nbh.make_sandbox()
    workingdf = prep_working_df()
    # print(workingdf.columns)
    #workingdf = workingdf[workingdf.bgCAS=='100-79-8']
    #_ = gen_chem.Chem_gen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    # _ = gen_states.State_gen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    # _ = gen_operators.Operator_gen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    _ = gen_flaws.FF_flaws_gen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    # _ = gen_disc.Disc_gen(workingdf,arc_diff,use_archive_diff=use_archive_diff)
    # _ = gen_disc_links.Disc_link_gen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    # _ = gen_scope.ScopeGen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    # _ = gen_misc_nb.MiscNbGen(workingdf) #,arc_diff,use_archive_diff=use_archive_diff)
    print('DONE')