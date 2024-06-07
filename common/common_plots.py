"""Code for plots that are used throughout openFF"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def proprietary_bars(df,plot_title='TEST_title',
                     save_file=None):
    """df is a groupby at the disclosure level and the value `perc_proprietary'
    is pre-calculated"""
    import seaborn as sns
    df = df.copy()
    # df['year'] = df.date.dt.year
    df['propCut'] = pd.cut(df.perc_proprietary,right=False,bins=[0,0.0001,10,25,50,101],
                          labels=['no proprietary designations','up to 10% of records\nare proprietary designations',
                                  'between 10 and 25% of records\nare proprietary designations',
                                  'between 25 and 50% of records\nare proprietary designations',
                                  'greater than 50% of records\nare proprietary designations'])
        
    # t = df.propCut.value_counts(sort=False).reset_index()
    # totcnt = t.propCut.sum()
    # t['prop_perc'] = t.propCut/totcnt *100

    # ax = sns.barplot(data=t,y='index',x='propCut',palette='Reds',orient="h")
    t = df.propCut.value_counts(sort=False).reset_index(name='count')
    t = t.rename({'count':'pcount'},axis=1)

    totcnt = t['pcount'].sum()
    t['prop_perc'] = t['pcount']/totcnt *100

    ax = sns.barplot(data=t,x='pcount',y='propCut',palette='Reds',orient="h")
    ax.set_xlabel("Number of disclosures")
    ax.set_ylabel("")
    ax.set_title(plot_title)
    # ax.set_xlim(right=58000)
    ax.invert_yaxis()
    
    perc_lst = t.prop_perc.tolist()
    for i,p in enumerate(ax.patches):
        width = p.get_width()
        #nw = f'  {round_sig(width,8)}'
        nw = f'  {float(round(perc_lst[i],1))}%'
        plt.text(p.get_width(), p.get_y()+0.55*p.get_height(),
                 nw,
                 ha='left', va='center',fontsize=12)
    if save_file:
        plt.tight_layout()
        plt.savefig(save_file)
        
