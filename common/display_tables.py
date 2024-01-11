# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 16:43:00 2023

@author: garya
"""
import pandas as pd
import numpy as np
import openFF.common.text_handlers as th
import openFF.common.collapsibles as collaps
import openFF.common.chem_list_summary as chem_sum

# indent_txt = '<span style="padding-left: 20px; display:block">'
# end_indent = '</span>'

# def build_collapsible(toggle_text,content=[],clr='black'):
#     """toggle_text goes one line, collapisible content is contructed into multi-line, based on items in list"""
#     cntstr = indent_txt
#     for item in content:
#         cntstr += item + '<br>'
#     cntstr += end_indent
#     return f"""    
#     <div class="collapsible">
#     <div class="collapsible-toggle" style="color: {clr}">{toggle_text} <span class="icon">&#x25BC;</span></div>
#     <div class="content">{cntstr}</div>
#     </div>\n
#     """    
# def collapse_object(button_txt,content_lst=['NO CONTENT'],has_flags=False):
#     return (button_txt,content_lst,has_flags)

# def build_collapsible_set(lst):
#     s = ''
#     for i in lst:
#         clr_change = ''
#         if i[2]: # has_flags
#             clr_change = 'style="background-color: #8a1003" '
#         s+= f'<button class="collapsible" {clr_change}>{i[0]}</button>\n'
#         s+= '<div class="content"><p>\n'
#         for item in i[1]:
#             s+= item + '<br>\n'
#         s+= '</p></div>\n'
#     return s

def make_html_of_disclosure_meta(disc_table):
    """Use collapsibles to keep visibilty managable"""
    row = disc_table.iloc[0]
    colls = []
    # APINumber, etc
    colls.append(collaps.collapse_object(f'<b>IDENTITY: APINumber</b>: {row.APINumber}',
                                 [f"WellName: {row.WellName}",
                                  f"DisclosureId: {row.DisclosureId}",
                                  f"api10: {row.api10}"])
   )
    # dates, etc
    try: jstart = row.JobStartDate.split()[0]
    except: jstart = row.JobStartDate
    try: jend = row.JobEndDate.split()[0]
    except: jend = row.JobEndDate

    delay = row.pub_delay_days

    colls.append(collaps.collapse_object(f'<b>DATES:  Job Start and End</b>: {jstart}, {jend}',
                                 [f'date (Open-FF): {row.date}',
                                  f'date_added (first detected by Open-FF): {row.date_added}',
                                  f'publication delay: {delay} days'])
   )
    # operators
    colls.append(collaps.collapse_object(f'<b>COMPANIES:  OperatorName</b>: {row.OperatorName}',
                                 [f'bgOperatorName: {row.bgOperatorName}',
                                 f'primarySupplier (the most common supplier on the disclosure): {row.primarySupplier} '])
    )
    # state and county
    flag = row.loc_name_mismatch | (row.loc_within_county=='NO') | (row.loc_within_state=='NO')
    colls.append(collaps.collapse_object(f'<b>LOCATION: </b> {row.CountyName} County, {row.StateName}',
                                 [f'bgStateName: {row.bgStateName}', f'bgCountyName: {row.bgCountyName}',
                                 f'loc_name_mismatch: {row.loc_name_mismatch}',
                                 f'loc_within_county: {row.loc_within_county}',
                                 f'loc_within_state: {row.loc_within_state}'],
                                 flag)
    )
    # TBWV
    flag = ~(row.TotalBaseWaterVolume>0) | ~row.has_water_carrier
    colls.append(collaps.collapse_object(f'<b>CARRIER: TotalBaseWaterVolume</b>: {row.TotalBaseWaterVolume:,} gallons',
                          [f'TotalBaseNonWaterVolume: {row.TotalBaseNonWaterVolume:,}',
                           f'carrier status: {row.carrier_status}',
                           f'auto_carrier_type: {row.auto_carrier_type}',
                           f'carrier Problem Flags: {row.carrier_problem_flags}'],
                          flag)
    )    
    # Status flags
    flag = ~(row.within_total_tolerance) | row.no_chem_recs | row.is_duplicate
    colls.append(collaps.collapse_object(f'<b>STATUS: </b>  ',
                          [f'no chemical records: {row.no_chem_recs}',
                           f'is_duplicate: {row.is_duplicate}',
                           f'within_total_tolerance: {row.within_total_tolerance}',
                           f'FracFocus version: {row.FFVersion}',
                           f'MI_inconsistent: {row.MI_inconsistent}'],
                           flag)
    )    
    colls.append(collaps.collapse_object('<b>Click here for more details</b>',
                          ['<b>Provided by FracFocus:</b>',
                          f'{collaps.indent_txt}',
                          # f'DisclosureId: {row.DisclosureId}',f'WellName: {row.WellName}',
                          f'TVD: {row.TVD} feet',
                          # f'TotalBaseNonWaterVolume: {row.TotalBaseNonWaterVolume} gallons',
                          f'FracFocus version: {row.FFVersion}',
                          # f'FederalWell: {row.FederalWell}',
                          # f'IndianWell: {row.IndianWell}',
                          f'{collaps.end_indent}',
                          '<b>Generated by Open-FF:</b>',
                          f'{collaps.indent_txt}',
                          # f'bgFederalLand: {row.bgFederalLand}',
                          # f'bgNativeAmericanLand: {row.bgNativeAmericanLand}',
                          # f'bgStateLand: {row.bgStateLand}',
                          f'{collaps.end_indent}'
                          ])
    )  
                         
    s = "<h2> Fracking Job Details </h2>\n"
    s+= f'<h3>{th.getMapLink(row,txt="Google Map")} ; '
    s+= f'<a href="https://fracfocus.org/wells/{row.APINumber}"  target="_blank"> Disclosure at FracFocus</a></h3>\n'
    s += collaps.build_collapsible_set(colls)
    return s

