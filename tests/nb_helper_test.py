# tests for nb_helper.py
import sys
import os
sys.path.insert(0,'c:/MyDocs/integrated/openFF') # adjust to your setup


from common.nb_helper import *
simp_url = "https://storage.googleapis.com/open-ff-common/test_fixtures/simple_df.parquet"
simp_fn = os.path.join('test_fixture','simp_df.parquet')

def test_file_size():
    assert get_size_of_url_file(simp_url)==15053

def test_mkdir():
    assert os.path.exists('test_fixture')==False
    make_sandbox('test_fixture')    
    assert os.path.exists('test_fixture')==True
    
def test_fetch_df_from_file():
    df = get_df_from_file(simp_url,simp_fn)
    assert df.shape == (7,20)
    
def test_remove_fixture():
    import shutil
    shutil.rmtree('test_fixture')
    assert os.path.exists('test_fixture')==False
    