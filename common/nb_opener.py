import pandas as pd
import numpy as np
import os

def is_remote():
    import platform
    locals = ['Dell_2023_Gary']
    if platform.node() in locals:
        return False
    return True

# make output location
tmp_dir = 'sandbox'
try:
    os.mkdir(tmp_dir)
except:
    print(f'{tmp_dir} already exists')