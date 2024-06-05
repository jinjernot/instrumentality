import pandas as pd

def battery_life(file, file2):
    df = pd.read_excel(file.stream, engine='openpyxl') 
    
    # Create a new DataFrame       
    battery_life_df = pd.DataFrame(columns=['SKU', 'displaybright', 'displaymet', 'displaycolorgamut',
                                       'facet_maxres', 'graphicseg_01header', 'processorname',
                                       'filter_storagetype', 'storage_acceleration', 
                                       'graphicseg_01card_01', 'graphicseg_02card_01', 'facet_graphics'])
    try:
        # Group by SKU
        grouped = df.groupby('SKU')

        for sku, group_df in grouped:
            # Define a dictionary to store the data for the current SKU
            sku_data = {'SKU': sku}
            
            # Populate the dictionary with data from each ContainerName
            for header in ['displaybright', 'displaymet', 'displaycolorgamut',
                           'facet_maxres', 'graphicseg_01header', 'processorname',
                           'filter_storagetype', 'storage_acceleration', 
                           'graphicseg_01card_01', 'graphicseg_02card_01', 'facet_graphics']:
                container_value = group_df.loc[group_df['ContainerName'] == header, 'ContainerValue'].reset_index(drop=True)
                if not container_value.empty:
                    sku_data[header] = container_value[0]  # Take the first value if multiple values exist

            # Append the data for the current SKU to battery_life_df
            battery_life_df = battery_life_df.append(sku_data, ignore_index=True)

        # Read the second DataFrame
        df2 = pd.read_excel(file2.stream, engine='openpyxl')
        
        # Filter rows from df2 based on "Container" column
        filtered_df2 = df2[df2['Container'].isin(['batterylife', 'maxbatterylifevideo'])]
        
        # Merge the filtered data from df2 to battery_life_df based on "SKU" column
        battery_life_df = pd.merge(battery_life_df, filtered_df2, on='SKU', how='left')
        
        # Save battery_life_df to an Excel file
        battery_life_df.to_excel("/home/garciagi/frame/Battery_Life_QA.xlsx", index=False)
        
    except Exception as e:
        print(e)
    
    return battery_life_df
