import xml.etree.ElementTree as ET
import pandas as pd
from zipfile import ZipFile
from io import BytesIO

def annotated_only(file):
    # Image dimensions
    image_width = 300
    image_height = 300

    # Create an empty list
    all_image_data = []

    # Extract the filename without extension for naming HTML and Excel files
    filename = file.filename.rsplit('.', 1)[0]

    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing the XML file '{file.filename}'. Skipping.")
        return None

    # Create an empty list
    image_data = []
    # Get the prodnum
    prodnum_element = root.find(".//product_numbers/prodnum")
    prodnum = prodnum_element.text.strip() if prodnum_element is not None else ""

    # Loop through all the required elements
    for asset_element in root.findall(".//msc/asset"):
        asset_embed_code_element = asset_element.find("asset_embed_code")
        asset_name_element = asset_element.find("asset_name")
        asset_category_element = asset_element.find("asset_category")
        document_type_detail_element = asset_element.find("asset_type")
        language_code_element = asset_element.find("language_code")
        asset_id_element = asset_element.find("asset_id")
        imagedetail_element = asset_element.find("imagedetail")

        # Check if 'asset_embed_code_element', 'asset_category', and 'asset_type' are available
        if asset_embed_code_element is not None and asset_category_element is not None and document_type_detail_element is not None:
            asset_embed_code = asset_embed_code_element.text.strip()
            asset_category = asset_category_element.text.strip()
            document_type_detail = document_type_detail_element.text.strip()

            # Extract the new tags if available
            language_code = language_code_element.text.strip() if language_code_element is not None else ""
            asset_name = asset_name_element.text.strip() if asset_name_element is not None else ""
            asset_id = asset_id_element.text.strip() if asset_id_element is not None else ""
            imagedetail = imagedetail_element.text.strip() if imagedetail_element is not None else ""

            # Get the elements if conditions are met
            if document_type_detail == "Image" and asset_category == "Image - Annotated":
                image_data.append({
                    "prodnum": prodnum,
                    "asset_name": asset_name,
                    "url": asset_embed_code,
                    "language_code": language_code,
                    "asset_id": asset_id,
                    "imagedetail": imagedetail,
                })

                # Append data to the list
                all_image_data.append({
                    "prodnum": prodnum,
                    "asset_name": asset_name,
                    "url": asset_embed_code,
                    "language_code": language_code,
                    "asset_id": asset_id,
                    "imagedetail": imagedetail,
                })

    # Create the HTML table
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
    </style>
    </head>
    <body>
    <table>
    <tr>
        <th>Prodnum</th>
        <th>Asset Name</th>
        <th>URL</th>
        <th>Language Code</th>
        <th>Asset ID</th>
        <th>Image Detail</th>
        <th>Image</th>
    </tr>
    """
    
    for data in image_data:
        html_content += f"""
        <tr>
            <td>{data['prodnum']}</td>
            <td>{data['asset_name']}</td>
            <td>{data['url']}</td>
            <td>{data['language_code']}</td>
            <td>{data['asset_id']}</td>
            <td>{data['imagedetail']}</td>
            <td><img src='{data['url']}' alt='Image' width='{image_width}' height='{image_height}'></td>
        </tr>
        """
    html_content += """
    </table>
    </body>
    </html>
    """

    # Create a DataFrame from the image data
    df = pd.DataFrame(all_image_data)

    # Identify duplicate rows
    duplicates = df.duplicated(subset=["url", "language_code", "asset_id", "imagedetail"], keep=False)

    # Add a new column "note" and set it to "duplicate" for duplicate rows
    df['note'] = ''
    df.loc[duplicates, 'note'] = 'duplicate'

    # Prepare the output files
    excel_file_name = f"{filename}.xlsx"
    html_file_name = f"{filename}.html"

    # Use BytesIO to handle the files in memory
    excel_buffer = BytesIO()
    html_buffer = BytesIO()

    # Save the DataFrame to an Excel file
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)

    # Save the HTML content to the buffer
    html_buffer.write(html_content.encode('utf-8'))
    html_buffer.seek(0)

    # Create a zip file
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr(html_file_name, html_buffer.getvalue())
        zip_file.writestr(excel_file_name, excel_buffer.getvalue())
    zip_buffer.seek(0)

    return zip_buffer, f"{filename}.zip"