# def make_extrnl_column(chem_df):
#     chem_df['extrnl'] = np.where(chem_df.is_on_CWA,'CWA<br>','    ')
#     chem_df.extrnl = np.where(chem_df.is_on_AQ_CWA,chem_df.extrnl+'AQ_CWA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_HH_CWA,chem_df.extrnl+'HH_CWA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_NPDWR,chem_df.extrnl+'NPDWR<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_DWSHA,chem_df.extrnl+'DWSHA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_TEDX,chem_df.extrnl+'TEDX<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_prop65,chem_df.extrnl+'prop65<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_PFAS_list,chem_df.extrnl+'EPA_PFAS<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_UVCB,chem_df.extrnl+'UVCB<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_diesel,chem_df.extrnl+'diesel<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_IRIS,chem_df.extrnl+'IRIS    ',chem_df.extrnl)
#     chem_df.extrnl = '<p style="color:green;font-size:105%;text-align:center;background-color:lightgrey;">'+chem_df.extrnl.str[:-4]+'</p>'
#     return chem_df


# def make_chem_single_disclosure(rec_table,cas_table,
#                                  show_dup_recs=True,
#                                  removeCAS=[],showOnlyCAS=[],
#                                  ):
# def make_chem_single_disclosure(disc_df): #rec_table,cas_table,
#     """This is for the display of a single disclosure. Records are not collapsed to one/CASRN."""
#     assert len(disc_df.DisclosureId.unique()) == 1, 'More than one disclosure not allowed!'
#     chem_obj = chem_sum.ChemListSummary(disc_df, summarize_by_chem=False)
#     return(chem_obj.get_display_table(colset='single_disc'))
    # # filters
    # if not show_dup_recs: rec_table = rec_table[~rec_table.dup_rec]
    # if removeCAS: rec_table = rec_table[~rec_table.bgCAS.isin(removeCAS)]
    # if showOnlyCAS: rec_table = rec_table[rec_table.bgCAS.isin(showOnlyCAS)]
    # cas_table.fillna('--',inplace=True)
    # chem_df = pd.merge(rec_table,cas_table,on='bgCAS',how='left')


    # # chem_df['CASRN'] = chem_df.bgCAS+'<br><em>('+chem_df.CASNumber+')</em>'
    # # chem_df['name'] = chem_df.epa_pref_name+'<br><em>('+chem_df.IngredientName+')</em>'
    # chem_df = make_extrnl_column(chem_df)
    # chem_df['hazard fingerprint'] = chem_df.bgCAS.map(lambda x: th.getFingerprintImg(x))
    # chem_df['compTox'] = chem_df.DTXSID.map(lambda x: th.getCompToxRef(x))

    # return chem_df[['TradeName','Supplier','Purpose','CASNumber','bgCAS','IngredientName','bgIngredientName','epa_pref_name',
    #                 'PercentHighAdditive','PercentHFJob',
    #                 'cleanMI','calcMass',
    #                 'extrnl','hazard fingerprint','compTox','is_water_carrier','dup_rec']]

