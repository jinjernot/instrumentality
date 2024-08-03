import os
import pandas as pd
import xml.etree.ElementTree as ET
import requests
from PIL import Image
from keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np

# Load the ResNet50 model
model = ResNet50(weights='imagenet')

def validate_url(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return "Valid"
        else:
            return "Invalid"
    except requests.RequestException:
        return "Invalid"

def classify_image(image_url, model):
    try:
        # Download the image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Open the image and resize it
        img = Image.open(response.raw).convert('RGB').resize((224, 224))

        # Convert the image to a numpy array and preprocess it
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Make predictions using the model
        preds = model.predict(img_array)
        decoded_preds = decode_predictions(preds, top=3)[0]

        # Check for specific categories
        categories = {
            "laptop": ["laptop", "notebook"],
            "desktop": ["desktop", "monitor", "computer"],
            "printer": ["printer"],
        }

        for _, name, _ in decoded_preds:
            for category, keywords in categories.items():
                if any(keyword in name.lower() for keyword in keywords):
                    return category.capitalize()

        return "Other"

    except Exception as e:
        print(f"Error classifying image {image_url}: {e}")
        return "Error"

def process_xml_files_from_folder(folder_path):
    all_image_data = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.xml'):
            xml_file_path = os.path.join(folder_path, filename)
            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
            except ET.ParseError:
                print(f"Error parsing the XML file '{filename}'. Skipping.")
                continue

            # Extract filename without extension
            base_filename = os.path.splitext(filename)[0]

            # Create an empty list
            image_data = []

            # Get the prodnum
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

                    # Get the elements
                    if image_url and document_type_detail in ["product image", "product in use"]:
                        orientation = orientation_element.text.strip() if orientation_element is not None else ""
                        master_object_name = master_object_name_element.text.strip() if master_object_name_element is not None else ""
                        pixel_height = pixel_height_element.text.strip() if pixel_height_element is not None else ""
                        pixel_width = pixel_width_element.text.strip() if pixel_width_element is not None else ""
                        content_type = content_type_element.text.strip() if content_type_element is not None else ""
                        cmg_acronym = cmg_acronym_element.text.strip() if cmg_acronym_element is not None else ""
                        color = color_element.text.strip() if color_element is not None else ""

                        # Validate URL
                        url_validity = validate_url(image_url)

                        # Validate the image type using computer vision
                        image_type = classify_image(image_url, model)

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
                            "color": color,
                            "url_validity": url_validity,
                            "image_type": image_type
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
                            "color": color,
                            "url_validity": url_validity,
                            "image_type": image_type
                        })

    # Sort image data by document type detail
    image_data = sorted(all_image_data, key=lambda x: x["document_type_detail"])

    # Read the template file
    with open('xml/template.html', 'r') as file:
        html_template = file.read()

    # Generate HTML table rows
    previous_type = None
    table_rows = ""
    for data in image_data:
        if previous_type is not None and previous_type != data['prodnum']:
            # Add <hr> to separate different document types
            table_rows += """
            <tr>
                <td colspan="13"><hr class="divider"></td>
            </tr>
            """

        table_rows += f"""
        <tr>
            <td>{data['prodnum']}</td>
            <td>{data['url']}</td>
            <td>{data['url_validity']}</td>
            <td>{data['orientation']}</td>
            <td>{data['master_object_name']}</td>
            <td>{data['pixel_height']}</td>
            <td>{data['pixel_width']}</td>
            <td>{data['content_type']}</td>
            <td>{data['document_type_detail']}</td>
            <td>{data['cmg_acronym']}</td>
            <td>{data['color']}</td>
            <td>{data['image_type']}</td>
            <td><img src='{data['url']}' alt='Image' width='300' height='300'></td>
        </tr>
        """

        previous_type = data['prodnum']

    # Replace placeholder with the generated rows
    html_content = html_template.replace('{{ table_rows }}', table_rows)

    # Create a DataFrame from the image data
    df = pd.DataFrame(all_image_data)

    # Identify duplicate rows
    duplicates = df.duplicated(subset=["prodnum", "orientation", "pixel_height", "content_type", "cmg_acronym", "color"], keep=False)

    # Add a new column "note" and set it to "duplicate" for duplicate rows
    df['note'] = ''
    df.loc[duplicates, 'note'] = 'duplicate'

    # Prepare the output files
    excel_file_name = "output.xlsx"
    html_file_name = "output.html"

    # Save the DataFrame to an Excel file
    excel_path = os.path.join(folder_path, excel_file_name)
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    # Save the HTML content to a file
    html_path = os.path.join(folder_path, html_file_name)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Processed {len(all_image_data)} images. Output saved to '{excel_path}' and '{html_path}'.")

# Specify the path to your XML folder here
xml_folder_path = 'xml/'
process_xml_files_from_folder(xml_folder_path)
