import json
import pandas as pd

def npu_check(df, npu_json_path):
    """
    Validates both 'npu' and 'a_processor_nputops' data for processors found in the JSON.
    
    This function uses a JSON file where each processor name maps to its expected
    'npu' type and 'a_processor_nputops' value. If a processor from the report
    is found in the JSON, the function checks if its corresponding 'npu' and
    'a_processor_nputops' rows are present and correct. If the processor is not
    in the JSON, its rows are skipped entirely.
    """
    print("\n--- [NPU CHECK] Starting NPU & NPU TOPS Validation ---")
    
    try:
        with open(npu_json_path, 'r', encoding='utf-8') as f:
            npu_data = json.load(f).get("processor", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ [NPU CHECK] ERROR: Failed to load or parse NPU JSON: {e}")
        error_mask = df['ContainerName'].isin(['processorname', 'npu', 'a_processor_nputops'])
        df.loc[error_mask, 'Additional Information'] = 'NPU FAIL - JSON Error'
        return df

    if not npu_data:
        print("⚠️ [NPU CHECK] WARNING: 'processor' key not found or empty in NPU JSON.")
        return df

    processor_map = {
        proc_obj['processorname']: {
            'npu': npu_type,
            'a_processor_nputops': proc_obj['a_processor_nputops']
        }
        for npu_type, proc_list in npu_data.items()
        for proc_obj in proc_list
    }

    for sku, group in df.groupby('SKU'):
        
        processor_rows = group[group['ContainerName'] == 'processorname']
        if processor_rows.empty:
            continue

        # Corrected line: Added .strip() to remove whitespace
        processor_value = processor_rows['ContainerValue'].iloc[0].strip()
        
        expected_values = processor_map.get(processor_value)
        
        if expected_values:
            # The processor was found. Now, we MUST validate its related fields.
            npu_rows = group[group['ContainerName'] == 'npu']
            a_proc_tops_rows = group[group['ContainerName'] == 'a_processor_nputops']

            actual_npu_value = npu_rows['ContainerValue'].iloc[0].strip() if not npu_rows.empty else None
            actual_a_proc_tops_value = a_proc_tops_rows['ContainerValue'].iloc[0].strip() if not a_proc_tops_rows.empty else None

            npu_ok = actual_npu_value == expected_values['npu']
            a_proc_tops_ok = actual_a_proc_tops_value == expected_values['a_processor_nputops']
            
            status = "NPU OK" if npu_ok and a_proc_tops_ok else "NPU FAIL"
            
            indices_to_update = processor_rows.index.union(npu_rows.index).union(a_proc_tops_rows.index)
            df.loc[indices_to_update, 'Additional Information'] = status
        
        else:
            # This block now helps debug which processors are not being found.
            print(f"ℹ️ [NPU CHECK] Skipping SKU {sku}: Processor '{processor_value[:40]}...' not found in validation list.")
            continue

    print("\n--- [NPU CHECK] Finished Processing ---")
    return df