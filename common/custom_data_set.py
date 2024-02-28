"""class to produce a local (even on colab) custom dataset.  As of Feb 2024, the free version of colab 
can't handle the whole full_df - it overflows the RAM.  The solution here is to:
- download the separate database tables locally.
- use information about what fields the user wants to 
- create local dfs of the tables that are smaller than the full tables (when appropriate)
- then, merge them to create the data frame desired. 

Currently we download all tables, though that might not be necessary.  However, minor tables are pretty
small so probably not a lots of savings to control that.

 """

import pandas as pd
import os

import openFF.common.handles as hndl
import openFF.common.file_handlers as fh


class Custom_Data_Set():
    def __init__(self,use_set='standard',added_cols=[],force_refresh=False):
        # fetch repo tables if you don't have them already
        fh.make_tables_local(force_refresh=force_refresh)

    def get_table_cols(tablename='disclosures'):
        pass