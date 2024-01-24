"""Used to create various reports, mostly for the colab notebooks"""

import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import openFF.common.handles as hndl

class Report_gen():
    def __init__(self,outfn):
        self.outfn = outfn
        self.doc = SimpleDocTemplate(outfn)
        self.story = [] # contains the elements, in order

    def convert_df(self,df):
        column_names = df.columns.tolist()
        data_list = df.values.tolist()
        return [column_names] + data_list

    def add_table(self,df):
        data = self.convert_df(df)
        table = Table(data, 
                      style = [('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center header
                               ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
                                ])
        self.story.append(table)

    def create_doc(self):
        print(f'Creating report at {self.outfn}')
        self.doc.build(self.story)



    