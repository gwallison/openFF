""" """

import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from openFF.common.handles import repo_name,  data_source 
from openFF.common.handles import browser_out_dir

import openFF.browser.gen_disclosures as gen_disc

_ = gen_disc.Disc_gen()

if __name__ == '__main__':
    print('ran it')