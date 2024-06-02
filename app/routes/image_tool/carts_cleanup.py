import os
import xml.etree.ElementTree as ET
import pandas as pd

# Route to grab the XML files
xml_files = [file for file in os.listdir() if file.endswith(".xml")]

# Image dimensions
image_width = 500
image_height = 500

# Create an empty list
all_image_data = []

# Loop through each XML file
for xml_file_name in xml_files:
    # Define the corresponding HTML file name based on the XML file name
    html_file_name = os.path.splitext(xml_file_name)[0] + ".html"
    try:
        tree = ET.parse(xml_file_name)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing the XML file '{xml_file_name}'. Skipping.")
        continue

    # Create an empty list
    image_data = []

    # Get the prodnum
    prodnum_element = root.find(".//product_numbers/prodnum")
    prodnum = prodnum_element.text.strip() if prodnum_element is not None else ""

    # Loop through all the required elements
    for asset_element in root.findall(".//image"):
        asset_embed_code_element = asset_element.find("image_url_https")
        asset_id_element = asset_element.find("file_name")
        orientation_element = asset_element.find("orientation")
        master_object_name_element = asset_element.find("master_object_name")
        pixel_height_element = asset_element.find("pixel_height")
        pixel_width_element = asset_element.find("pixel_width")
        content_type_element = asset_element.find("content_type")
        document_type_detail_element = asset_element.find("document_type_detail")
        cmg_acronym_element = asset_element.find("cmg_acronym")
        color_element = asset_element.find("color")

        # Check if 'image_url_https' and 'product image' is available
        if asset_embed_code_element is not None and document_type_detail_element is not None:
            image_url = asset_embed_code_element.text.strip()
            document_type_detail = document_type_detail_element.text.strip()

            # Get the elements
            if image_url and document_type_detail == "product image":
                orientation = orientation_element.text.strip() if orientation_element is not None else ""
                master_object_name = master_object_name_element.text.strip() if master_object_name_element is not None else ""
                pixel_height = pixel_height_element.text.strip() if pixel_height_element is not None else ""
                pixel_width = pixel_width_element.text.strip() if pixel_width_element is not None else ""
                content_type = content_type_element.text.strip() if content_type_element is not None else ""
                cmg_acronym = cmg_acronym_element.text.strip() if cmg_acronym_element is not None else ""
                color = color_element.text.strip() if color_element is not None else ""

                image_data.append({
                    "prodnum": prodnum,
                    "url": image_url,
                    "orientation": orientation,
                    "master_object_name": master_object_name,
                    "pixel_height": pixel_height,
                    "pixel_width": pixel_width,
                    "content_type": content_type,
                    "document_type_detail": document_type_detail,
                    "cmg_acronym": cmg_acronym,
                    "color": color
                })

                # Append data to the list
                all_image_data.append({
                    "prodnum": prodnum,
                    "url": image_url,
                    "orientation": orientation,
                    "master_object_name": master_object_name,
                    "pixel_height": pixel_height,
                    "pixel_width": pixel_width,
                    "content_type": content_type,
                    "document_type_detail": document_type_detail,
                    "cmg_acronym": cmg_acronym,
                    "color": color
                })

    # Create the HTML
    with open(html_file_name, 'w') as html_file:
        html_file.write("<html>\n")
        html_file.write("<body>\n")

        # Loop through the data
        for data in image_data:
            html_file.write(f"<p>URL: {data['url']}</p>\n")
            html_file.write(f"<img src='{data['url']}' alt='Image' width='{image_width}' height='{image_height}'>\n")
            html_file.write(f"<p>Orientation: {data['orientation']}</p>\n")
            html_file.write(f"<p>Master Object Name: {data['master_object_name']}</p>\n")
            html_file.write(f"<p>Pixel Height: {data['pixel_height']}</p>\n")
            html_file.write(f"<p>Pixel Width: {data['pixel_width']}</p>\n")
            html_file.write(f"<p>Content Type: {data['content_type']}</p>\n")
            html_file.write(f"<p>Document Type Detail: {data['document_type_detail']}</p>\n")
            html_file.write(f"<p>CMG Acronym: {data['cmg_acronym']}</p>\n")
            html_file.write(f"<p>Color: {data['color']}</p>\n")
        html_file.write("</body>\n")
        html_file.write("</html>\n")

# Create a DataFrame from the image data
df = pd.DataFrame(all_image_data)

# Identify duplicate rows
duplicates = df.duplicated(subset=["prodnum", "orientation", "pixel_height", "content_type", "cmg_acronym", "color"], keep=False)

# Add a new column "note" and set it to "duplicate" for duplicate rows
df['note'] = ''
df.loc[duplicates, 'note'] = 'duplicate'

# Save the DataFrame to an Excel file
excel_file_name = "extracted_image_data.xlsx"
df.to_excel(excel_file_name, index=False)
