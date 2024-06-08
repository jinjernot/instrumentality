from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

def insert_horizontal_line(paragraph, thickness=12):
    """Insert a horizontal line into the given paragraph"""
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    pPr.insert_element_before(pBdr,
        'w:shd', 'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap',
        'w:overflowPunct', 'w:topLinePunct', 'w:autoSpaceDE', 'w:autoSpaceDN',
        'w:bidi', 'w:adjustRightInd', 'w:snapToGrid', 'w:spacing', 'w:ind',
        'w:contextualSpacing', 'w:mirrorIndents', 'w:suppressOverlap', 'w:jc',
        'w:textDirection', 'w:textAlignment', 'w:textboxTightWrap',
        'w:outlineLvl', 'w:divId', 'w:cnfStyle', 'w:rPr', 'w:sectPr',
        'w:pPrChange'
    )
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), str(thickness))
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), 'auto')
    pBdr.append(bottom)

def insert_html_horizontal_line(html_file):
    """Insert a horizontal line into the HTML file"""
    with open(html_file, 'a', encoding='utf-8') as txt:
        txt.write('<tr style="HEIGHT: 15pt">\n')
        txt.write('<td style="HEIGHT: 15pt; WIDTH: 537.25pt; PADDING-BOTTOM: 0.85pt; PADDING-TOP: 0.85pt; PADDING-LEFT: 0.85pt; PADDING-RIGHT: 0.85pt" vAlign="top" width="716" colSpan="4">\n')
        txt.write('<div class="MsoNormal" style="TEXT-ALIGN: center; LINE-HEIGHT: 115%" align="center"><span lang="EN-US">\n')
        txt.write('<hr align="center" SIZE="2" width="100%">\n')
        txt.write('</span></div>\n')
        txt.write('<p class="MsoNormal" style="LINE-HEIGHT: 115%"></p></td></tr></tbody></table>')
