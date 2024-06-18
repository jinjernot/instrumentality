import requests
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

def image_url(file):
    # Create an empty list to store unique image URLs and their response status
    unique_image_data = []

    # Extract the filename without extension for naming
    filename = file.filename.rsplit('.', 1)[0]

    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing the XML file '{file.filename}'. Skipping.")
        return None

    # Loop through all 'image' elements in the XML file
    for asset_element in root.findall(".//image"):
        asset_embed_code_element = asset_element.find("image_url_https")
        pixel_width_element = asset_element.find("pixel_width")
        pixel_height_element = asset_element.find("pixel_height")
        document_type_detail_element = asset_element.find("document_type_detail")
        orientation_element = asset_element.find("orientation")
        master_object_name_element = asset_element.find("master_object_name")
        cmg_acronym_element = asset_element.find("cmg_acronym")

        # Check if the 'image_url_https' element is present
        if asset_embed_code_element is not None:
            image_url = asset_embed_code_element.text.strip()

            # If the URL is not empty, get additional data and add to the list
            if image_url:
                response = requests.head(image_url)
                status_code = response.status_code

                pixel_width = pixel_width_element.text.strip() if pixel_width_element is not None else ""
                pixel_height = pixel_height_element.text.strip() if pixel_height_element is not None else ""
                document_type_detail = document_type_detail_element.text.strip() if document_type_detail_element is not None else ""
                orientation = orientation_element.text.strip() if orientation_element is not None else ""
                master_object_name = master_object_name_element.text.strip() if master_object_name_element is not None else ""
                cmg_acronym = cmg_acronym_element.text.strip() if cmg_acronym_element is not None else ""

                unique_image_data.append({
                    "url": image_url,
                    "status": status_code,
                    "pixel_width": pixel_width,
                    "pixel_height": pixel_height,
                    "document_type_detail": document_type_detail,
                    "orientation": orientation,
                    "master_object_name": master_object_name,
                    "cmg_acronym": cmg_acronym
                })

    # Convert the list of unique image data to a pandas DataFrame
    df = pd.DataFrame(unique_image_data)

    # Save the DataFrame to an Excel file
    excel_file_name = f"{filename}.xlsx"
    # Use BytesIO to handle the files in memory
    excel_buffer = BytesIO()
    
    # Save the DataFrame to an Excel file
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        # Access the XlsxWriter workbook and worksheet objects
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Define the format for status codes not equal to 200
        format_red = workbook.add_format({'font_color': 'red'})
        
        # Apply conditional formatting to the status column (assuming it is column B, change if necessary)
        worksheet.conditional_format('H2:H{}'.format(len(df) + 1), 
                                     {'type': 'cell',
                                      'criteria': '!=',
                                      'value': 200,
                                      'format': format_red})
        
    excel_buffer.seek(0)
    
    return excel_buffer, excel_file_name
