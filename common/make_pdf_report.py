"""Used to create various reports, mostly for the colab notebooks"""

import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize


import openFF.common.handles as hndl

class Report_gen():
    def __init__(self,outfn,custom_title='Custom Title',report_title='Report title'):
        self.styles = getSampleStyleSheet()
        self.outfn = outfn
        self.custom_title = custom_title
        self.report_title = report_title
        self.doc = SimpleDocTemplate(outfn)
        self.story = [] # contains the elements, in order
        self.gen_title_page()

    def gen_title_page(self):
        self.add_spacer(2)
        self.add_heading(self.custom_title,"Title")
        self.add_spacer(2)
        self.add_heading(self.report_title,"Title")
        self.story.append(PageBreak())
        
 

    def first_page(self,canvas,document):
        PAGE_HEIGHT = defaultPageSize[1]
        PAGE_WIDTH = defaultPageSize[0]
        canvas.saveState()
        # Things you want just on the front page (headers, etc.)
        # canvas.setFont('Helvetica',18)
        # canvas.drawCentredString(PAGE_WIDTH/2.0,PAGE_HEIGHT-108,self.custom_title)
        
        # canvas.setFont('Helvetica',14)
        # canvas.drawCentredString(PAGE_WIDTH/2.0,PAGE_HEIGHT-80,self.report_title)
        canvas.restoreState()
    
        
    def later_pages(self,canvas, document):
        canvas.saveState()
        # canvas.setFont('Helvetica',10)
        # canvas.drawString(inch,10*inch,self.custom_title)

        canvas.setFont('Helvetica',10)
        canvas.drawString(7.5*inch,0.5*inch,'page {}'.format(document.page))

    def convert_df(self,df):
        column_names = df.columns.tolist()
        data_list = df.values.tolist()
        return [column_names] + data_list

    def add_spacer(self,num=1):
        spacer = Spacer(1,0.5*inch)
        for i in range(num):
            self.story.append(spacer)

    def add_table(self,df):
        data = self.convert_df(df)
        table = Table(data, 
                      style = [('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center header
                               ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
                               ('GRID',(0,0),(-1,-1),0.5,colors.black)
                                ])
        self.story.append(table)

    def add_paragraph(self,txt):
        para = Paragraph(txt,style=self.styles["Normal"])
        self.story.append(para)

    def add_heading(self,txt,kind="Heading1"):
        # styles available: Heading1-6, Bullet, Code, Definition, Normal, Title, OrderedList, UnorderedList
        para = Paragraph(txt,style=self.styles[kind])
        self.story.append(para)
        
    def add_image(self,img):
        # img = Image(fn)
        self.story.append(img)
        
    def create_doc(self):
        doc = SimpleDocTemplate(self.outfn, pagesize=letter,
                            rightMargin=72,
                            leftMargin = 72,
                            topMargin= 72,
                            bottomMargin=18)
        doc.build(self.story,onFirstPage=self.first_page,onLaterPages=self.later_pages)
    


    