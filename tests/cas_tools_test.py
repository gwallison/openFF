# tests for cas_tools.py
import sys
# import os
sys.path.insert(0,'c:/MyDocs/integrated/openFF') # adjust to your setup


from build.core.cas_tools import *

def test_is_valid_CAS_code():
    assert is_valid_CAS_code(1234)==False
    assert is_valid_CAS_code('50-00-0')==True
    assert is_valid_CAS_code('50-0-0')==False
    assert is_valid_CAS_code('50-00-1')==False
    assert is_valid_CAS_code('050-00-0')==False
    assert is_valid_CAS_code('50000')==False
    assert is_valid_CAS_code('50-00-0b')==False
    assert is_valid_CAS_code('1004542-84-0')==True
    
def test_cleanup_cas():
    assert cleanup_cas('50-00-0') == '50-00-0'
    assert cleanup_cas('050-00-0') == '50-00-0'
    assert cleanup_cas('00050-00-0') == '50-00-0'
    assert cleanup_cas('50-0-0') == '50-00-0'
    assert cleanup_cas('a50a-0d0-0f') == '50-00-0'
    assert cleanup_cas('50-00-0!') == '50-00-0'
    assert cleanup_cas('5000-0') == '5000-0' # can't fix
    assert cleanup_cas('-50-00-0') == '-50-00-0' # can't fix
    

    

