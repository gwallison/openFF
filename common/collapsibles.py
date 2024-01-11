# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 16:43:00 2023

@author: garya
"""
#import pandas as pd
#import numpy as np
#from openFF.common.text_handlers import getFingerprintImg, getCompToxRef, getMapLink, round_sig, getCatLink, getPubChemLink

indent_txt = '<span style="padding-left: 20px; display:block">'
end_indent = '</span>'

def build_collapsible(toggle_text,content=[],clr='black'):
    """toggle_text goes one line, collapisible content is contructed into multi-line, based on items in list"""
    cntstr = indent_txt
    for item in content:
        cntstr += item + '<br>'
    cntstr += end_indent
    return f"""    
    <div class="collapsible">
    <div class="collapsible-toggle" style="color: {clr}">{toggle_text} <span class="icon">&#x25BC;</span></div>
    <div class="content">{cntstr}</div>
    </div>\n
    """    
def collapse_object(button_txt,content_lst=['NO CONTENT'],has_flags=False):
    return (button_txt,content_lst,has_flags)

def build_collapsible_set(lst):
    s = ''
    for i in lst:
        clr_change = ''
        if i[2]: # has_flags
            clr_change = 'style="background-color: #8a1003" '
        s+= f'<button class="collapsible" {clr_change}>{i[0]}</button>\n'
        s+= '<div class="content"><p>\n'
        for item in i[1]:
            s+= item + '<br>\n'
        s+= '</p></div>\n'
    return s
