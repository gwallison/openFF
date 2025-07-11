# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 14:23:01 2022

@author: Gary

This is used to add the google analytics codelet to all html files in
a catalog directory and perform any last minute global changes.
"""

import os,shutil

codetext_google = """
   <!-- Google tag (gtag.js) -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-P9QJLSJ71E"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());

     gtag('config', 'G-P9QJLSJ71E');
   </script>
"""

codetext_drv_tw = """
   <!-- Google tag (gtag.js) -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-HKXBPT3N8K"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());

     gtag('config', 'G-HKXBPT3N8K');
   </script>
"""

def add_codelet(filepath,codetext=codetext_google,
                change_repo_name = False):
    with open(filepath,'r',encoding='utf-8') as f:
        alltext = f.read()
    alltext  = alltext.replace('<head>',
                               f'<head>\n{codetext}\n',1)
    
    if change_repo_name:
        alltext = change_header_repo_name(alltext)
    
    with open(filepath,'w',encoding='utf-8') as f:
        f.write(alltext)
    

def modify_sitemap(filepath,urlroot):
    sitemapfn = os.path.join(filepath,'sitemap.xml')
    with open(sitemapfn,'r') as f:
        alltxt = f.read()
    alltxt = alltxt.replace('<loc>',f'<loc>{urlroot}')
    with open(sitemapfn,'w') as f:
        f.write(alltxt)
        
def create_index(dirpath):
    txt = """<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url='Open-FF_Catalog.html'" />
  </head>
  <body>
    <p>Please follow <a href="Open-FF_Catalog.html">this link</a>.</p>
  </body>
</html>"""
    with open(os.path.join(dirpath,'index.html'),'w') as f:
        f.write(txt)
    
        
def add_google_verification_file(dirpath):
    vfile = r"C:\MyDocs\OpenFF\src\openFF-catalog\work\google8891d50ef4ba0a05.html"
    shutil.copy(vfile,dirpath)

def change_header_repo_name(alltext,
                            existing = 'from data repository: current_repo',
                            replace_with = 'from data repository: openFF_data_2024_02_17'):
    # not usually necessary if the source repo is named with a date.
    alltext = alltext.replace(existing,replace_with)
    return alltext

def walk_all_files(filepath,version='google'):
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if file.lower().endswith('html'):
                print(os.path.join(root,file))
                if version=='google':
                    add_codelet(os.path.join(root, file),codetext_google)
                if version=='drv.tw':
                    add_codelet(os.path.join(root, file),codetext_drv_tw)
    if version=='google':
        add_google_verification_file(filepath)
        # create_index(filepath)
        # modify_sitemap(filepath,"https://storage.googleapis.com/open-ff-browser/")

if __name__ == '__main__':
    # dirpath = r"C:\MyDocs\integrated\browser_to_google"
    dirpath = r"G:\My Drive\production\browser_out"
    create_index(dirpath)
    walk_all_files(dirpath,version='google')