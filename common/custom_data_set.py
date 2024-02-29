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
import openFF.common.nb_helper as nbh


# parquet schema code from; https://stackoverflow.com/questions/41567081/get-schema-of-parquet-file-in-python
import pyarrow.parquet

def read_parquet_schema_df(uri: str) -> pd.DataFrame:
    """Return a Pandas dataframe corresponding to the schema of a local URI of a parquet file.
    The returned dataframe has the columns: column, pa_dtype
    """
    # Ref: https://stackoverflow.com/a/64288036/
    schema = pyarrow.parquet.read_schema(uri, memory_map=True)
    schema = pd.DataFrame(({"column": name, "pa_dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
    schema = schema.reindex(columns=["column", "pa_dtype"], fill_value=pd.NA)  # Ensures columns in case the parquet file has an empty dataframe.
    return schema



class Custom_Data_Set():
    def __init__(self,use_set='standard',added_cols=[], filters={},#{'bgStateName':['pennsylvania']},
                 force_refresh=False,
                 create_std_flag=True):
        # fetch repo tables if you don't have them already
        fh.make_tables_local(force_refresh=force_refresh)
        self.filters = filters
        self.create_std_flag = create_std_flag
        self.pkldir = os.path.join(hndl.sandbox_dir,'pickles')

        # We only use the 4 main tables.  To create data sets from other tables, use alternate means
        self.pList = ['disclosures','chemrecs','bgCAS','water_source']

        self.col_sets = {'standard': ['DisclosureId', 'JobEndDate', 'JobStartDate', 'OperatorName', 'APINumber',
                                    'TotalBaseWaterVolume', 'FFVersion', 'TVD', 'api10',
                                    'WellName', 'bgOperatorName', 'StateName', 'bgStateName',
                                    'CountyName', 'bgCountyName', 'Latitude', 'bgLatitude', 'Longitude', 'bgLongitude',
                                    'bgLocationSource', 'latlon_too_coarse', 'loc_name_mismatch', 'loc_within_state', 'loc_within_county',
                                    'date','ws_perc_total', 'no_chem_recs', 'is_duplicate', 'primarySupplier',
                                    'MI_inconsistent', 'IngredientsId', 'CASNumber', 'IngredientName', 'PercentHFJob', 'Supplier', 'Purpose', 
                                    'TradeName', 'PercentHighAdditive', 'MassIngredient', 'ingKeyPresent', 'reckey',
                                    'bgCAS', 'ingredCommonName', 'bgSupplier', 'dup_rec', 'cleanMI', 'calcMass', 'massComp', 'massCompFlag',
                                    'massSource', 'mass', 'bgIngredientName', 'is_on_CWA', 'is_on_DWSHA', 'is_on_AQ_CWA', 'is_on_HH_CWA', 
                                    'is_on_IRIS', 'is_on_PFAS_list', 'epa_pref_name', 'is_on_NPDWR', 'is_on_prop65', 'is_on_TEDX', 'is_on_diesel', 
                                    'is_on_UVCB', 'rq_lbs']}

        self.cols_wanted = list(set(self.col_sets[use_set] + added_cols + list(filters.keys())+ ['dup_rec','is_duplicate']))

    def get_all_table_cols(self):
        # use schema to keep from loading whole file.
        self.tCols = {}
        for name in self.pList:
            fn = os.path.join(self.pkldir,name+'.parquet')
            cdf = read_parquet_schema_df(fn)
            self.tCols[name] = cdf['column'].tolist()

    def get_table_list(self):
        self.tables_needed = {}
        for name in self.pList:
            common = set(self.cols_wanted) & set(self.tCols[name])
            if len(common)>0:
                self.tables_needed[name] = list(common)

    def has_non_key_columns(self,tablename):
        keycols = {'disclosures':['DisclosureId'],
                   'chemrecs':['bgCAS','DisclosureId'],
                   'bgCAS':['bgCAS'],
                   'water_source' : ['DisclosureId']}
        l = self.tables_needed[tablename]
        if tablename == 'bgCAS':
            l.remove('bgCAS')
        if tablename == 'water_source':
            l.remove('DisclosureId')
        return len(l)>0 
    
    def assemble_tables(self):
        df_dic = {}
        for name in self.tables_needed.keys():
            fn = os.path.join(self.pkldir,name+'.parquet')
            df = fh.get_df(fn,cols=self.tables_needed[name])
            # do we need to filter?
            for fcol in self.filters.keys():
                if fcol in df.columns.tolist():
                    df = df[df[fcol].isin(self.filters[fcol])]
            df_dic[name] = df

        out = pd.merge(df_dic['disclosures'],df_dic['chemrecs'],
                      on = 'DisclosureId', how='inner',validate ='1:m')
        
        if self.has_non_key_columns('bgCAS'):
            out = out.merge(df_dic['bgCAS'],on='bgCAS',how='left',validate='m:1')
        if self.has_non_key_columns('water_source'):
            out = out.merge(df_dic['water_source'],on='DisclosureId',how='left',validate='m:1')
        if self.create_std_flag:
            out['in_std_filtered'] = ~(out.dup_rec | out.is_duplicate)

        self.final_df = out
    
    def make_final_data_set(self,filters={}):
        self.filters = filters
        self.get_all_table_cols()
        self.get_table_list()
        self.assemble_tables()
        nbh.completed()

