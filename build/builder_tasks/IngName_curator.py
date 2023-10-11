# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 09:54:59 2021

@author: Gary

This set of routines is used to assist in the curation of IngredientName.

"""
import numpy as np
import pandas as pd
import difflib as dl
import os
from openFF.common.file_handlers import get_df


######## -------------------------------------------------
# create ref dictionary
#  Text/syn : (curation_code, [(casnum,source), (casnum,source),...])
######## --------------------------------------------------
def add_to_ref(dic,txt,curcode,casnum,source):
    if txt=='': # don't add empty strings
        return dic
        
    if txt in dic.keys():
        if len(txt)<1:
            print(txt)
        # add to existing entry. NOTE THAT LAST INSTANCE FOR AN ENTRY IS
        #   THE GIVEN PRIMACY by writing over previous curcodes
        prev = dic[txt]
        new = prev[1]
        new.append((casnum,source))
        dic[txt] = (curcode,new)
    else:
        dic[txt] = (curcode,[(casnum,source)])
    return dic

def summarize_refs(ref):
    for item in ref:
        lst = ref[item][1]
        lbl = ref[item][0]
        if len(lst)>1:  # may need to adjust curation code
            first = lst[0][0]
            for l in lst[1:]:
                if l[0]!=first:
                    lbl = 'non_spec'
                    ref[item] = (lbl, lst)
                    #print(f'adjusted {item} to non_specific')
                    break
    return ref

def ref_stats(dic):
    cntr =0
    for item in dic:
        if len(dic[item][1])>1:
            cntr+=1
    return cntr

def build_refdic(ref_dir):
    refdic = {}
    syndf = get_df(os.path.join(ref_dir,'master_synonym_list.parquet'))
    for i,row in syndf.iterrows():
        refdic = add_to_ref(refdic, row.synonym, 'CASsyn',row.cas_number, row.Source)
    
    return summarize_refs(refdic)

def add_curated_record(record,ING_curated):
    t = pd.concat([record,ING_curated],sort=True)
    return t


def make_record(IngN='unk',recog_syn='unk',prospect_CAS='unk',syn_code='unk',match_ratio=0,
                alt1_CAS='unk',alt1_syn='unk'):
    return pd.DataFrame({'IngredientName':[IngN],
                         'is_new':True,
                         'recog_syn':[recog_syn],
                         'prospect_CAS_fromIng':[prospect_CAS],
                         'syn_code':[syn_code],
                         'match_ratio':[match_ratio],
                         'alt_CAS':[alt1_CAS]})




def add_fullscan_record(record,fs_df,ref_dir):
    t = pd.concat([record,fs_df],sort=True)
    t = t[['CASNumber','curatedCAS','IngredientName','recog_syn','synCAS',
           'match_ratio','n_close_match']]
    return t



def make_fullscan_record(CASNumber='unk',curatedCAS='unk',IngredientName='unk',
                         recog_syn='unk',synCAS='unk',match_ratio=0,n_close_match=0):
    return pd.DataFrame({'CASNumber':[CASNumber],
                      'curatedCAS':[curatedCAS],
                      'IngredientName':[IngredientName],
                      'recog_syn':[recog_syn],
                      'synCAS': [synCAS],
                      'match_ratio':[match_ratio],
                      'n_close_match':[n_close_match]})

def make_empty_record(IngredientName):
    return make_fullscan_record('--','--',IngredientName,'','',0)

def full_scan(to_curate,refdic,fs_df,ref_dir):
    # used to scan and classify the entire list of IngNames.  This will take
    # a significant amt of time for each entry.
    #ingwords = to_curate[to_curate.IngredientName.notna()].IngredientName.tolist()
    ref = list(refdic.keys())
    for cntr,row in to_curate.iterrows():
        #if cntr%100==0:
        print(f'{cntr}: processing:< {row.CASNumber} > < {row.IngredientName} >')
        d = dl.get_close_matches(row.IngredientName, ref,cutoff=0.85,n=7) # 
        if len(d)==0:
            #print(f'No matches  ({cntr})')
            rec = make_fullscan_record(row.CASNumber,row.curatedCAS,row.IngredientName,
                                       'no match','non_spec',0,0)
            fs_df = add_fullscan_record(rec, fs_df,ref_dir)
        if len(d)>0:
            # first determine how many unique CAS numbers are in the close set
            uni_cas = set()
            for cnt,match in enumerate(d):
                mat = refdic[d[cnt]]
                if mat[0] == 'non_spec':
                    uni_cas.add('non_spec')
                else:
                    uni_cas.add(mat[1][0][0])
            #print(uni_cas)
            for cnt,match in enumerate(d):
                #print(f'match {cnt}  ({cntr})')
                #print(refdic[match])
                mat = refdic[d[cnt]]
                ratio = dl.SequenceMatcher(a=row.IngredientName,b=match).ratio() 
                if mat[0] == 'non_spec':
                    rec = make_fullscan_record(row.CASNumber,row.curatedCAS,row.IngredientName,
                                               d[cnt],'non_spec',ratio,len(uni_cas))
                else:
                    rec = make_fullscan_record(row.CASNumber,row.curatedCAS,row.IngredientName,
                                               d[cnt],mat[1][0][0],ratio,len(uni_cas))
                fs_df = add_fullscan_record(rec, fs_df,ref_dir)
        # check for proprietary wording in Name
        prop_txt = ['proprietary','secret','confidential']
        for txt in prop_txt:# this is not an full search of all possibilities, just a helper
            if txt in row.IngredientName:
                rec = make_fullscan_record(row.CASNumber,row.curatedCAS,row.IngredientName,
                                           '--','proprietary',0,len(d))
                fs_df = add_fullscan_record(rec, fs_df,ref_dir)
                break

    return fs_df

    
def analyze_fullscan(fs_df):
    # makes a dataframe that aids manual curation
    fs_df['curValid'] = fs_df.curatedCAS.str[0].str.isdigit()
    fs_df['synValid'] = fs_df.synCAS.str[0].str.isdigit()
    
    fs_df['casing_match'] = np.where(fs_df.curatedCAS==fs_df.synCAS,'YES','')
    fs_df['source'] = 'neither'
    fs_df.source = np.where((~fs_df.curValid)&fs_df.synValid,
                            'ING_only',fs_df.source)
    fs_df.source = np.where(fs_df.curValid&(~fs_df.synValid),
                            'CAS_only',fs_df.source)
    fs_df.source = np.where(fs_df.curatedCAS=='proprietary','CAS_only',fs_df.source)
    fs_df.source = np.where(fs_df.casing_match=='YES','both',fs_df.source)
    fs_df.source = np.where(fs_df.curValid&fs_df.synValid\
                            &~(fs_df.casing_match=='YES')&(fs_df.match_ratio>=0.95),
                            'conflict',fs_df.source)
    fs_df.source = np.where(fs_df.curValid&fs_df.synValid\
                            &~(fs_df.casing_match=='YES')&(fs_df.match_ratio<0.95),
                            'CAS_only',fs_df.source)
    fs_df['bgCAS'] = 'ambiguousID'
    fs_df.bgCAS = np.where(fs_df.source.isin(['both','CAS_only']),fs_df.curatedCAS,fs_df.bgCAS)
    fs_df.bgCAS = np.where(fs_df.source.isin(['ING_only']),fs_df.synCAS,fs_df.bgCAS)
    fs_df.bgCAS = np.where(fs_df.source.isin(['conflict']),'conflictingID',fs_df.bgCAS)
    
    # find likely best choice by ranking them
    gb = fs_df.groupby(['CASNumber','IngredientName'],as_index=False)['match_ratio'].max()\
        .rename({'match_ratio':'maxratio'},axis=1)
    fs_df = pd.merge(fs_df,gb,on=['CASNumber','IngredientName'],how='left')
    fs_df['rrank'] = 0
    fs_df.rrank = np.where(fs_df.source=='both',fs_df.rrank + 4, fs_df.rrank)
    fs_df.rrank = np.where(fs_df.curatedCAS=='proprietary',fs_df.rrank + 2, fs_df.rrank)
    fs_df.rrank = np.where(fs_df.match_ratio==fs_df.maxratio,fs_df.rrank + 1, fs_df.rrank)

    gb = fs_df.groupby(['CASNumber','IngredientName'],as_index=False)['rrank'].max()\
        .rename({'rrank':'bestguess'},axis=1)
    fs_df = pd.merge(fs_df,gb,on=['CASNumber','IngredientName'],how='left')
    fs_df['picked'] = np.where(fs_df.bestguess==fs_df.rrank,'xxx','')
    # print(fs_df.columns)
    
    
    # add spacers
    gbsp = fs_df.groupby(['CASNumber','IngredientName'],as_index=False).size()
    out = pd.concat([fs_df,gbsp[['CASNumber','IngredientName']]])
    out = out.drop(['curValid','synValid','casing_match','bestguess','maxratio'],axis=1)
    out = out.fillna('---------')    
    
    out = out.sort_values(['CASNumber','IngredientName','rrank'],ascending=False)
    return out

