from app.routes.scs_tool.core.process_data import process_data_av, process_data_granular
from app.routes.scs_tool.core.format_data import format_data, format_data_granular
from app.routes.scs_tool.core.product_line import pl_check
from app.routes.scs_tool.core.qa_av import av_check
from config import *

import pandas as pd
import json
import os


def omega_report(file):
    
    try:
        # Read excel file
        df_s = pd.read_excel(file.stream, engine='openpyxl', sheet_name='SKU Accuracy')
        df_g = pd.read_excel(file.stream, engine='openpyxl', sheet_name='GranularContentReport')

        # Drop a list of columns
        cols_to_drop_s = SCS_COLS_TO_DROP
        cols_to_drop_g = SCS_COLS_TO_DROP_GRANULAR
        
        df_s = df_s.drop(cols_to_drop_s, axis=1)
        df_g = df_g.drop(cols_to_drop_g, axis=1)

        # Add a list of columns
        df_s[SCS_COLS_TO_ADD] = ''
        df_g[SCS_COLS_TO_ADD] = ''
        
        # Call the pl_check
        pl_check(df_s)

        # Filter out the rows where ContainerValue and ContainerName are '[BLANK]'
        df_s = df_s[df_s['ContainerValue'] != '[BLANK]']
        df_s = df_s[df_s['ContainerName'] != '[BLANK]']
        
        df_g = df_g[df_g['Granular Container Value'] != '[BLANK]']
        df_g = df_g[df_g['Granular Container Tag'] != '[BLANK]']
        
        # Drop rows with NaN values
        df_s = df_s.dropna(subset=['ContainerValue', 'ContainerName'])
        df_g = df_g.dropna(subset=['Granular Container Value', 'Granular Container Tag'])

        # Replace unicode character '\u00A0' with space
        df_s.replace('\u00A0', ' ', regex=True, inplace=True)
        df_g.replace('\u00A0', ' ', regex=True, inplace=True)
        
        # Removing ';' from end of ContainerValue
        df_s.loc[df_s['ContainerValue'].str.endswith(';'), 'ContainerValue'] = df_s['ContainerValue'].str.slice(stop=-1)
        df_g.loc[df_g['Granular Container Value'].str.endswith(';'), 'Granular Container Value'] = df_g['Granular Container Value'].str.slice(stop=-1)

        # Stripping leading whitespaces from PhwebDescription
        df_s['PhwebDescription'] = df_s['PhwebDescription'].str.lstrip()

        # Converting ContainerValue column to string type
        df_s['ContainerValue'] = df_s['ContainerValue'].astype(str)
        df_g['Granular Container Value'] = df_g['Granular Container Value'].astype(str)
        
        # Load JSON data
        with open(SCS_COMPONENT_GROUPS_PATH, 'r') as json_file:
            json_data = json.load(json_file)
        groups = json_data['Groups']
        
        # Filter rows based on criteria from JSON data
        filtered_rows = df_s[df_s.apply(lambda row: any(row['ComponentGroup'] == group['ComponentGroup'] and row['ContainerName'] in group['ContainerName'] for group in groups), axis=1)]
        rows_to_delete = df_s.index.difference(filtered_rows.index)
        df_s = df_s.drop(rows_to_delete)

        # Process JSON files
        #for x in os.listdir(JSON_PATH_AV):
        #    if x.endswith('.json'):
        #        container_name = x.split('.')[0]
        #        container_df_s = df_s[df_s['ContainerName'] == container_name]
        #        process_data_av(os.path.join(JSON_PATH_AV, x), container_name, container_df_s, df_s)
                       
        # Process JSON files
        #for x in os.listdir(JSON_GRANULAR_PATH):
        #    if x.endswith('.json'):
        #        container_name = x.split('.')[0]
        #        container_df_g = df_g[df_g['Granular Container Tag'] == container_name]
        #        process_data_granular(os.path.join(JSON_GRANULAR_PATH, x), container_name, container_df_g, df_g)

        excel_file = pd.ExcelFile(file.stream, engine='openpyxl')

        # Check if "ms4" sheet exists
        if "ms4" in excel_file.sheet_names:
            df_s_final = av_check(file)
            
            # Filter df_s to exclude rows where ComponentGroup is "Operating System"
            df_s_filtered = df_s[~df_s['ComponentGroup'].isin(['Operating System', 'Environment','Power Supply','Security Software','Optional Port','Special Features'])]
            
            # Find missing components only in the filtered df_s
            missing_components = set(df_s_filtered['Component']) - set(df_g['Component'])
            df_m = df_s_filtered[df_s_filtered['Component'].isin(missing_components)]
            
            with pd.ExcelWriter(SCS_REGULAR_FILE_PATH) as writer:
                df_s.to_excel(writer, sheet_name='qa', index=False)
                df_g.to_excel(writer, sheet_name='granular', index=False)
                df_s_final.to_excel(writer, sheet_name='duplicated', index=False)
                df_m.to_excel(writer, sheet_name='missing', index=False)
        else:
            # Filter df_s to exclude rows where ComponentGroup is "Operating System"
            df_s_filtered = df_s[~df_s['ComponentGroup'].isin(['Operating System', 'Environment'])]
            
            # Find missing components only in the filtered df_s
            missing_components = set(df_s_filtered['Component']) - set(df_g['Component'])
            df_m = df_s_filtered[df_s_filtered['Component'].isin(missing_components)]

            with pd.ExcelWriter(SCS_REGULAR_FILE_PATH) as writer:
                df_s.to_excel(writer, sheet_name='qa', index=False)
                df_g.to_excel(writer, sheet_name='granular', index=False)
                df_m.to_excel(writer, sheet_name='missing', index=False)

                
        #format_data()
    except Exception as e:
        print(e)

    

    return