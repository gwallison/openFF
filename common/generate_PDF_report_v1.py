import os
import pandas as pd
from datetime import datetime
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, KeepTogether, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.lib import colors

class PDFReport:
    """
    Generates a multi-page PDF report summarizing FracFocus data.
    """
    def __init__(self, output_filename):
        self.output_filename = output_filename
        self.doc = SimpleDocTemplate(output_filename, pagesize=letter,
                                     rightMargin=0.75*inch, leftMargin=0.75*inch,
                                     topMargin=1*inch, bottomMargin=1*inch)
        self.story = []
        self._define_styles()

    # In your PDFReport class...
    def _define_styles(self):
        """Creates custom paragraph and table styles for the report."""
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='ReportTitle', parent=self.styles['h1'],
                                        fontSize=18, alignment=1, spaceAfter=14))
        self.styles.add(ParagraphStyle(name='SectionHead', parent=self.styles['h2'],
                                        fontSize=14, spaceAfter=10))
        
        # ADD THESE MISSING STYLE DEFINITIONS
        self.styles.add(ParagraphStyle(name='ChemHeader', parent=self.styles['h3'],
                                        fontSize=12, leading=14))
        self.styles.add(ParagraphStyle(name='SmallText', parent=self.styles['Normal'],
                                        fontSize=8, leading=10))
        
        # Define the base style WITHOUT the alternating color line
        self.well_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
    
        # ADD THE MISSING DEFINITION FOR THE CHEMICAL LAYOUT STYLE
        self.chem_layout_style = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 1, colors.darkgrey),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.lightgrey),
            ('SPAN', (0, 0), (-1, 0)),  # Span header across all columns
        ])
        
    def _header_footer(self, canvas, doc):
        """Adds a header and footer to each page."""
        canvas.saveState()
        # Header
        header = Paragraph("Open-FF FracFocus Chemical Disclosure Report", self.styles['SmallText'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        
        # Footer
        footer = Paragraph(f"Page {doc.page}", self.styles['SmallText'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

# In your PDFReport class...

    def build_title_page(self, report_name, intro_paragraph, meta_info):
        """
        Creates a flexible title page from provided arguments.
    
        Args:
            report_name (str): The main title of the report.
            intro_paragraph (str): The introductory text.
            meta_info (dict): A dictionary of key-value pairs to display in a table.
        """
        self.story.append(Paragraph(report_name, self.styles['ReportTitle']))
        
        self.story.append(Paragraph(intro_paragraph, self.styles['Normal']))
        self.story.append(Spacer(1, 0.25 * inch))
        
        # Dynamically create the metadata table from the dictionary
        meta_data = []
        for key, value in meta_info.items():
            # Format values with commas if they are numbers
            if isinstance(value, (int, float)):
                value_str = f"{value:,.6f}" if isinstance(value, float) else f"{value:,}"
            else:
                value_str = str(value)
            meta_data.append([f"{key}:", value_str])
    
        # Add the current date automatically
        meta_data.append(["Report Generated:", datetime.now().strftime("%B %d, %Y")])
        
        meta_table = Table(meta_data, colWidths=[1.5 * inch, 5.5 * inch])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        self.story.append(meta_table)
        self.story.append(PageBreak())
    
    # In your PDFReport class...
    
    def build_well_list(self, well_df):
        """
        Creates a table of well disclosures from all columns in the provided DataFrame.
        It will conditionally format 'date' and 'TotalBaseWaterVolume' if they exist.
        """
        if well_df.empty:
            self.story.append(Paragraph("No wells found in the specified area.", self.styles['Normal']))
            return
    
        self.story.append(Paragraph("Fracking Disclosures in Search Area", self.styles['SectionHead']))
    
        # Work on a copy to avoid modifying the original DataFrame
        df = well_df.copy()
    
        # --- Conditionally format known columns if they exist ---
        if 'date' in df.columns:
            # Create a formatted date column and drop the original
            df['Job End Date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df = df.drop(columns=['date'])
            # Optional: move the new date column to the front
            cols = df.columns.tolist()
            cols.insert(0, cols.pop(cols.index('Job End Date')))
            df = df[cols]
            
        if 'TotalBaseWaterVolume' in df.columns:
            # Format the volume with commas, handling potential errors
            try:
                df['TotalBaseWaterVolume'] = df['TotalBaseWaterVolume'].apply(lambda x: f"{float(x):,.0f}")
            except (ValueError, TypeError):
                # If formatting fails, just convert to string
                pass
    
        # --- Use all columns from the processed DataFrame for the table ---
        table_data = [df.columns.tolist()] + df.values.tolist()
    
        well_table = Table(table_data, repeatRows=1)
        
        # Get a copy of the base style and add banding
        style = TableStyle(self.well_table_style.getCommands())
        for i, row in enumerate(df.values):
            if (i + 1) % 2 == 1: # Odd data rows
                style.add('BACKGROUND', (0, i + 1), (-1, i + 1), colors.beige)
    
        well_table.setStyle(style)
        self.story.append(well_table)
        self.story.append(PageBreak())
    
    
    def build_water_graphic(self, image_path):
        """Adds the water usage graphic to the report, preserving aspect ratio."""
        self.story.append(Paragraph("Water Volume Analysis", self.styles['SectionHead']))
        
        if os.path.exists(image_path):
            # 1. Read the original image size
            img_reader = ImageReader(image_path)
            original_width, original_height = img_reader.getSize()
            
            # 2. Calculate the aspect ratio
            aspect = original_height / float(original_width)
            
            # 3. Set your desired width and calculate the proportional height
            desired_width = 6.5 * inch
            desired_height = desired_width * aspect
            
            # 4. Create the Image with both dimensions explicitly set
            img = Image(image_path, width=desired_width, height=desired_height)
            self.story.append(img)
        else:
            self.story.append(Paragraph("Water use graphic not available.", self.styles['Normal']))
            
        self.story.append(PageBreak())

        
    def build_chemical_summary(self, chem_df):
        """Builds the detailed summary for each chemical."""
        self.story.append(Paragraph("Summary of Disclosed Chemicals", self.styles['SectionHead']))
        
        chem_df = chem_df.sort_values('bgCAS').fillna(' -- ')
        
        for _, row in chem_df.iterrows():
            header_text = f"<b>{row.bgCAS}</b>: {row.epa_pref_name}"
            header_para = Paragraph(header_text, self.styles['ChemHeader'])

            stats_data = [
                ['Records', 'w/ Mass', 'Total Mass (lbs)', 'RQ (lbs)'],
                [row.tot_records, int(row.num_w_mass), f"{row.tot_mass}", row.rq_lbs]
            ]
            stats_table = Table(stats_data, colWidths=[0.8*inch, 0.8*inch, 1.5*inch, 1.4*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            lists_para = Paragraph(f"<b>Lists of Concern:</b><br/>{row.coc_lists}", self.styles['SmallText'])

            # Placeholder for the fingerprint image
            # In a real scenario, you'd generate or load this image
            fingerprint_placeholder = Paragraph("Fingerprint Image Unavailable", self.styles['SmallText'])

            layout_data = [
                [header_para],
                [stats_table, [fingerprint_placeholder, Spacer(1, 0.1*inch), lists_para]]
            ]

            master_table = Table(layout_data, colWidths=[4.6*inch, 2.4*inch])
            master_table.setStyle(self.chem_layout_style)
            
            self.story.append(KeepTogether([master_table, Spacer(1, 0.15*inch)]))

    def generate(self):
        """Builds and saves the final PDF document."""
        self.doc.build(self.story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        print(f"✅ Report successfully generated: {self.output_filename}")


if __name__ == '__main__':
    # ===================================================================
    # EXAMPLE USAGE: All report content is defined here
    # ===================================================================

    # 1. Define all text and data for the title page
    report_title = "Watershed Test Report"
    
    intro_text = """This report summarizes the chemicals disclosed in FracFocus within a
                  defined radius around a focal point. It was generated by the Open-FF
                  project to make chemical disclosures more accessible to the public."""

    report_metadata = {
        'Focal Latitude': 40.11137,
        'Focal Longitude': -81.37047,
        'Search Radius (feet)': 5280,
        'FracFocus Data Source': 'September 7, 2025 Download'
    }

    # --- (The rest of your data and path definitions remain the same) ---
    output_dir = './'
    water_graphic_path = 'water_use.jpg'
    
    # (Sample DataFrames for wells and chemicals)
    well_data = { # ... as before
    }
    wells_df = pd.DataFrame(well_data)

    chem_data = { # ... as before
    }
    chemicals_df = pd.DataFrame(chem_data)
    
    # 2. Generate the report
    output_file = os.path.join(output_dir, "FracFocus_Report_Flexible.pdf")
    report = PDFReport(output_file)
    
    # Call the new, more flexible method
    report.build_title_page(report_title, intro_text, report_metadata)
    
    # The rest of the calls are unchanged
    report.build_well_list(wells_df)
    report.build_water_graphic(water_graphic_path)
    report.build_chemical_summary(chemicals_df)
    
    # Save the final file
    report.generate()