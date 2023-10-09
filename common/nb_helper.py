import pandas as pd
#import numpy as np
import requests
import urllib
import os

#################### general utilities  ########################
def is_remote():
    # check if we are not working on a known local machine
    import platform
    locals = ['Dell_2023_Gary']
    if platform.node() in locals:
        return False
    return True

def show_done(txt='Completed'):
    print(txt)

def make_sandbox(name='sandbox'):
    # make output location
    try:
        os.mkdir(name)
    except:
        print(f'{name} already exists')

