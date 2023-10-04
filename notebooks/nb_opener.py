import platform
import sys

def is_remote():
    locals = ['Dell_2023_Gary']
    if platform.node() in locals:
        return False
    return True

if is_remote():
    sys.path.insert(0,'../')
else:
    sys.path.insert(0,'../')

# make output location
# this code may overwrite files in the "sandbox" directory.  Make sure you want to do that
import os
tmp_dir = 'sandbox'
try:
    os.mkdir(tmp_dir)
except:
    print(f'{tmp_dir} already exists')