def make_html_for_chem_table(df):
    cols = df.columns.tolist()
    header_str = ''
    for col in cols:
        header_str += f'       <th>{col}</th>\n'
    
    jdata = df.to_json(orient='values')

    template =  f""" <h2> Fracking Chemical Details </h2>
    <div id="datatable-container">
    <table id="data-table" class="display compact cell-border" style="table-layout:auto;width:80%;margin:auto;caption-side:bottom">
      <thead>
        <tr>
    {header_str}

      </tr>
      </thead>
      <tbody> 
      </tbody>
    </table>
  </div>
  <script>
    $(document).ready(function() {{
      // Data to be displayed in the DataTable
  """
    template += f'const data = {jdata}'
    template += """ \n // Initialize DataTables
      $('#data-table').DataTable({
        data: data,
        paging: false,
        fixedHeader: false,
        dom: 'Bfrtip',
        buttons: [{extend: 'colvis',text: 'Columns'}],
        columnDefs: [{"width": "100px", "targets": 2},
                     {"targets": [0,1,2,3,5,6,8,11,12,13,17,18], "visible": false},
                     {"render": $.fn.dataTable.render.number(',', '.', 0), "targets": [10,11]}]
      });
    });
    </script>
  ## the script below is used to include html into final page.  Has to be local to this html and doesn't work with localhost...
     <div w3-include-html="../disclosure_include.html"></div>
   <script>
      function addHTML() {
         var el, i, domEl, fileName, xmlHttp;
         
         /*Iterate all DOM*/
         el = document.getElementsByTagName("*");
         for (i = 0; i < el.length; i++) {
            domEl = el[i];
            
            /*find the element having w3-include-html attribute*/
            fileName = domEl.getAttribute("w3-include-html");
            if (fileName) {
               
               /*http request with attribute value as file name*/
               xmlHttp = new XMLHttpRequest();
               xmlHttp.onreadystatechange = function() {
                  if (this.readyState == 4) {
                     if (this.status == 200) {
                        domEl.innerHTML = this.responseText;
                     }
                     if (this.status == 404) {
                        domEl.innerHTML = "Page not found.";
                     }
                     
                     /* Remove the attribute and invoke the function again*/
                     domEl.removeAttribute("w3-include-html");
                     addHTML();
                  }
               }
               xmlHttp.open("GET", fileName, true);
               xmlHttp.send();
               
               /*function ends*/
               return;
            }
         }
      }
      addHTML();
   </script>
  """
    return template

# def make_compact_chem_summary(df_cas,removeCAS=['ambiguousID','sysAppMeta','conflictingID']):

#     df_cas = df_cas[~df_cas.bgCAS.isin(removeCAS)]
    
#     chem_df = df_cas.groupby('bgCAS',as_index=False)[['DisclosureId']].count()
#     chem_df = chem_df.rename({'DisclosureId':'numRecords'},axis=1)
#     gb1 = df_cas[df_cas.in_std_filtered].groupby('bgCAS',as_index=False)[['DisclosureId']].count()
#     chem_df = pd.merge(chem_df,gb1,on='bgCAS',how='left')
#     chem_df.fillna(0,inplace=True)
#     chem_df.numRecords = chem_df.DisclosureId.astype('int').astype('str') #+ '<br>'+ chem_df.numRecords.astype('str')
#     t = df_cas[(df_cas.calcMass>0)&(df_cas.in_std_filtered)].groupby('bgCAS',as_index=False)[['DisclosureId']].count()
#     t = t.rename({'DisclosureId':'numWithMass'},axis=1)
    
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
#     chem_df.numWithMass.fillna(0,inplace=True)
    
#     t = df_cas.groupby('bgCAS')[['bgIngredientName','is_on_TEDX','is_on_prop65',#'is_on_CWA_priority',
#                                  'is_on_CWA','is_on_DWSHA','is_on_PFAS_list',
#                                  'is_on_UVCB','is_on_diesel','is_on_AQ_CWA','is_on_HH_CWA','is_on_IRIS',
#                                  'is_on_NPDWR','rq_lbs',
#                                  'DTXSID']].first()
#     #t.rq_lbs = t.rq_lbs.map(lambda x: round_sig(x,2))
#     #t.rq_lbs.fillna('  ',inplace=True)
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
    
