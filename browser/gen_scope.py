import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup

import os
import pandas as pd
# import numpy as np
# import subprocess
from datetime import datetime
import openFF.common.handles as hndl 
import openFF.common.defaults as dflt
import openFF.common.file_handlers as fh
# import openFF.common.text_handlers as th
# import openFF.common.nb_helper as nbh


today = datetime.today()


class ScopeGen():

    def __init__(self):
        print(f'Compiling Scope data using repository: {hndl.curr_data}')
        self.allrec = fh.get_df(hndl.curr_data)
        # make dir within browser_out if not already there
        try:
            os.mkdir(hndl.browser_scope_dir)
        except:
            "   -- Didn't make scope dir. Already exists?"
        self.run_all()

    def run_all(self):
        self.water_sand_BTEX()
        
    def water_sand_BTEX(self):
        gb1 = self.allrec[self.allrec.in_std_filtered].groupby('DisclosureId',as_index=False)\
            [['TotalBaseWaterVolume','date','OperatorName','bgOperatorName',
             'StateName','CountyName','APINumber','Latitude','Longitude']].first()
        gb1['api10'] = gb1.APINumber.str[:10]
        cond = self.allrec.bgCAS=='14808-60-7'
        gb2 = self.allrec[cond&(self.allrec.in_std_filtered)].groupby('DisclosureId',as_index=False)\
            ['calcMass'].sum().rename({'calcMass':'sandMass'},axis=1)
        cond = self.allrec.bgCAS=='71-43-2'
        gb3 = self.allrec[cond&(self.allrec.in_std_filtered)].groupby('DisclosureId',as_index=False)\
            ['calcMass'].sum().rename({'calcMass':'benzene_mass'},axis=1)
        cond = self.allrec.bgCAS=='108-88-3'
        gb4 = self.allrec[cond&(self.allrec.in_std_filtered)].groupby('DisclosureId',as_index=False)\
            ['calcMass'].sum().rename({'calcMass':'toluene_mass'},axis=1)
        cond = self.allrec.bgCAS=='100-41-4'
        gb5 = self.allrec[cond&(self.allrec.in_std_filtered)].groupby('DisclosureId',as_index=False)\
            ['calcMass'].sum().rename({'calcMass':'ethylbenzene_mass'},axis=1)
        cond = self.allrec.bgCAS=='1330-20-7'
        gb6 = self.allrec[cond&(self.allrec.in_std_filtered)].groupby('DisclosureId',as_index=False)\
            ['calcMass'].sum().rename({'calcMass':'xylene_mass'},axis=1)
        out = pd.merge(gb1,gb2,on='DisclosureId',how='left')
        out = pd.merge(out,gb3,on='DisclosureId',how='left')
        out = pd.merge(out,gb4,on='DisclosureId',how='left')
        out = pd.merge(out,gb5,on='DisclosureId',how='left')
        out = pd.merge(out,gb6,on='DisclosureId',how='left')
        out.drop('DisclosureId',axis=1,inplace=True)
        out.to_csv(os.path.join(hndl.browser_scope_dir,'water_sand_btex.zip'),
                   encoding='utf-8',index=False,
                   compression={'method': 'zip', 'archive_name': 'water_sand_btex.csv'})

