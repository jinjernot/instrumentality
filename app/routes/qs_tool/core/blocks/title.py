from docx.shared import Pt

def insert_title(doc, title, html_file):
    """Insert a title into the Word document and corresponding HTML file"""
    # Add the title to the Word document
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(title)
    run.font.size = Pt(12)
    run.bold = True

    # Write the HTML title
    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(f'<h2 style="LINE-HEIGHT: 115%"><span lang="EN-US">{title}</span></h2>\n')
        txt.write('<table class="MsoTableGrid" style="BORDER-TOP: medium none; BORDER-RIGHT: medium none; BORDER-BOTTOM: medium none; BORDER-LEFT: medium none" cellSpacing="3" cellPadding="0" width="720" border="0">\n')
        txt.write('<tbody>\n')
        txt.write('<tr>\n')
        txt.write('<td style="WIDTH: 18.45pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="25">\n')
        txt.write('<p class="MsoNormal" style="LINE-HEIGHT: 115%"><span lang="EN-US">&nbsp;</span></p></td>\n')

def insert_subtitle(doc, html_file, df, iloc_row, iloc_column):
    """Insert a subtitle into the Word document and corresponding HTML file"""
    # Add the subtitle to the Word document
    paragraph = doc.add_paragraph()
    subtitle = df.iloc[iloc_row, iloc_column]
    run = paragraph.add_run(subtitle)
    run.bold = True

    # Write the HTML subtitle
    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write(f'<p class="MsoNormal" style="LINE-HEIGHT: 115%"><b><span lang="EN-US">{subtitle}</span></b></p>\n')
