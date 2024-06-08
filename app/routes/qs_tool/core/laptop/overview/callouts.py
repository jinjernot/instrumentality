import pandas as pd
import requests
import os

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.shared import Pt, Inches
from io import BytesIO

from app.routes.qs_tool.core.format.table import table_column_widths
from app.routes.qs_tool.core.format.hr import *

def download_image(url):
    """Download image from URL and return the image data."""
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None

def get_temp_filename(counter, suffix=".png"):
    """Generate a fixed temporary file name with a three-digit counter."""
    return f"image{counter:03d}{suffix}"


def callout_section(doc, file, html_file, prod_name, df):
    """Add Callout Section"""

    # Add the product name
    prodname_paragraph = doc.add_paragraph()
    run = prodname_paragraph.add_run(prod_name)
    run.font.size = Pt(14)
    run.bold = True
    prodname_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Read text from the external file
    with open("/home/garciagi/qs/app/core/format/styles.txt", 'r', encoding='utf-8') as external_txt:
    #with open("app/core/format/styles.txt", 'r', encoding='utf-8') as external_txt:
        external_text = external_txt.read()

    # add HTML Headers
    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(f'<html><head><title>{prod_name}</title>\n')
        txt.write('<meta content="text/html; charset=utf-8" http-equiv="Content-Type">\n')
        txt.write('<meta name="Generator" content="Microsoft Word 15 (filtered)">\n')
        # Add external text to HTML
        txt.write(f'{external_text}\n')
        txt.write('</head>\n')

        #Add title and product name
        txt.write('<body lang="ES-MX" style="WORD-WRAP: break-word" vLink="#990099" link="#0096d6"><qsnav heading="Overview"><a name="Overview"></a>\n')
        txt.write('<p class="title">Overview</p></qsnav>\n')
        txt.write('<div class="section">\n')
        txt.write(f'<p class="MsoNormal" style="LINE-HEIGHT: 115%"><b><span lang="EN-US" style="FONT-SIZE: 14pt; LINE-HEIGHT: 115%">{prod_name}</span></b></p>\n')

    # Read the doc
    #df = pd.read_excel(file, sheet_name='Callouts')
    df = pd.read_excel(file.stream, sheet_name='Callouts', engine='openpyxl')

    # Set the target directory
    target_directory = '/home/garciagi/qs'
    #target_directory = '.'

    # Get image URLs from the DataFrame
    img_url1 = df.iloc[4, 0]  # Assuming column 0, row 5
    img_url2 = df.iloc[11, 0]  # Assuming column 0, row 12

    # Initialize image counter
    img_counter = 1

    # Download images
    img_data1 = download_image(img_url1)
    img_data2 = download_image(img_url2)

    # Generate fixed temporary file names
    img_filename1 = get_temp_filename(img_counter)
    img_filename2 = get_temp_filename(img_counter + 1)

    # Increment image counter for the next iteration
    img_counter += 2

    # Save images to the specified directory
    img_filepath1 = os.path.join(target_directory, img_filename1)
    img_filepath2 = os.path.join(target_directory, img_filename2)

    with open(img_filepath1, "wb") as img_file1:
        img_file1.write(img_data1.getvalue())

    with open(img_filepath2, "wb") as img_file2:
        img_file2.write(img_data2.getvalue())

    paragraph_with_image = doc.add_paragraph()
    run = paragraph_with_image.add_run()
    run.add_picture(os.path.join(target_directory, img_filename1), width=Inches(5))
    
    # Center the paragraph
    paragraph_with_image.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Image HTML Tags
    img_html_code = f'<img src="{img_url1}" alt="Product Image" width="702" height="561"></span></p></td></tr>'
    img_html_code2 = f'<img src="{img_url2}" alt="Product Image" width="702" height="561"></span></p></td></tr>'

    # Front image HTML 
    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write('<table class="MsoTableGrid" style="BORDER-TOP: medium none; BORDER-RIGHT: medium none; BORDER-BOTTOM: medium none; BORDER-LEFT: medium none" cellSpacing="3" cellPadding="0" width="720" border="0">\n')
        txt.write('<tbody>\n')
        txt.write('<tr style="HEIGHT: 15pt">\n')
        txt.write('<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt" width="716" colSpan="4">\n')
        txt.write('<p class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><span lang="EN-US" style="COLOR: red"><img id="Imagen 4" src="image001.png" width="702" height="561"></span></p></td></tr>\n')
        txt.write('<tr style="HEIGHT: 15pt">\n')
        txt.write('<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="716" colSpan="4">')
        txt.write('<p class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><b><span lang="EN-US">Front</span></b></p></td></tr>')
        #txt.write(img_html_code +  '\n')

    # Add Front subtitle
    paragraph = doc.add_paragraph()
    run = paragraph.add_run("Front")
    run.font.size = Pt(12)
    run.bold = True
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add Table "Front"
    start_col_idx = 1
    end_col_idx = 4
    start_row_idx = 4
    end_row_idx = 9

    data_range = df.iloc[start_row_idx:end_row_idx+1, start_col_idx:end_col_idx+1]
    data_range = data_range.dropna(how='all')

    num_rows, num_cols = data_range.shape
    table = doc.add_table(rows=num_rows, cols=num_cols)

    table_column_widths(table, (Inches(.5), Inches(3.5), Inches(.5), Inches(3.5)))

    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for row_idx in range(num_rows):
        for col_idx in range(num_cols):
            value = data_range.iat[row_idx, col_idx]
            cell = table.cell(row_idx, col_idx)
            if not pd.isna(value):
                if isinstance(value, (int, float)):
                    cell.text = str(int(value))
                else:
                    cell.text = str(value)
                    
    #HTML Table
    html_table = '<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="716" colSpan="4"><p class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><b><span lang="EN-US">&nbsp;</span></b></p></td></tr>\n'
    for row_idx in range(num_rows):
        html_table += f'<tr style="HEIGHT: 15pt">\n'
        for col_idx in range(num_cols):
            value = data_range.iat[row_idx, col_idx]
            html_table += f'<td style="HEIGHT: 15pt; WIDTH: 19.2pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="26"><p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US">{value}</span></p></td>\n'

    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(html_table)

    # Insert HR
    insert_horizontal_line(doc.add_paragraph(), thickness=3)
    insert_html_horizontal_line(html_file)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    paragraph_with_image = doc.add_paragraph()
    run = paragraph_with_image.add_run()
    run.add_picture(os.path.join(target_directory, img_filename2), width=Inches(5))

    # Center the paragraph
    paragraph_with_image.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Sides image HTML subtitle
    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write('<table class="MsoTableGrid" style="BORDER-TOP: medium none; BORDER-RIGHT: medium none; BORDER-BOTTOM: medium none; BORDER-LEFT: medium none" cellSpacing="3" cellPadding="0" width="720" border="0">\n')
        txt.write('<tbody>\n')
        txt.write('<tr style="HEIGHT: 15pt">\n')
        txt.write('<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 5.4pt; PADDING-RIGHT: 5.4pt" width="716" colSpan="4">\n')
        txt.write('<p class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><span lang="EN-US" style="COLOR: red"><img id="Imagen 4" src="image002.png" width="702" height="561"></span></p></td></tr>\n')
        txt.write('<tr style="HEIGHT: 15pt">\n')
        txt.write('<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="716" colSpan="4">')
        txt.write('<p class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><b><span lang="EN-US">Sides</span></b></p></td></tr>')

    # Add Right subtitle
    paragraph = doc.add_paragraph()
    run = paragraph.add_run("Sides")
    run.font.size = Pt(12)
    run.bold = True
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # add table 'Sides'
    start_col_idx = 1
    end_col_idx = 4
    start_row_idx = 11
    end_row_idx = 22

    data_range = df.iloc[start_row_idx:end_row_idx+1, start_col_idx:end_col_idx+1]
    data_range = data_range.dropna(how='all')

    num_rows, num_cols = data_range.shape
    table = doc.add_table(rows=num_rows, cols=num_cols)

    table_column_widths(table, (Inches(.5), Inches(3.5), Inches(.5), Inches(3.5)))

    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for row_idx in range(num_rows):
        for col_idx in range(num_cols):
            value = data_range.iat[row_idx, col_idx]
            cell = table.cell(row_idx, col_idx)
            if not pd.isna(value):
                if isinstance(value, (int, float)):
                    cell.text = str(int(value))
                else:
                    cell.text = str(value)

    #HTML Table
    html_table = '<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="716" colSpan="4"><p class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><b><span lang="EN-US">&nbsp;</span></b></p></td></tr>\n'
    for row_idx in range(num_rows):
        html_table += f'<tr style="HEIGHT: 15pt">\n'
        for col_idx in range(num_cols):
            value = data_range.iat[row_idx, col_idx]
            html_table += f'<td style="HEIGHT: 15pt; WIDTH: 19.2pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="26"><p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US">{value}</span></p></td>\n'

    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(html_table)

    # Insert HR
    insert_horizontal_line(doc.add_paragraph(), thickness=3)
    insert_html_horizontal_line(html_file)

    doc.add_page_break()
    section = doc.sections[-1]
    section.start_type
    section.start_type = WD_SECTION.CONTINUOUS
