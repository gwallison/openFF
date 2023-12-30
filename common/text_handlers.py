# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:53:33 2023

@author: garya

Helper routines to handle common text tasks throughout open-ff -
often in relation to getting a url or displaying in HTML.

"""
import os
from math import log10
from openFF.common.handles import pic_dir

# pic_dir = r"C:\MyDocs\OpenFF\src\openFF-catalog\pic_dir"

def sort_id(st):
    l = list(st)
    l.sort()
    return l

def wrap_URL_in_html(link,txtToShow='MAP'):
    return f'<a href="{link}" target="_blank" >{txtToShow}</a>'

def make_clickable(val):
    try:
        if val[:4]=='http':
            return '<a href="{}" target="_blank">{}</a>'.format(val,'map')
    except:
        return val
    return val

# def getLink(row,latname='bgLatitude',lonname='bgLongitude'):
#     return ggmap.getSearchLink(row[latname],row[lonname])
# #    return ggmap.getSearchLink(row.bgLatitude,row.bgLongitude)

def getCatLink(cas,text_to_show='Analysis',use_remote=False):
    preamble = ''
    if use_remote:
        preamble = 'https://storage.googleapis.com/open-ff-browser/'
    s = f'{preamble}{cas}/analysis_{cas}.html'
    return wrap_URL_in_html(s,text_to_show)

# def getOpLink(opname,text_to_show='Operator details',use_remote=False,up_level=False):
#     preamble = ''
#     if use_remote:
#         preamble = 'https://storage.googleapis.com/open-ff-browser/'
#     if up_level:
#         preamble = '../'
#     s = f'{preamble}operators/{opname}.html'
#     return ggmap.wrap_URL_in_html(s,text_to_show)

# def getStateLink(state,text_to_show='State details',use_remote=False):
#     preamble = 'states'
#     if use_remote:
#         preamble = 'https://storage.googleapis.com/open-ff-browser/states/'
#     s = f'{preamble}/{state.lower()}.html'
#     return ggmap.wrap_URL_in_html(s,text_to_show)

# def getCountyLink(county,state,text_to_show='County details',use_remote=False):
#     preamble = '.' # when coming from a state link, don't need preamble
#     if use_remote:
#         preamble = 'https://storage.googleapis.com/open-ff-browser/states/'
#     name = county.lower().replace(' ','_') + '-' + state.lower().replace(' ','_')
#     # s = f'{preamble}/{name}.csv'
#     s = f'{preamble}/{name}.html'
#     return ggmap.wrap_URL_in_html(s,text_to_show)

def getDataLink(cas):
    s = f'{cas}/data.zip'
    return wrap_URL_in_html(s,'data; ')

def getMapLink(row, txt='',latname='bgLatitude',lonname='bgLongitude'):
    lnk = f'https://maps.google.com/maps?q={row[latname]},{row[lonname]}&t=k'
    return wrap_URL_in_html(lnk,txt)

def getAPILink(row, txt='',latname='bgLatitude',lonname='bgLongitude'):
    lnk = f'https://maps.google.com/maps?q={row[latname]},{row[lonname]}&t=k'
    return wrap_URL_in_html(lnk,row.APINumber)

def getDisclosureLink(APINumber,uploadkey,text_to_show='disclosure',
                      use_remote=False,up_level=True):
    preamble = ''
    if use_remote:
        preamble = 'https://storage.googleapis.com/open-ff-browser/'
    if up_level:
        preamble = '../'
    APINumber = str(APINumber)
    api5 = APINumber.replace('-','')[:5]
    s =  f'{preamble}disclosures/{api5}/{uploadkey}.html'
    return wrap_URL_in_html(s,text_to_show)    

# def getMapLink(lat=51.477222,lon=0):
#     return f'https://www.google.com/maps/@?api=1&map_action=map&center={lat},{lon}&basemap=satellite'

# def wrapLink(url,txt):
#     # simple wrapping to make a link displayable in notebook
#     return ggmap.wrap_URL_in_html(url,txt)

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
    cas_ignore = ['7732-18-5','proprietary','conflictingID','ambiguousID','sysAppMeta']
    if cas in cas_ignore:
        return ' <center>---</center> '
    if os.path.exists(fp_path):
        return f"""<center><img src="https://storage.googleapis.com/open-ff-browser/images/{cas}/haz_fingerprint.png" onerror="this.onerror=null; this.remove();" width="100"></center>"""
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

from math import log10, floor
def round_sig(x, sig=2,guarantee_str=''):
    try:
        if abs(x)>=1:
            out =  int(round(x, sig-int(floor(log10(abs(x))))-1))
            return f"{out:,d}" # does the right thing with commas
        else: # fractional numbers
            return str(round(x, sig-int(floor(log10(abs(x))))-1))
    except: 
        if guarantee_str:
            return guarantee_str
        return x
    

