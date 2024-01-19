# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 19:40:01 2023

@author: garya

This is a collection of tools used to parse, summarize, store and display
the results from the ChemInformatics modules.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import openFF.common.file_handlers as fh
import openFF.common.handles as hndl

# from openFF.common.file_handlers import save_df
# from openFF.common.handles import pic_dir

class Process_SDF():
    def __init__(self,fn):
        self.fn = fn
        self.lines = []
        self.currline = 0
        self.allrecs = []

    def read_whole_sdf(self):
        #print('reading SDF')
        with open(self.fn, 'r') as f:
            self.lines = f.read().splitlines()
        
    def fetch_all_varnames(self):
        self.names = set()
        self.read_whole_sdf()
        for l in self.lines:
            #print(len(l),'|',l,'|')
            if (len(l)>0):
                if (l[0]=='>'):
                    self.names.add(l[3:-1])
        #print(self.names)
        
    def make_new_record(self):
        self.curr_rec = {}
        for v in self.names:
            self.curr_rec[v] = 'ND'
            
    def store_completed_record(self):
        self.allrecs.append(self.curr_rec)
        
    def process_all_lines(self):
        keep_long = ['CAS','Name','DTXSID']
        self.read_whole_sdf()
        self.fetch_all_varnames()
        self.make_new_record()
        while self.currline < len(self.lines)-1:
            self.currline += 1
            try:
                if self.lines[self.currline][0] == '>':
                    v = self.lines[self.currline][3:-1]
                    self.currline +=1 
                    value = self.lines[self.currline]
                    if not v in keep_long: # make authority values shorter
                        value = value[0]
                    self.curr_rec[v] = value
            except:
                pass
            if self.lines[self.currline] == '$$$$':
                self.store_completed_record()
                self.make_new_record()
                # print('end')
        print(f'Lines in ChemInformatics Hazard SDF file: {len(self.lines)}')
        print(f'Number of materials in chemInfo list: {len(self.allrecs)}')     
        self.df = pd.DataFrame(self.allrecs)
    

def sdf_extract(ci_source,out_dir):
    # pull scores and authority from the .sdf text files from the
    # Hazard module.  
    to_process = []
    lst = os.listdir(ci_source)
    for fn in lst:
        if fn[-4:] == '.sdf':
            if fn[:6]=='hazard':
                to_process.append(os.path.join(ci_source,fn))
    if len(to_process)!=1:
        print(to_process)
        assert 0==1,'Code only setup for exactly one file'
    pSDF = Process_SDF(to_process[0])
    pSDF.process_all_lines()
    fh.save_df(pSDF.df,os.path.join(out_dir,hndl.ci_summ_fn))
    
######################  Used in catalog routines ############
ci_dir = r"C:\MyDocs\OpenFF\src\testing\chemInfo"
# report_dir = r"C:\MyDocs\OpenFF\data\external_refs\ChemInformatics"
# im_dir = r"C:\MyDocs\OpenFF\src\openFF-catalog\pic_dir"


def get_summary_from_xls(fn):
    """This routine throws a warning for each file in the report dir. They are
    harmless and difficult to remove."""
    t = pd.read_excel(fn,skiprows=5)
    cols = ['DTXSID','CASRN','Name','HH: Oral','HH: Inhalation','HH: Dermal','HH: Carcinogenicity',
            'HH: Genotoxicity Mutagenicity','HH: Endocrine Disruption','HH: Reproductive','HH: Developmental',
            'HH: Neurotoxicity: Repeat Exposure','HH: Neurotoxicity: Single Exposure',
            'HH: Systemic Toxicity: Repeat Exposure','HH: Systemic Toxicity: Single Exposure',
            'HH: Skin Sensitization','HH: Skin Irritation','HH: Eye Irritation',
            'Ecotoxicity: Acute Aquatic Toxicity','Ecotoxicity: Chronic Aquatic Toxicity',
            'Fate: Persistence','Fate: Bioaccumulation','Fate: Exposure']
    t.columns = cols
    return t


def get_all_excel(inputdir=ci_dir, single_file = ''):
    if single_file:
        lst = [single_file]
    else:
        lst = os.listdir(inputdir)
    dfs = []
    for fn in lst:
        if fn[-4:] != 'xlsx':
            continue
        filename = os.path.join(inputdir,fn)
        dfs.append(get_summary_from_xls(filename))
    out = pd.concat(dfs,sort=False)
    print(len(out))
    out = out[~out.duplicated(subset='DTXSID')]
    print(len(out))
    return out

def getImage(path, zoom=.5):
    return OffsetImage(plt.imread(path), zoom=zoom)

def make_fingerprint(df,casrn = '107-19-7'):
    #print(casrn)
    t = df[df.CASRN==casrn].drop(['DTXSID','CASRN','Name'],axis=1)
    t = t.fillna('ND')
    #categ = ['VH','H','M','L','I','ND']
    im_dic = {'I':os.path.join(hndl.pic_dir,'ci_icons','grey_question.png'),
              'ND':os.path.join(hndl.pic_dir,'ci_icons','grey_square.png'),
              'H':os.path.join(hndl.pic_dir,'ci_icons','orange_exclamation.png'),
              'VH':os.path.join(hndl.pic_dir,'ci_icons','red_skull.png'),
              'M':os.path.join(hndl.pic_dir,'ci_icons','yellow-minus.png'),
              'L':os.path.join(hndl.pic_dir,'ci_icons','green-minus.png'),
              'noval':os.path.join(hndl.pic_dir,'ci_icons','brown-x.png')}

    out = t.values.flatten().tolist()
    
    # handle chem without ci data
    if len(out) == 0: # don't save anything
        #for i in range(20): out.append('noval') 
        return
    x = []; y = []; paths = []          
    for i,val in enumerate(out):
        x.append(i%5)
        y.append(3 - i//5)
        paths.append(im_dic[val])
    # for i in zip(x, y,paths): print(i)
    fig, ax = plt.subplots(facecolor='black')
    ax.scatter(x, y) 
    # ax.set_title(casrn)

    for x0, y0, path in zip(x, y,paths):
        ab = AnnotationBbox(getImage(path,zoom=0.75), (x0, y0), frameon=False)
                           # bboxprops = dict(facecolor='wheat',boxstyle='round',color='black'))
        ax.add_artist(ab)
        ax.set_facecolor('black')
    plt.savefig(os.path.join(hndl.pic_dir,casrn,'haz_fingerprint.png'))    

def make_all_fingerprints(caslst,hazdf):
    cas_ignore = ['proprietary','ambiguousID','sysAppMeta','conflictingID']
    for i,cas in enumerate(caslst):
        print(f'{i}: {cas}')
        if not cas in cas_ignore:            
            make_fingerprint(hazdf,cas)
        
# def remove_all(caslst):
#     for cas in caslst:
#         try:
#             os.remove(os.path.join(pic_dir,cas,'haz_fingerprint.png'))        
#         except:
#             print(f'Not there: {cas}')
            
                    
                
