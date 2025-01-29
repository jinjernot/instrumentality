import asyncio
import os
import pandas as pd
import json
from app.routes.scs_tool.core.process_data import process_data_av, process_data_granular
from app.routes.scs_tool.core.format_data import format_data
from app.routes.scs_tool.core.product_line import pl_check
from config import *

# Asynchronous function to process AV JSON files
async def process_av_file(json_file, container_name, df_s):
    try:
        process_data_av(json_file, container_name, df_s, df_s)
        print(f"Processed AV file: {json_file}")
    except Exception as e:
        print(f"Error processing AV file {json_file}: {e}")

# Asynchronous function to process Granular JSON files
async def process_granular_file(json_file, container_name, df_g):
    try:
        process_data_granular(json_file, container_name, df_g, df_g)
        print(f"Processed Granular file: {json_file}")
    except Exception as e:
        print(f"Error processing Granular file {json_file}: {e}")

# Gather tasks for all AV files
async def process_all_av_files(df_s):
    tasks = []
    for x in os.listdir(SCS_JSON_PATH_AV):
        if x.endswith('.json'):
            container_name = x.split('.')[0]
            container_df_s = df_s[df_s['ContainerName'] == container_name]
            json_file = os.path.join(SCS_JSON_PATH_AV, x)
            tasks.append(process_av_file(json_file, container_name, container_df_s))
    await asyncio.gather(*tasks)

# Gather tasks for all Granular files
async def process_all_granular_files(df_g):
    tasks = []
    for x in os.listdir(SCS_JSON_GRANULAR_PATH):
        if x.endswith('.json'):
            container_name = x.split('.')[0]
            container_df_g = df_g[df_g['Granular Container Tag'] == container_name]
            json_file = os.path.join(SCS_JSON_GRANULAR_PATH, x)
            tasks.append(process_granular_file(json_file, container_name, container_df_g))
    await asyncio.gather(*tasks)

# Main asynchronous function to process all files
async def main_async(df_s, df_g):
    await asyncio.gather(
        process_all_av_files(df_s),
        process_all_granular_files(df_g)
    )

# Fallback for Python 3.6 to run asyncio tasks
def run_asyncio_task(task):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # If there's no event loop in the current thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(task)

# Entry point for processing
def omega_report(file):
    try:
        # Read Excel sheets
        df_s = pd.read_excel(file.stream, engine='openpyxl', sheet_name='SKU Accuracy')
        df_g = pd.read_excel(file.stream, engine='openpyxl', sheet_name='GranularContentReport')

        # Drop a list of columns
        df_s = df_s.drop(SCS_COLS_TO_DROP, axis=1)
        df_g = df_g.drop(SCS_COLS_TO_DROP_GRANULAR, axis=1)

        # Add a list of columns
        df_s[SCS_COLS_TO_ADD] = ''
        df_g[SCS_COLS_TO_ADD] = ''

        # Call the pl_check function
        pl_check(df_s)

        # Filter out rows where certain columns are '[BLANK]'
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

        # Removing ';' from the end of strings in certain columns
        df_s.loc[df_s['ContainerValue'].str.endswith(';'), 'ContainerValue'] = df_s['ContainerValue'].str.slice(stop=-1)
        df_g.loc[df_g['Granular Container Value'].str.endswith(';'), 'Granular Container Value'] = df_g['Granular Container Value'].str.slice(stop=-1)

        # Strip leading whitespaces from `PhwebDescription`
        df_s['PhwebDescription'] = df_s['PhwebDescription'].str.lstrip()

        # Convert `ContainerValue` to string type
        df_s['ContainerValue'] = df_s['ContainerValue'].astype(str)
        df_g['Granular Container Value'] = df_g['Granular Container Value'].astype(str)

        # Load JSON data for filtering
        with open(SCS_COMPONENT_GROUPS_PATH, 'r') as json_file:
            json_data = json.load(json_file)
        groups = json_data['Groups']

        # Filter rows based on JSON criteria
        filtered_rows = df_s[df_s.apply(
            lambda row: any(
                row['ComponentGroup'] == group['ComponentGroup'] and row['ContainerName'] in group['ContainerName']
                for group in groups
            ), axis=1
        )]
        df_s = df_s.loc[filtered_rows.index]

        # Launch asynchronous tasks for JSON processing
        run_asyncio_task(main_async(df_s, df_g))

        # Final Excel file creation
        missing_components = set(df_s['Component']) - set(df_g['Component'])
        df_m = df_s[df_s['Component'].isin(missing_components)]

        with pd.ExcelWriter(SCS_REGULAR_FILE_PATH) as writer:
            df_s.to_excel(writer, sheet_name='qa', index=False)
            df_g.to_excel(writer, sheet_name='granular', index=False)
            df_m.to_excel(writer, sheet_name='missing', index=False)

        # Format final data
        format_data()

    except Exception as e:
        print(f"Error in omega_report: {e}")
