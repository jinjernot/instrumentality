from openpyxl.styles import PatternFill,Font

import openpyxl

def format_data():
    """This function is used to to formate the data in the excel file, bold headers, adjust the column width and highlight the errors"""

    # Load Workbook and get the active sheet
    wb = openpyxl.load_workbook('/home/garciagi/frame/SCS_QA.xlsx') # Server
    #wb = openpyxl.load_workbook('SCS_QA.xlsx') # Local
    worksheet = wb.active

    # Bold and color the headers
    header_fill = PatternFill(start_color='0072C6', end_color='0072C6', fill_type='solid') 
    for cell in worksheet[1]:
        cell.fill = header_fill
    
    # Loop over all the columns in the worksheet.
    for column in worksheet.columns:
        # Get the maximum length of any value in the column.
        max_length = 0
        column_name = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        # Calculate the adjusted width of the column.
        adjusted_width = (max_length + 2)
        # Set the width of the column to the adjusted width.
        worksheet.column_dimensions[column_name].width = adjusted_width
        worksheet.column_dimensions['H'].width = 100
        worksheet.column_dimensions['J'].width = 100

    # Loop over all the cells in column `I`.
    for cell in worksheet['I']:
        if 'ERROR' in str(cell.value):
            # Change the color of the font in the cell to red.
            font = cell.font
            cell.font = Font(color='FF0000', name=font.name, size=font.size)
    # Save the workbook to a file called `SCS_QA.xlsx`.
    wb.save('/home/garciagi/frame/SCS_QA.xlsx') # Server
    #wb.save('SCS_QA.xlsx') # Local