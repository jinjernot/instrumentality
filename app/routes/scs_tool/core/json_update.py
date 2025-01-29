import json
import os
from config import SCS_JSON_PATH, SCS_JSON_PATH_AV

def process_json_input(tag, component, value):
    # Construct the file path using the tag as the file name
    file_path = os.path.join(SCS_JSON_PATH, f"{tag}.json")

    # Check if the JSON file exists
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as json_file:
            data = json.load(json_file)

            # The root key of the JSON is the same as the tag
            root_key = tag

            # Check if the component and value are already present
            for entry in data.get(root_key, []):
                if entry.get('PhwebDescription') == component and entry.get('ContainerValue') == value:
                    raise ValueError("Value already in JSON")  # Raise an error if the component and value are already in the file

            # If not present, add the new component and value
            data[root_key].append({
                'PhwebDescription': component,
                'ContainerValue': value
            })

            # Move the cursor to the beginning and truncate the file before writing
            json_file.seek(0)
            json_file.truncate()
            json.dump(data, json_file, indent=4)

    else:
        # If the file doesn't exist, raise an error
        raise FileNotFoundError("JSON file not found. Please ensure the file exists before attempting to update it.")

def update_json_av(tag_av, component_av, value_av):
    # Construct the file path using the tag as the file name
    file_path = os.path.join(SCS_JSON_PATH_AV, f"{tag_av}.json")

    # Check if the JSON file exists
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as json_file:
            data = json.load(json_file)

            # The root key of the JSON is the same as the tag
            root_key = tag_av

            # Check if the component and value are already present
            for entry in data.get(root_key, []):
                if entry.get('Component') == component_av and entry.get('ContainerValue') == value_av:
                    raise ValueError("Value already in JSON")  # Raise an error if the component and value are already in the file

            # If not present, add the new component and value
            data[root_key].append({
                'Component': component_av,
                'ContainerValue': value_av
            })

            # Move the cursor to the beginning and truncate the file before writing
            json_file.seek(0)
            json_file.truncate()
            json.dump(data, json_file, indent=4)

    else:
        # If the file doesn't exist, raise an error
        raise FileNotFoundError("JSON file not found. Please ensure the file exists before attempting to update it.")
