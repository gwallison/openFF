# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 18:55:49 2023

@author: garya
"""

import requests
import os
from datetime import datetime
from hashlib import sha256  # use to detect when downloads are identical


a_prefix = 'ff_archive_'

def get_most_recent_archive(sources='./sources/'):
    lst = os.listdir(sources)
    filtered = list(filter(lambda fn: fn[:len(a_prefix)] == a_prefix, lst))
    if len(filtered)>0:
        return os.path.join(sources,max(filtered))
    return

def files_are_same(newfn,lastfn):
    with open(newfn,'rb') as f:
        newsig = sha256(f.read()).hexdigest()
    with open(lastfn,'rb') as f:
        lastsig = sha256(f.read()).hexdigest()
    return newsig==lastsig


def check_lengths(newfn,lastfn):
    if lastfn==None:
        print('No archived data to compare against; skipping comparison.')
        return True
    if files_are_same(newfn,lastfn):
        print('Current download is identical to last archive; processing not necessary')
        return False
    nlen = os.path.getsize(newfn)
    olen = os.path.getsize(lastfn)
    if nlen<olen:
        print('\n**********\nWARNING: new download is smaller that last archive. Possible corrupted file.')
        print(f'       new={nlen}  vs. last={olen}\n*********\n')
        return False
    else:
        print('New archive looks ok so far...')
        return True

def store_FF_bulk(newdir='./newdir/',sources = './sources/',
                  archive=True, warn=True):
    tempfn = os.path.join(newdir,'testData.zip')
    today = datetime.today()

    url = 'http://fracfocusdata.org/digitaldownload/fracfocuscsv.zip'
    #url = 'https://storage.googleapis.com/open-ff-browser/100-42-5/data.zip'
    # url = 'https://storage.googleapis.com/open-ff-browser/100-42-5/analysis_100-42-5.html'
    print(f'Downloading FracFocus data from {url}')
    r = requests.get(url, allow_redirects=True,timeout=20.0)
    open(tempfn, 'wb').write(r.content)
    
    if warn:
        if check_lengths(tempfn,get_most_recent_archive(sources))==False:
            return False
        
    if archive:
        afn = os.path.join(newdir,f'{a_prefix}{today.strftime("%Y-%m-%d")}.zip')
        open(afn, 'wb').write(r.content)
        print(f'Archive saved as: {afn}')
    return True

if __name__ == '__main__':
    store_FF_bulk()
