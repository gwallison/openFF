import pandas as pd
import numpy as np
import os

out_dir = 'sandbox'


def is_remote():
    import platform
    locals = ['Dell_2023_Gary']
    if platform.node() in locals:
        return False
    return True

def make_sandbox(name=out_dir):
    # make output location
    tmp_dir = name
    try:
        os.mkdir(name)
    except:
        print(f'{name} already exists')
        