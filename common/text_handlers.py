# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:53:33 2023

@author: garya

Helper routines to handle common text tasks throughout open-ff -
often in relation to getting a url or displaying in HTML.

"""
import os
from math import log10

pic_dir = r"C:\MyDocs\OpenFF\src\openFF-catalog\pic_dir"

def sort_id(st):
    l = list(st)
    l.sort()
    return l

def wrap_URL_in_html(link,txtToShow='MAP'):
    return f'<a href="{link}" target="_blank" >{txtToShow}</a>'

def getCatLink(cas,text_to_show='Analysis',use_remote=False):
    preamble = ''
    if use_remote:
        preamble = 'https://storage.googleapis.com/open-ff-browser/'
    s = f'{preamble}{cas}/analysis_{cas}.html'
    return wrap_URL_in_html(s,text_to_show)

def getDataLink(cas):
    s = f'{cas}/data.zip'
    return wrap_URL_in_html(s,'data; ')

def getPubChemLink(cas):
    try:
        if cas[0].isnumeric():
            s = f'https://pubchem.ncbi.nlm.nih.gov/#query={cas}'
            return wrap_URL_in_html(s,'PubChem; ')
    except:
        pass
    return ''

def getFingerprintImg(cas):
    fp_path = os.path.join(pic_dir,cas,'haz_fingerprint.png')
    # take comptox version if it exists
    if os.path.exists(fp_path):
        return f"""<center><img src="https://storage.googleapis.com/open-ff-browser/images/{cas}/haz_fingerprint.png" onerror="this.onerror=null; this.remove();" width="200"></center>"""
    return "<center>ChemInformatics not available</center>"
    
def getFingerprintStatus(cas):
    #!!!!! Doesn't work for colab - need to pull from storage, not local
    fp_path = os.path.join(pic_dir,cas,'haz_fingerprint.png')
    # take comptox version if it exists
    if os.path.exists(fp_path):
        return 'Yes'
    return 'No'
    
def getCompToxRef(DTXSID):
    #return DTXSID   
    try:
        if DTXSID[:3] == 'DTX':
            s = f'https://comptox.epa.gov/dashboard/dsstoxdb/results?search={DTXSID}'
            return wrap_URL_in_html(s,'CompTox')
    except:
        pass
    return ""


def xlate_to_str(inp,sep='; ',trunc=False,tlen=20,totallen = 5000,sort=True,
                maxlen=10000,maxMessage='Too many items to display'):
    """used to translate a list into a meaningful string for display"""
    try:
        if isinstance(inp,str):
            inp = [inp]
        l = list(inp)
        if sort:
            l.sort()
        if len(l)>maxlen:
            return maxMessage

        out = ''
        for a in l:
            s = str(a)
            if trunc:
                if len(s)>tlen:
                    s = s[:tlen-3]+ '...'
            out+= s+sep
        out = out[:-(len(sep))]
    except:
        return ''
    if len(out)>totallen:
        out = out[:totallen]+' ...' 
    return out

def round_sig(x, sig=2):
    try:
        if abs(x)>=1:
            out =  int(round(x, sig-int(floor(log10(abs(x))))-1))
            return f"{out:,d}" # does the right thing with commas
        else: # fractional numbers
            return str(round(x, sig-int(floor(log10(abs(x))))-1))
    except:
        return x
    
