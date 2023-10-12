# tests for nb_helper.py
import sys
import os
sys.path.insert(0,'c:/MyDocs/integrated/openFF') # adjust to your setup


from common.nb_helper import *
simp_url = "https://storage.googleapis.com/open-ff-common/test_fixtures/simple_df.parquet"
simp_fn = os.path.join('test_fixture','simp_df.parquet')


def test_mkdir():
    assert os.path.exists('test_fixture')==False
    make_sandbox('test_fixture')    
    assert os.path.exists('test_fixture')==True
    
   
def test_remove_fixture():
    import shutil
    shutil.rmtree('test_fixture')
    assert os.path.exists('test_fixture')==False
    
