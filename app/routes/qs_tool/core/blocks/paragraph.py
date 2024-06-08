from docx.enum.text import WD_BREAK
from docx.shared import RGBColor
from docx.shared import Pt

from app.routes.qs_tool.core.format.hr import *

def insert_paragraph(doc, html_file, df, iloc_row, iloc_column):
    """Insert a paragraph into both the Word document and an HTML file"""
    data = df.iloc[iloc_row, iloc_column]
    paragraph = doc.add_paragraph()
    paragraph.add_run(data)

    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(f"<p>{data}</p>\n")

def process_footnotes(doc, footnotes):
    """Add footnotes to the Word document with blue font color"""
    if not footnotes:
        return

    paragraph = doc.add_paragraph()
    for index, data in enumerate(footnotes):
        run = paragraph.add_run(data)
        run.font.color.rgb = RGBColor(0, 0, 153)
        
        if index < len(footnotes) - 1:
            run.add_break(WD_BREAK.LINE)

def insert_list(doc, html_file, df, start_value):
    """Insert a list into the Word document and HTML file"""
    if start_value not in df.iloc[:, 1].tolist():
        print(f"Error: '{start_value}' not found in DataFrame.")
        return
    
    start_index = df.index[df.iloc[:, 1] == start_value].tolist()[0]
    next_value_indices = df.iloc[start_index:, 1][df.iloc[start_index:, 1] == 'Value'].index.tolist()
    
    if not next_value_indices:
        print("Error: 'Value' not found after", start_value)
        return
    next_value_index = next_value_indices[0]
    
    items = df.iloc[start_index:next_value_index, 1].tolist()
    
    if 'Footnotes' in items:
        footnotes_index = items.index('Footnotes')
        items = items[:footnotes_index]
        footnotes = df.iloc[footnotes_index + start_index + 1:next_value_index, 1].tolist()
    else:
        footnotes = []

    paragraph = doc.add_paragraph()
    run = paragraph.add_run(start_value.upper()) 
    paragraph = doc.add_paragraph()
    run.font.size = Pt(12)
    run.bold = True
    run.add_break(WD_BREAK.LINE)

    for index, data in enumerate(items[1:], start=1):
        run = paragraph.add_run(data)
        
        if index < len(items) - 1:
            run.add_break(WD_BREAK.LINE)
    
    run.add_break(WD_BREAK.LINE)
    process_footnotes(doc, footnotes)

    insert_horizontal_line(doc.add_paragraph(), thickness=3)
    insert_html_horizontal_line(html_file)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def insert_footnote(doc, html_file, df, iloc_range, iloc_column):
    """Insert a footnote into both the Word document and the HTML file"""
    footnote = df.iloc[iloc_range, iloc_column].tolist()

    paragraph = doc.add_paragraph()

    for index, note in enumerate(footnote):
        run = paragraph.add_run(note)
        run.font.color.rgb = RGBColor(0, 0, 153)
        
        if index < len(footnote) - 1:
            run.add_break(WD_BREAK.LINE)

    html_footnotes = '<tr>\n'
    for index, note in enumerate(footnote):
        html_footnotes += f'<p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US" style="COLOR: #000099">{note}</span></p>'
        if index < len(footnote) - 1:
            html_footnotes += '\n'
    html_footnotes += '</td></tr>\n'

    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write('<tr>')
        txt.write('<td style="WIDTH: 15.75pt; PADDING-BOTTOM: 0.75pt; PADDING-TOP: 0.75pt; PADDING-LEFT: 0.75pt; PADDING-RIGHT: 0.75pt" vAlign="top" width="21">')
        txt.write('<p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US" style="COLOR: #000099">&nbsp;</span></p></td>')
        txt.write('<td style="WIDTH: 519.8pt; PADDING-BOTTOM: 0.75pt; PADDING-TOP: 0.75pt; PADDING-LEFT: 0.75pt; PADDING-RIGHT: 0.75pt" vAlign="top" width="693" colSpan="2">')
        txt.write('<p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US" style="COLOR: black">&nbsp;</span></p></td></tr>')
        txt.write('<tr>')
        txt.write('<td style="WIDTH: 15.75pt; PADDING-BOTTOM: 0.75pt; PADDING-TOP: 0.75pt; PADDING-LEFT: 0.75pt; PADDING-RIGHT: 0.75pt" vAlign="top" width="21">')
        txt.write('<td style="WIDTH: 519.8pt; PADDING-BOTTOM: 0.75pt; PADDING-TOP: 0.75pt; PADDING-LEFT: 0.75pt; PADDING-RIGHT: 0.75pt" vAlign="top" width="693" colSpan="2">')
        txt.write(html_footnotes)
