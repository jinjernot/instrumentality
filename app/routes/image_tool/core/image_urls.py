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

        # Check if the 'image_url_https' element is present
        if asset_embed_code_element is not None:
            image_url = asset_embed_code_element.text.strip()

            # If the URL is not empty and not already in the list, add it to the list
            if image_url:
                response = requests.head(image_url)
                status_code = response.status_code
                unique_image_data.append({"url": image_url, "status": status_code})

    # Convert the list of unique image data to a pandas DataFrame
    df = pd.DataFrame(unique_image_data)

    # Save the DataFrame to an Excel file
    excel_file_name = f"{filename}.xlsx"
    # Use BytesIO to handle the files in memory
    excel_buffer = BytesIO()
    
    # Save the DataFrame to an Excel file
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    return excel_buffer, excel_file_name 