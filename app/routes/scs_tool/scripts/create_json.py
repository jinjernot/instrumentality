import pandas as pd
import json
from collections import defaultdict

def generate_npu_json_from_excel(excel_filepath, json_filepath):
    """
    Reads processor data directly from an Excel (.xlsx) file, processes it,
    and writes it to a JSON file with a specific nested structure.

    NOTE: This script requires the 'pandas' and 'openpyxl' libraries.
    You can install them by running: pip install pandas openpyxl

    Args:
        excel_filepath (str): The path to the input Excel file.
        json_filepath (str): The path where the output JSON file will be saved.
    """
    print(f"--- Starting JSON Generation from Excel ---")
    print(f"Reading data from: {excel_filepath}")

    try:
        # Read the data directly from the first sheet of the Excel file.
        df = pd.read_excel(excel_filepath, sheet_name=0)
        
        # Ensure the column names are what we expect, stripping any extra whitespace.
        df.columns = [col.strip() for col in df.columns]

    except FileNotFoundError:
        print(f"❌ ERROR: The file was not found at '{excel_filepath}'")
        return
    except Exception as e:
        print(f"❌ ERROR: Failed to read or process the Excel file. Please ensure 'openpyxl' is installed. Reason: {e}")
        return

    # Use a defaultdict to easily append to lists for each NPU category.
    npu_groups = defaultdict(list)

    # Iterate over each row in the DataFrame to build the desired structure.
    for index, row in df.iterrows():
        # Check for and skip any rows where essential data might be missing.
        if pd.isna(row.get('npu')) or pd.isna(row.get('processorname')):
            print(f"⚠️ WARNING: Skipping row #{index + 2} due to missing 'npu' or 'processorname' data.")
            continue

        # Clean up potential whitespace or formatting issues.
        npu_category = str(row['npu']).strip()
        
        # Create the processor object for the JSON structure.
        processor_object = {
            "processorname": str(row['processorname']).strip(),
            # Corrected line: Take the value directly from the column without modification.
            "a_processor_nputops": str(row['a_processor_nputops']).strip()
        }
        
        # Add the new processor object to the correct NPU category list.
        npu_groups[npu_category].append(processor_object)

    # Create the final JSON structure with the top-level "processor" key.
    final_json_structure = {
        "processor": dict(npu_groups) # Convert defaultdict back to a regular dict for JSON
    }

    # Write the structured data to the output JSON file.
    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(final_json_structure, f, ensure_ascii=False, indent=2)
        print(f"✅ SUCCESS: JSON file has been created at '{json_filepath}'")
    except Exception as e:
        print(f"❌ ERROR: Failed to write JSON file. Reason: {e}")


if __name__ == "__main__":
    # Define the input and output file paths.
    input_excel_file = 'Processorname_NPU.xlsx'
    output_json_file = 'npu_database.json'

    # Call the function to generate the JSON file.
    generate_npu_json_from_excel(input_excel_file, output_json_file)
