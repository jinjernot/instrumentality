import xml.etree.ElementTree as ET
import pandas as pd

from zipfile import ZipFile, BadZipFile
from io import BytesIO

def image_only(file):
    # Image dimensions
    image_width = 300
    image_height = 300

    # Create an empty list to store all image data
    all_image_data = []

    # Check if the file is a ZIP file
    if file.filename.endswith('.zip'):
        try:
            # Open the ZIP file
            with ZipFile(file) as zip_file:
                # Iterate over each file in the ZIP
                for zip_info in zip_file.infolist():
                    # Check if the file is an XML file
                    if zip_info.filename.endswith('.xml'):
                        with zip_file.open(zip_info) as xml_file:
                            # Process the XML file
                            process_xml(xml_file, zip_info.filename, all_image_data)
        except BadZipFile:
            print(f"Error: The file '{file.filename}' is not a valid ZIP file.")
            return None
    else:
        # Process a single XML file
        process_xml(file, file.filename, all_image_data)

    # Sort image data by document type detail
    all_image_data = sorted(all_image_data, key=lambda x: x["document_type_detail"])

    # Generate HTML content
    html_content = generate_html(all_image_data, image_width, image_height)

    # Create a DataFrame from the image data
    df = pd.DataFrame(all_image_data)

    # Filter the DataFrame 
    df_filtered = df[df['document_type_detail'].isin(["product image", "product in use", "product image with output sample", "product image - not as shown with output sample"])]

    # Identify duplicate rows in the filtered DataFrame
    duplicates = df_filtered.duplicated(subset=["prodnum", "orientation", "pixel_height","pixel_width", "content_type", "cmg_acronym", "color"], keep=False)

    # Add a new column "note" and set it to "duplicate" for duplicate rows
    df_filtered['note'] = ''
    df_filtered.loc[duplicates, 'note'] = 'duplicate'

    # Extract the filename without extension for naming HTML and Excel files
    filename = file.filename.rsplit('.', 1)[0]
    
    # Prepare the output files
    excel_file_name = f"{filename}.xlsx"
    html_file_name = f"{filename}.html"

    # Use BytesIO to handle the files in memory
    excel_buffer = BytesIO()
    html_buffer = BytesIO()

    # Save the filtered DataFrame to an Excel file
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False)
    excel_buffer.seek(0)
    
    # Save the HTML content to the buffer
    html_buffer.write(html_content.encode('utf-8'))
    html_buffer.seek(0)

    # Create a ZIP file
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr(html_file_name, html_buffer.getvalue())
        zip_file.writestr(excel_file_name, excel_buffer.getvalue())
    zip_buffer.seek(0)

    return zip_buffer, f"{filename}.zip"

def process_xml(file, filename, all_image_data):
    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing the XML file '{filename}'. Skipping.")
        return

    # Extract the prodnum
    prodnum_element = root.find(".//product_numbers/prodnum")
    prodnum = prodnum_element.text.strip() if prodnum_element is not None else ""

    # Loop through all the required elements
    for asset_element in root.findall(".//image"):
        asset_embed_code_element = asset_element.find("image_url_https")
        orientation_element = asset_element.find("orientation")
        master_object_name_element = asset_element.find("master_object_name")
        pixel_height_element = asset_element.find("pixel_height")
        pixel_width_element = asset_element.find("pixel_width")
        content_type_element = asset_element.find("content_type")
        document_type_detail_element = asset_element.find("document_type_detail")
        cmg_acronym_element = asset_element.find("cmg_acronym")
        color_element = asset_element.find("color")

        # Check if 'image_url_https' and 'product image' or 'product in use' is available
        if asset_embed_code_element is not None and document_type_detail_element is not None:
            image_url = asset_embed_code_element.text.strip()
            document_type_detail = document_type_detail_element.text.strip()

            if image_url and document_type_detail in ["product image", "product in use", "product image with output sample", "product image - not as shown with output sample"]:
                orientation = orientation_element.text.strip() if orientation_element is not None else ""
                master_object_name = master_object_name_element.text.strip() if master_object_name_element is not None else ""
                pixel_height = pixel_height_element.text.strip() if pixel_height_element is not None else ""
                pixel_width = pixel_width_element.text.strip() if pixel_width_element is not None else ""
                content_type = content_type_element.text.strip() if content_type_element is not None else ""
                cmg_acronym = cmg_acronym_element.text.strip() if cmg_acronym_element is not None else ""
                color = color_element.text.strip() if color_element is not None else ""

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

def generate_html(image_data, image_width, image_height):
    html_content = """
    <html>
    <head>
    <style>
        table {
            font-family: Arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .divider {
            border: none;
            border-top: 2px solid rgb(0, 150, 214);
            margin: 20px auto;
            width: 50%;
        }
    </style>
    </head>
    <body>
    <table>
    <tr>
        <th>Prodnum</th>
        <th>URL</th>
        <th>Orientation</th>
        <th>Master Object Name</th>
        <th>Pixel Height</th>
        <th>Pixel Width</th>
        <th>Content Type</th>
        <th>Document Type Detail</th>
        <th>CMG Acronym</th>
        <th>Color</th>
        <th>Image</th>
    </tr>
    """
    
    previous_type = None
    for data in image_data:
        if previous_type is not None and previous_type != data['document_type_detail']:
            # Add <hr> to separate different document types
            html_content += """
            <tr>
                <td colspan="11"><hr class="divider"></td>
            </tr>
            """

        html_content += f"""
        <tr>
            <td>{data['prodnum']}</td>
            <td>{data['url']}</td>
            <td>{data['orientation']}</td>
            <td>{data['master_object_name']}</td>
            <td>{data['pixel_height']}</td>
            <td>{data['pixel_width']}</td>
            <td>{data['content_type']}</td>
            <td>{data['document_type_detail']}</td>
            <td>{data['cmg_acronym']}</td>
            <td>{data['color']}</td>
            <td><img src='{data['url']}' alt='Image' width='{image_width}' height='{image_height}'></td>
        </tr>
        """

        previous_type = data['document_type_detail']

    html_content += """
    </table>
    </body>
    </html>
    """
    return html_content