#     t = df_cas[(df_cas.calcMass>0)&(df_cas.in_std_filtered)].groupby('bgCAS',as_index=False)['calcMass'].sum()
#     t.calcMass = t.calcMass.map(lambda x: round_sig(x,3))
#     chem_df = pd.merge(chem_df,t,on='bgCAS',how='left')
#     chem_df.calcMass.fillna(0,inplace=True)
    
#     #chem_df['Filtered Data'] = chem_df.bgCAS.map(lambda x: getDataLink(x))
#     chem_df['History'] = chem_df.bgCAS.map(lambda x: getCatLink(x,x,use_remote=True))
#     chem_df['ChemID'] = chem_df.bgCAS.map(lambda x: getPubChemLink(x)) # Now through PubChem instead of ChemID
#     chem_df['EPA_ref'] = chem_df.DTXSID.map(lambda x: getCompToxRef(x))
    
#     #chem_df['molecule'] = chem_df.bgCAS.map(lambda x: getMoleculeImg(x))
#     #chem_df.molecule = chem_df.molecule # ?! why is this here?
#     # chem_df['fingerprint'] = chem_df.bgCAS.map(lambda x: getFingerprintStatus(x))
#     chem_df['fingerprint'] = chem_df.bgCAS.map(lambda x: getFingerprintImg(x))
#     #opt.classes = ['display','cell-border']
#     chem_df.bgIngredientName.fillna('non CAS',inplace=True)
#     chem_df['names'] = chem_df.bgIngredientName 
#     chem_df['just_cas'] = chem_df.bgCAS
#     chem_df.bgCAS = '<center><h3>'+chem_df.History+'</h3>'+chem_df.names+'</center>'
#     chem_df['ref'] = chem_df.ChemID+'<br>'+chem_df.EPA_ref
    
#     chem_df['extrnl'] = np.where(chem_df.is_on_CWA,'CWA<br>','    ')
#     chem_df.extrnl = np.where(chem_df.is_on_AQ_CWA,chem_df.extrnl+'AQ_CWA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_HH_CWA,chem_df.extrnl+'HH_CWA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_NPDWR,chem_df.extrnl+'NPDWR<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_DWSHA,chem_df.extrnl+'DWSHA<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_TEDX,chem_df.extrnl+'TEDX<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_prop65,chem_df.extrnl+'prop65<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_PFAS_list,chem_df.extrnl+'EPA_PFAS<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_UVCB,chem_df.extrnl+'UVCB<br>',chem_df.extrnl)
#     chem_df.extrnl = np.where(chem_df.is_on_diesel,chem_df.extrnl+'diesel<br>',chem_df.extrnl)
#     chem_df.extrnl = '<p style="color:green;font-size:105%;text-align:center;background-color:lightgrey;">'+chem_df.extrnl.str[:-4]+'</p>'
#     #chem_df.extrnl = np.where(chem_df.is_on_IRIS,chem_df.extrnl+'IRIS; ',chem_df.extrnl)
    
#     t = df_cas.groupby('bgCAS',as_index=False)['date'].min().rename({'date':'earliest_date',
#                                                                      'bgCAS':'just_cas'},axis=1)
#     chem_df = pd.merge(chem_df,t,on='just_cas',how='left')
#     chem_df = chem_df[['bgCAS',#'molecule',#'names',
#                        #'bgIngredientName','comm_name',
#                        'numRecords','numWithMass','calcMass','rq_lbs',
#                        'extrnl','fingerprint','ref']].sort_values('numWithMass',ascending=False)
#     chem_df.rq_lbs.fillna(' ',inplace=True)
#     chem_df = chem_df.rename({'bgCAS':'Material',#'bgIngredientName':'Name',# 'comm_name':'Common Name',
#                               'numRecords':'Total\nnumber of records','rq_lbs':'Reportable quantity (lbs)',
#                               'numWithMass':'Number of records with mass','calcMass':'Total mass used (lbs)',
#                               'extrnl':'Lists of Chemicals of Concern',
#                              'fingerprint':'ChemInformatics'},
#                              axis=1)    
#     return chem_df