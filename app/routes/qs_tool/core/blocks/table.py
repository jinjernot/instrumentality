from docx.enum.text import WD_BREAK
from docx.shared import RGBColor
from docx.shared import Inches

from app.routes.qs_tool.core.format.hr import *

def process_footnotes(doc, footnotes):
    """ Process footnotes and add them to the Word document with blue font color"""
    paragraph = doc.add_paragraph()
    for index, data in enumerate(footnotes):
        # Skip footnotes containing unwanted values
        if "Container Name" in data or "Wireless WAN" in data:
            continue
        run = paragraph.add_run(data)
        run.font.color.rgb = RGBColor(0, 0, 153)
        
        if index < len(footnotes) - 1 and footnotes[index + 1].strip():  # Check if the next footnote is not empty
            run.add_break(WD_BREAK.LINE)

def insert_table(doc, df, html_file):
    """Insert tables into the Word document and corresponding HTML file"""
    footnotes = []  # To store footnotes temporarily
    
    # Remove NaN values and empty rows from the DataFrame
    df.fillna('', inplace=True)
    df.dropna(how='all', inplace=True)
    
    for index, row in df.iterrows():
        if row[0] == "Table":
            # Calculate page width
            page_width = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin
            
            # Add a table to the Word document
            table = doc.add_table(rows=1, cols=3)
            column_widths = (Inches(2), Inches(2), Inches(4))
            for column, width in zip(table.columns, column_widths):
                column.width = width
            
            for i in range(index + 1, len(df)):
                if df.iloc[i, 0] == "Table":
                    break
                elif df.iloc[i, 0] == "Footnotes":
                    footnotes = []
                    for j in range(i + 1, len(df)):
                        if df.iloc[j, 0] == "Table":
                            break
                        footnotes.append(str(df.iloc[j, 0]))
                    break
                else:
                    cell_1 = table.add_row().cells[1]
                    cell_1.text = str(df.iloc[i, 0])
                    for paragraph in cell_1.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True

                    cell_2 = table.rows[-1].cells[2]
                    cell_2.text = str(df.iloc[i, 1])

            cell_0 = table.cell(1, 0)
            cell_0.text = str(row[1])
            for paragraph in cell_0.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                
            table.rows[0]._element.getparent().remove(table.rows[0]._element)
            
            if footnotes:
                process_footnotes(doc, footnotes)
                footnotes = []

            doc.add_paragraph()

    # Generating HTML table
    html_table = '<table class="MsoNormalTable" cellSpacing="3" cellPadding="0" width="728" border="0">\n'
    
    for index, row in df.iterrows():
        if row[0] == "Table":
            start_row_index = index + 1
            html_table += '<tr>'
            html_table += '<th><b>{}</b></th>'.format(df.columns[0])
            html_table += '<th><b>{}</b></th>'
            html_table += '</tr>\n'
            end_row_index = start_row_index
            while end_row_index < len(df) and df.iloc[end_row_index, 0] != "Table":
                end_row_index += 1
                
            for i in range(start_row_index, end_row_index):
                html_table += '<tr>'
                html_table += '<td><b>{}</b></td>'.format(df.iloc[i, 0])
                html_table += '<td><b>{}</b></td>'
                html_table += '</tr>\n'
            
            html_table += '<tr><td colspan="2"><b>{}</b></td></tr>\n'.format(row[1])

    html_table += '</table>'

    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(html_table)
