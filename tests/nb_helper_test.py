# tests for nb_helper.py
import sys
sys.path.insert(0,'c:/MyDocs/integrated/openFF') # adjust to your setup
from common.nb_helper import *
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4