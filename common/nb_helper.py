import pandas as pd
#import numpy as np
# import requests
# import urllib
import os

#################### general utilities  ########################

# def show_done(txt='Completed'):
#     print(txt)

def make_sandbox(name='sandbox'):
    # make output location
    try:
        os.mkdir(name)
    except:
        print(f'{name} already exists')

def clr_cell(txt='Cell Completed', color = '#669999'):
    import datetime    
    from IPython.display import display
    from IPython.display import Markdown as md

    t = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    s = f"""<div style="background-color: {color}; padding: 10px; border: 1px solid green;">"""
    s+= f'<h3> {txt} </h3> {t}'
    s+= "</div>"
    display(md(s))

def completed(status=True,txt=''):
    if txt =='':
        if status:
            txt = 'This step completed normally.'
        else:
            txt ='Problems encountered in this cell! Resolve before continuing.' 
    if status:
        clr_cell(txt)
    else:
        clr_cell(txt,color='#ff6666')
