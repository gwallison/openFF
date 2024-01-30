"""Used to create various reports, mostly for the colab notebooks"""
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, TableStyle, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
# import requests
# from io import BytesIO
from datetime import datetime


import openFF.common.handles as hndl

class Report_gen():
    def __init__(self,outfn,custom_title='Custom Title',report_title='Report title',
                 description=''):
        self.styles = getSampleStyleSheet()
        self.outfn = outfn
        self.custom_title = custom_title
        self.report_title = report_title
        self.description = description
        self.doc = SimpleDocTemplate(outfn)
        self.story = [] # contains the elements, in order
        self.gen_title_page()

    def gen_title_page(self):
        l = []
        l.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        logos = [[Image(os.path.join(hndl.logos_dir,'openFF_logo.png'),width=80,height=80),
                 self.make_paragraph('Open-FF Notebook Report','Title'),
                 Image(os.path.join(hndl.logos_dir,'2021_FT_logo_icon.png'),width=80,height=80)],
                 [self.make_paragraph('Open-FF'),'',self.make_paragraph('Sponsored by FracTracker')]]
        l.append(self.make_simple_row(logos))
        l.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        l.append(self.make_spacer(1))
        l.append(self.make_paragraph(self.custom_title,"Title"))
        l.append(self.make_spacer(2))
        l.append(self.make_paragraph(self.report_title,"Title"))
        l.append(self.make_spacer(3))
        l.append(self.make_paragraph("FracFocus download date: "+hndl.bulkdata_date,"Heading4"))
        l.append(self.make_paragraph("Open-FF data repository: "+hndl.repo_name,"Heading4"))
        l.append(self.make_paragraph(f'This report generated on {datetime.today():%B %d, %Y}',"Heading4"))
        l.append(self.make_spacer())

        l.append(self.make_paragraph(self.description))
        l.append(PageBreak())
        self.add_list_to_story(l)
        
        
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

    def make_spacer(self,num=1):
        return Spacer(1,0.5*inch*num)

    def make_simple_row(self,data,style=None):
        t = Table(data)
        # print(f'row style: {style}')
        if not style:
            t.setStyle(TableStyle([('HALIGN', (0, 0), (-1, -1), 'TA_CENTER')]))
        return t
    
    def make_table(self,df,convert=True):
        data = df
        if convert:
            data = self.convert_df(df)
        return Table(data, 
                      style = [('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center 
                               ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
                               ('GRID',(0,0),(-1,-1),0.5,colors.black)
                                ])

    # def add_paragraph(self,txt):
    #     para = Paragraph(txt,style=self.styles["Normal"])
    #     self.story.append(para)

    def make_paragraph(self,txt,kind="Normal"):
        # styles available: Heading1-6, Bullet, Code, Definition, Normal, Title, OrderedList, UnorderedList
        style = getSampleStyleSheet()[kind]
        return Paragraph(txt,style=style)
  
    def add_list_to_story(self,lst):
        for item in lst:
            self.story.append(item)
       
    def create_doc(self):
        doc = SimpleDocTemplate(self.outfn, pagesize=letter,
                            rightMargin=72,
                            leftMargin = 72,
                            topMargin= 72,
                            bottomMargin=18)
        doc.build(self.story,onFirstPage=self.first_page,onLaterPages=self.later_pages)
    

############################################
    # functions to make reportlab-friendly values from Open-FF data
    def getMoleculeImg_RL(self,cas,width=120,height=120):
        # uses file in openFF code repo for image, not url in browser
        ct_path = os.path.join(hndl.pic_dir,cas,'comptoxid.png')
        if os.path.exists(ct_path):
            # and is not empty:  # this is the normal return
            if os.path.getsize(ct_path) > 0:
                return Image(ct_path,width=width,height=height)
        return Paragraph('Image not available')

    def getFingerprintImg_RL(self,cas,width=90, height=65):
        fp_path = os.path.join(hndl.pic_dir,cas,'haz_fingerprint.png')
        cas_ignore = ['7732-18-5','proprietary','conflictingID',
                    'ambiguousID','sysAppMeta','cas_not_assigned']
        if not cas in cas_ignore:
            if os.path.exists(fp_path):
                return Image(fp_path,width=width,height=height)
        return self.make_paragraph(' -- ',"Normal")
   
    