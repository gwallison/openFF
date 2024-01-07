""" some default values used throughout Open-FF"""

# the standard filtered columns, instead of full_df, about half
filt_cols = ['PercentHFJob', 'mass','massSource',
            'calcMass', 'DisclosureId', 'OperatorName',
            'bgOperatorName',
            'APINumber', 'TotalBaseWaterVolume',
            'TotalBaseNonWaterVolume', 'FFVersion', 
            'TVD', 'StateName', 'CountyName', 
            'Latitude', 'Longitude', 'Projection',
            'data_source', 'bgStateName', 'bgCountyName', 
            'bgLatitude', 'bgLongitude', 'date',
            'IngredientName', 'Supplier', 'bgSupplier', 
            'CASNumber', 'bgCAS','primarySupplier',
            'epa_pref_name','iupac_name',
            'bgIngredientName','in_std_filtered',
            'TradeName','Purpose','has_TBWV',
            'within_total_tolerance','has_water_carrier',
            'carrier_status','massComp','massCompFlag',
            'cleanMI','loc_within_state','no_chem_recs',
            'loc_within_county','rq_lbs','bgLocationSource']

if __name__ == '__main__':
    print(len(filt_cols),len(set(filt_cols)))
