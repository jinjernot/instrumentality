import json
import pandas as pd

def npu_check(df, npu_json_path):
    """
    Validates NPU data only for processors explicitly found in the JSON file.
    If a processor from the report is not in the JSON, it is skipped entirely,
    leaving its "Additional Information" column untouched.
    """
    print("\n--- [NPU CHECK] Starting NPU Validation (Skip Logic Version) ---")
    
    try:
        with open(npu_json_path, 'r', encoding='utf-8') as f:
            npu_data = json.load(f).get("processor", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ [NPU CHECK] ERROR: Failed to load or parse NPU JSON: {e}")
        # We only mark an error for rows that *would* have been checked.
        df.loc[df['ContainerName'].isin(['processorname', 'npu']), 'Additional Information'] = 'NPU FAIL - JSON Error'
        return df

    if not npu_data:
        print("⚠️ [NPU CHECK] WARNING: 'processor' key not found in NPU JSON.")
        return df

    # Create a reverse map for efficient lookup
    processor_to_npu_map = {
        proc_string: npu_type
        for npu_type, proc_list in npu_data.items()
        for proc_string in proc_list
    }

    # --- Core Logic: Group by SKU ---
    for sku, group in df.groupby('SKU'):
        
        processor_rows = group[group['ContainerName'] == 'processorname']

        if processor_rows.empty:
            continue

        processor_value = processor_rows['ContainerValue'].iloc[0]
        
        # Determine if the processor from the report is in our JSON map
        expected_npu_type = None
        for valid_proc, npu_type in processor_to_npu_map.items():
            if valid_proc in processor_value:
                expected_npu_type = npu_type
                break
        
        # --- Main "Skip" Logic ---
        if expected_npu_type:
            # The processor was found in our list, so we proceed with validation.
            processor_row_index = processor_rows.index[0]
            npu_rows = group[group['ContainerName'] == 'npu']
            
            # Default to FAIL for the found processor; it must now prove its 'npu' row is correct.
            status = "NPU FAIL"

            if not npu_rows.empty:
                npu_value = npu_rows['ContainerValue'].iloc[0].strip()
                if npu_value == expected_npu_type:
                    # The processor is correct AND the NPU row is present with the correct value.
                    status = "NPU OK"
            
            # Update the status ONLY for the rows we intended to check.
            df.loc[processor_row_index, 'Additional Information'] = status
            if not npu_rows.empty:
                npu_row_index = npu_rows.index[0]
                df.loc[npu_row_index, 'Additional Information'] = status
        else:
            # The processor was NOT found in our list, so we do nothing and skip to the next SKU.
            continue

    print("\n--- [NPU CHECK] Finished Processing ---")
    return df