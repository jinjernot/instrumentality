import pandas as pd
from app.routes.ds_tool.core.word import excel_to_word

from config import DF_XLSX_FILE_PATH

def create_ds(file):
    """Builds a sheet"""

    # Read Excel
    df = pd.read_excel(file.stream, sheet_name='Content', engine='openpyxl')

    # Extract the header value from the DataFrame
    header_value = df.columns[1]  
    
    # Find the index where the value in the first column is "Name"
    name_index = df[df.iloc[:, 0] == "Name"].index[0]

    # Set column names based on the row where "Name" is found
    df.columns = df.iloc[name_index]

    # Drop rows before the "Name" row
    df = df.iloc[name_index+1:]

    # Remove formatting from text (e.g., italicized text)
    df = df.applymap(lambda x: x if not hasattr(x, 'font') else x.value)

    # Convert all data to string format
    df = df.astype(str)

    # Replace cells with value "_x0000_" with "##BLANK##"
    df.replace("_x0000_", "##BLANK##", inplace=True)
    
    # Remove rows where "Container Group" contains specific strings
    unwanted_strings = ["Messaging", "Facets", "Core Information", "Metadata"]
    df = df[~df["Container Group"].str.contains('|'.join(unwanted_strings), na=False)]

    df_skus = df.copy()

    # Remove rows where the content is the same for all columns in that row 
    df_skus = df_skus[df_skus.iloc[:, 7:].nunique(axis=1) > 1]

    # Extracting values from "Container Name" column
    container_name_values = df_skus["Container Name"].values

    # Extracting values starting from column 7
    values_from_column_7 = df_skus.iloc[:, 7:].values

    # Create a new DataFrame with the extracted values
    new_df = pd.DataFrame({'Container Name': container_name_values})

    # Get the column names from the original DataFrame starting from column 7
    original_column_names = df_skus.columns[7:]

    # Iterate over the remaining columns and add them to the new DataFrame
    for col_name, col_values in zip(original_column_names, values_from_column_7.T):
        new_df[col_name] = col_values

    # Remove rows with "nan" values
    new_df = new_df[~new_df.isin(['nan']).any(axis=1)]

    # Drop columns containing "Update" or "Status"
    columns_to_drop = [col for col in new_df.columns if "Update" in col or "Status" in col]
    new_df.drop(columns=columns_to_drop, inplace=True)

    # Keep only "Container Name" and "Series Value" columns
    df = df[["Container Name", "Series Value"]]

    # Remove rows where "Series Value" is "nan|#Intentionally Left Blank#"
    #df = df[~df["Series Value"].isin(["#Intentionally Left Blank#"])]
    #df = df[~df["Series Value"].isin(["##BLANK##"])]
    df = df[~df["Series Value"].isin(["nan"])]

    # Save Excel file
    #excel_file = 'data.xlsx'
    #df.to_excel(excel_file, index=False)
    new_df.to_excel(DF_XLSX_FILE_PATH, index=False)
    # Convert Excel to Word
    #word_file = 'data.docx'
    return excel_to_word(df, new_df, header_value)
