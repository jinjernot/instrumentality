import xml.etree.ElementTree as ET  # Import the module for working with XML
import pandas as pd  # Import pandas for handling data in tabular form
from zipfile import ZipFile  # Import ZipFile to create zip files
from io import BytesIO  # Import BytesIO to handle in-memory data

def rich_media_only(file):
    # Image dimensions
    image_width = 300
    image_height = 300

    # List to store all image data
    all_image_data = []

    # Extract the file name without the extension for naming the HTML and Excel files
    filename = file.filename.rsplit('.', 1)[0]

    try:
        # Attempt to parse the XML file
        tree = ET.parse(file)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing XML file '{file.filename}'. Skipping.")
        return None

    # List to store specific image data
    image_data = []
    
# Get the product number, ensuring that prodnum_element is not None
    prodnum_element = root.find(".//product_numbers/prodnum")
    prodnum = prodnum_element.text.strip() if prodnum_element is not None else ""

    # Loop through all "asset" elements in the XML, ensuring that root.findall() doesn't return None
    for asset_element in root.findall(".//msc/asset") or []:  # Adding "or []" ensures it's iterable even if None
        # Find elements within each "asset"
        asset_embed_code_element = asset_element.find("asset_embed_code")
        asset_name_element = asset_element.find("asset_name")
        asset_category_element = asset_element.find("asset_category")
        document_type_detail_element = asset_element.find("asset_type")
        language_code_element = asset_element.find("language_code")
        asset_id_element = asset_element.find("asset_id")
        imagedetail_element = asset_element.find("imagedetail")

        # Check if certain elements are present (not None) before accessing them
        if (asset_embed_code_element is not None and
            asset_category_element is not None and
            document_type_detail_element is not None):
            
            asset_embed_code = asset_embed_code_element.text.strip()
            asset_category = asset_category_element.text.strip()
            document_type_detail = document_type_detail_element.text.strip()

            # Extract other elements if available, using conditional expressions to handle None
            language_code = language_code_element.text.strip() if language_code_element is not None else ""
            asset_name = asset_name_element.text.strip() if asset_name_element is not None else ""
            asset_id = asset_id_element.text.strip() if asset_id_element is not None else ""
            imagedetail = imagedetail_element.text.strip() if imagedetail_element is not None else ""
            # Filter data based on document type and asset category
            if document_type_detail == "Image" and asset_category in ["Image - Annotated", "Image - Product Detail", "Image - Banners"]:
                # Add the data to the list
                image_data.append({
                    "prodnum": prodnum,
                    "asset_name": asset_name,
                    "url": asset_embed_code,
                    "language_code": language_code,
                    "asset_id": asset_id,
                    "asset_category": asset_category,
                    "imagedetail": imagedetail,
                })

                # Add the data to the global image data list
                all_image_data.append({
                    "prodnum": prodnum,
                    "asset_name": asset_name,
                    "url": asset_embed_code,
                    "language_code": language_code,
                    "asset_id": asset_id,
                    "asset_category": asset_category,
                    "imagedetail": imagedetail,
                })

    # Sort the image data by asset category
    image_data = sorted(image_data, key=lambda x: x["asset_category"])

    # Create the HTML content to display the data in a table
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
        <th>Asset Name</th>
        <th>URL</th>
        <th>Language Code</th>
        <th>Asset ID</th>
        <th>Asset Category</th>
        <th>Image Detail</th>
        <th>Image</th>
    </tr>
    """

    # Variable to track the previous category
    previous_category = None
    for data in image_data:
        # Add a divider if the category changes
        if previous_category is not None and previous_category != data['asset_category']:
            html_content += """
            <tr>
                <td colspan="8"><hr class="divider"></td>
            </tr>
            """

        # Add the rows with the image data
        html_content += f"""
        <tr>
            <td>{data['prodnum']}</td>
            <td>{data['asset_name']}</td>
            <td>{data['url']}</td>
            <td>{data['language_code']}</td>
            <td>{data['asset_id']}</td>
            <td>{data['asset_category']}</td>
            <td>{data['imagedetail']}</td>
            <td><img src='{data['url']}' alt='Image' width='{image_width}' height='{image_height}'></td>
        </tr>
        """

        # Update the previous category
        previous_category = data['asset_category']

    # Close the table and the HTML content
    html_content += """
    </table>
    </body>
    </html>
    """

    # Create a DataFrame with the image data
    df = pd.DataFrame(all_image_data)

    # Identify duplicate rows in the DataFrame
    duplicates = df.duplicated(subset=["url", "language_code", "asset_id", "asset_category", "imagedetail"], keep=False)

    # Add a new "note" column and mark duplicate rows as "duplicate"
    df['note'] = ''
    df.loc[duplicates, 'note'] = 'duplicate'

    # Prepare the output file names
    excel_file_name = f"{filename}.xlsx"
    html_file_name = f"{filename}.html"

    # Use BytesIO to handle files in memory
    excel_buffer = BytesIO()
    html_buffer = BytesIO()

    # Save the DataFrame to an Excel file
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)

    # Save the HTML content to the buffer
    html_buffer.write(html_content.encode('utf-8'))
    html_buffer.seek(0)

    # Create a zip file with the Excel and HTML files
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr(html_file_name, html_buffer.getvalue())
        zip_file.writestr(excel_file_name, excel_buffer.getvalue())
    zip_buffer.seek(0)

    # Return the zip buffer and the zip file name
    return zip_buffer, f"{filename}.zip"
