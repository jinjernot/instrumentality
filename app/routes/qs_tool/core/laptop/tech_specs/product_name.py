import pandas as pd

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from app.routes.qs_tool.core.format.hr import *

def product_name_section(doc, file, html_file):
    """Product name section"""
    try:
        # Read Excel file
        df = pd.read_excel(file.stream, sheet_name='Callouts', engine='openpyxl')
        prod_name = df.columns[1]

        # Add title in Word document
        paragraph = doc.add_paragraph()
        run = paragraph.add_run("Product Name")
        run.font.size = Pt(12)
        run.bold = True
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # HTML content
        html_content = f'''
        <p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US" style="COLOR: #000099">&nbsp;</span></p></div></div><qsnav heading="Technical Specifications"><a name="Technical Specifications"></a>\n
        <p class="title">Technical Specifications</p></qsnav>
        <div class="section">
        <h2 style="MARGIN-TOP: 8pt; LINE-HEIGHT: 115%"><span lang="EN-US">PRODUCT NAME</span></h2>
        <table class="MsoNormalTable" cellSpacing="3" cellPadding="0" width="720" border="0">
        <tbody>
        <tr>
        <td style="WIDTH: 537.05pt; PADDING-BOTTOM: 0.75pt; PADDING-TOP: 0.75pt; PADDING-LEFT: 0.75pt; PADDING-RIGHT: 0.75pt" vAlign="top" width="716">
        <h2 style="MARGIN-TOP: 0cm; LINE-HEIGHT: 115%"><span lang="EN-US" style="FONT-SIZE: 10pt; FONT-VARIANT: normal !important; FONT-WEIGHT: normal; COLOR: black; LETTER-SPACING: 0pt; LINE-HEIGHT: 115%">{prod_name}</span></h2></td></tr>
        '''
        # Write HTML content to file
        with open(html_file, 'a', encoding='utf-8') as txt:
            txt.write(html_content)

        # Add product name to Word document
        paragraph = doc.add_paragraph(prod_name)

        # Add horizontal line
        insert_horizontal_line(doc.add_paragraph(), thickness=3)
        insert_html_horizontal_line(html_file)

    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)