# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:53:33 2023

@author: garya

Helper routines to handle common text tasks throughout open-ff -
often in relation to getting a url or displaying in HTML.

"""
import os
from math import log10
import openFF.common.handles as hndl

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
        preamble = hndl.browser_root
    s = f'{preamble}{cas}/analysis_{cas}.html'
    return wrap_URL_in_html(s,text_to_show)

def getOpLink(opname,text_to_show='Operator details',
              use_remote=False, up_level=False):
    preamble = ''
    oneword = opname.replace(' ','_')
    if up_level:
        preamble = '../'
    if use_remote: # this should trump up_level
        preamble = hndl.browser_root
    s = f'{preamble}operators/{oneword}.html'
    return wrap_URL_in_html(s,text_to_show)

def getStateLink(state,text_to_show='State details',use_remote=False):
    preamble = 'states/'
    if use_remote:
        preamble = hndl.browser_root+'states/'
    s = f'{preamble}{state.lower()}.html'
    return wrap_URL_in_html(s,text_to_show)

def getBlogStateLink(state,text_to_show='Link to state summary'):
    s = f'https://storage.googleapis.com/open-ff-browser/states/{state}.html'
    return wrap_URL_in_html(s,text_to_show)

def getCountyLink(county,state,text_to_show='County details',use_remote=False):
    preamble = './' # when coming from a state link, don't need preamble
    if use_remote:
        preamble = hndl.browser_root+'states/'
    name = county.lower().replace(' ','_') + '-' + state.lower().replace(' ','_')
    s = f'{preamble}{name}.html'    
    return wrap_URL_in_html(s,text_to_show)

def getFlawLink(flaw_id,text_to_show='',use_remote=False):
    if text_to_show=='':
        text_to_show = flaw_id
    preamble = 'flaws/'
    if use_remote:
        preamble = hndl.browser_root+'flaws/'
    s = f'{preamble}Issue_{flaw_id}.html'
    return wrap_URL_in_html(s,text_to_show)

# def getDataLink(cas):
#     s = f'{cas}/data.zip'
#     return wrap_URL_in_html(s,'data; ')

def getMapLink(row, txt='',latname='bgLatitude',lonname='bgLongitude'):
    lnk = f'https://maps.google.com/maps?q={row[latname]},{row[lonname]}&t=k'
    return wrap_URL_in_html(lnk,txt)

def getAPILink(row, txt='',latname='bgLatitude',lonname='bgLongitude'):
    lnk = f'https://maps.google.com/maps?q={row[latname]},{row[lonname]}&t=k'
    return wrap_URL_in_html(lnk,row.APINumber)

def getFFLink(row, txt='',fmt=''):
    # link to the FF disclosure with the (default) text as the APINumber
    lnk = f'https://www.fracfocus.org/wells/{row.APINumber}'
    if txt=='':
        if fmt == 'short':
            txt = row.APINumber[:10]
        elif fmt == 'dashed':
            txt = row.APINumber[:2]+'-'+row.APINumber[2:5]+'-'+row.APINumber[5:10]
        else:
            txt = row.APINumber
            
    return wrap_URL_in_html(lnk,txt)

def getAPIListLink(api10,txt='Link to disclosure list'):
    url = f'{hndl.browser_api_links_dir}{api10}'
    return wrap_URL_in_html(url,txt)

def getDisclosureLink(APINumber,disclosureid,text_to_show='disclosure',
                      use_remote=False,up_level=True,
                      check_if_exists=False):  
    import requests      
    preamble = ''
    if up_level:
        preamble = '../'
    if use_remote: # this should trump up_level
        preamble = hndl.browser_root
    APINumber = str(APINumber)
    api5 = APINumber.replace('-','')[:5]
    s =  f'{preamble}disclosures/{api5}/{disclosureid}.html'
    if check_if_exists:
        r = requests.head(s)
        if r.status_code != 200:
            return ' ' # doesn't exist so return empty
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

def getMoleculeImg(cas,size=120,use_remote=False,link_up_level=0,
                   alt=None):
    # returns an html image link
    prefix = ''
    if link_up_level:
        for i in range(link_up_level):
            prefix += '../'
    if use_remote: # override link_up_level
        prefix = hndl.browser_root
    if alt:
        alttext = alt
    else:
        alttext = f'Molecular structure of {cas}'
    # if chemical_report: prefix='../'
    ct_path = os.path.join(hndl.pic_dir,cas,'comptoxid.png')
    # print(ct_path)
    # take comptox version if it exists
    if os.path.exists(ct_path):
        # and is not empty:  # this is the normal return
        if os.path.getsize(ct_path) > 0:
            # print('got it')
            return f"""<center><img src="{prefix}images/{cas}/comptoxid.png" alt="{alttext}" onerror="this.onerror=null; this.remove();" width="{size}"></center>"""
    else: # but if all else fails, try linking ot chemid
        # print('ct_path didt exist')
        ci_path = os.path.join(hndl.pic_dir,cas,'chemid.png')
        if os.path.exists(ci_path):
            if os.path.getsize(ci_path) > 0:
                return f"""<center><img src="{prefix}images/{cas}/chemid.png" alt="{alttext}" onerror="this.onerror=null; this.remove();" width="{size}"></center>"""
    return "<center>Image not available</center>"

def getFingerprintImg(cas,size=140,alt=None):
    # returns an html image link when possible
    # check if we have it locally, but link to the cloud version
    fp_path = os.path.join(hndl.pic_dir,cas,'haz_fingerprint.png')
    # take comptox version if it exists
    cas_ignore = ['7732-18-5','proprietary','conflictingID',
                  'ambiguousID','sysAppMeta','cas_not_assigned']
    if alt:
        alttext = alt
    else:
        alttext = f'EPA Cheminformatics classifications of {cas}'

    if cas in cas_ignore:
        return ' <center>---</center> '
    if os.path.exists(fp_path):
        return f"""<center><img src="https://storage.googleapis.com/open-ff-browser/images/{cas}/haz_fingerprint.png" alt="{alttext}"  onerror="this.onerror=null; this.remove();" width={size}></center>"""
    return "<center>ChemInformatics not available</center>"
    
    
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
            return round(x, sig-int(floor(log10(abs(x))))-1)
    except: 
        if guarantee_str:
            return guarantee_str
        return x
    

