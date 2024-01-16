""" """

import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import shutil, os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import openFF.common.handles as hndl 

import openFF.browser.gen_disclosures as gen_disc
import openFF.browser.gen_chemicals as gen_chem
import openFF.browser.gen_misc_nb as gen_misc_nb
import openFF.browser.gen_scope as gen_scope

def erase_output_space(dir = hndl.browser_out_dir):
    # CAREFUL: This removes everything the the browser_out_dir!
    shutil.rmtree(dir,ignore_errors=True)
    os.mkdir(dir)

def init_output_space(dir = hndl.browser_out_dir):
    dirs = [hndl.browser_inc_dir,hndl.browser_states_dir,
            hndl.browser_operators_dir,hndl.browser_disclosures_dir]
    erase_output_space(dir)
    for dir in dirs:
        os.mkdir(dir)
    try:
        shutil.copytree(hndl.pic_dir, hndl.image_dir)
    except:
        print('image directory not copied, already exists?')
            # shutil.copyfile(self.css_fn,
            #                 os.path.join(self.outdir,'style.css'))

    


 


if __name__ == '__main__':
    # c = input("Type 'erase' if you want to clear the output dir before starting, otherwise <enter> > ")
    # if c == 'erase':
    #     print(f'Initializing {hndl.browser_out_dir}')
    #     init_output_space()

    #_ = gen_chem.Chem_gen()
    # _ = gen_disc.Disc_gen()
    _ = gen_scope.ScopeGen()
    # _ = gen_misc_nb.Misc_notebook_gen()
    print('DONE')