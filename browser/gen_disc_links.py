
import os
# import numpy as np
import pandas as pd
# import shutil
# import re
# import subprocess
from datetime import datetime
# import openFF.common.file_handlers as fh
import openFF.common.text_handlers as th
import openFF.common.handles as hndl
# import openFF.common.nb_helper as nbh
# import openFF.common.display_tables as disp_tab
# import openFF.common.chem_list_summary as chem_sum


today = datetime.today()

class Disc_link_gen():
    
    def __init__(self,workingdf,arc_diff=None,use_archive_diff=False):
        self.allrec = workingdf
        self.makeHTMLfiles()

    
    def make_api_list(self):
        self.apis = self.allrec.api10.unique().tolist()    


    def generate_HTML(self,api,df):
        """api is api10 and df is already filtered for that"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{api}: Disclosure links</title>
        <link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">
        """

        html_content += """
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                background-color: #f9f9f9 ;
                border: 1px solid #ddd;
                font-family: sans-serif;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Add a subtle shadow */
            }
    
            th, td {
                border: 1px solid #ddd;
                padding: 12px; /* Increase padding for better readability */
                text-align: left;
            }
    
            th {
                background-color: #0b830b  ;
                color: white;
                text-align: center;
            }
    
    
            tr:hover { /* Highlight row on hover */
                background-color: #e9ecef;
            }
        </style>
        </head>"""
        
        html_content += f"""
        <body>
        <h1><center>Disclosures available at Open-FF for API Number:<br> {api}</h1></center>
    
        <table>
            <tr>
                <th>Status</th>
                <th>Link to Open-FF disclosure</th>
                <th>Fracking end date</th>
                <th>TBWV (gallons)</th>
                <th>Operator</th>
                <th>Has Chemical Records</th>
            </tr>
    """
        for i,row in df.iterrows():
           html_content += f"""
           <b>
            <tr>
                <td>{row.status}</td>
                <td>{row.disc_link}</td>
                <td>{row.date}</td>
                <td>{row.TotalBaseWaterVolume}</td>
                <td>{row.OperatorName}</td>
                <td>{row.has_chem_recs}</td>
            </tr> </b>
            """

        html_content += """
            </table>
    
        """
        
        html_content += f""" 
        <h3>Link to current disclosure at FracFocus: {df.FF_disc.iloc[0]}</h3><br>
        """    
        
        html_content += """    
        <br><br><h4>Variable Descriptions</h4>
        
        <table>
            <tr>
                <th>column</th>
                <th>description</th>
            </tr>
            <tr>
                <td>status</td>
                <td>for now, only current disclosures are available</td>
            </tr>
            <tr>
                <td>Link to Open-FF disclosure</td>
                <td>Selecting this link will take you to a Open-FF display of this FracFocus disclosure's data and added Open-FF information</td>
            </tr>
            <tr>
                <td>Fracking end date</td>
                <td>Reported last day of fracking job</td>
            </tr>
            <tr>
                <td>TBWV</td>
                <td>Reported volume of water used as carrier</td>
            </tr>
            <tr>
                <td>Operator</td>
                <td>Reported name of operating company</td>
            </tr>
            <tr>
                <td>Has Chemical Records</td>
                <td>Many early FracFocus disclosures do not include chemical records in the bulk download. This column indicates when a disclosure has records</td>
            </tr>
    </table>
<br><br>    
<a href="https://frackingchemicaldisclosure.wordpress.com/" title="Open-FF project home page blog"><img alt="openFF logo" height="100" src="https://storage.googleapis.com/open-ff-common/openFF_logo.png" width="100"><h2>Open-FF</h2></a>    
        </body>
        </html>
        """
        return(html_content)
    
    def getlink(self,row):
        return th.getDisclosureLink(row.APINumber,
                                    row.DisclosureId,
                                    text_to_show='disclosure at Open-FF',
                                    use_remote=True)
    
    def makeHTMLfiles(self):
        self.make_api_list()
        t = self.allrec.groupby('DisclosureId',as_index=False)[['api10','APINumber',
                                                                'FF_disc',
                                                                'date',
                                                                'TotalBaseWaterVolume',
                                                                'no_chem_recs',
                                                                'OperatorName']].first()
        t['disc_link'] = t.apply(lambda x: self.getlink(x),axis=1)
        t['status'] = 'current'
        t['has_chem_recs'] = ~(t.no_chem_recs)
        
        api10s = []
        links = []
        for i,api in enumerate(self.apis):
            if i%1000==0:
                print(f'on api {api}, number {i}')
            oneapi = t[t.api10==api].copy()
            html = self.generate_HTML(api,oneapi)
            fn = os.path.join(hndl.browser_api_links_dir,api+'.html')
            with open(fn,'w') as f:
                f.write(html)
            api10s.append(api)
            url = hndl.browser_root+f'api_links/{api}.html'
            links.append(url)
    
        # now create the single 
        link_table = pd.DataFrame({'APINumber':api10s,
                                   'url':links})
        link_table.to_parquet(os.path.join(hndl.browser_out_dir,
                                           'api_disclosure_links.parquet'))