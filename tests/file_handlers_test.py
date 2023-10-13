# tests for nb_helper.py
import sys
import os
sys.path.insert(0,'c:/MyDocs/integrated') # adjust to your setup


from openFF.common.file_handlers import *
from openFF.common.nb_helper import make_sandbox

simp_url = "https://storage.googleapis.com/open-ff-common/test_fixtures/simple_df.parquet"
simp_fn = os.path.join('test_fixture','simp_df.parquet')

workdir = 'test_fixture'
make_sandbox(workdir)

def test_file_size():
    assert get_size_of_url_file(simp_url)==15053
    
def test_fetch_df_from_url():
    df = get_df_from_url(simp_url,simp_fn)
    assert df.shape == (7,20)


def test_remove_fixture():
    import shutil
    shutil.rmtree(workdir)
    assert os.path.exists(workdir)==False
    
