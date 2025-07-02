#Importar librería
import pandas as pd
import sys

def av_check(file):
    print("entro a av_check")
    #Cargar la informacion de los archivos en data frames
    try:
        SkuAcc=pd.read_excel(file, sheet_name="SKU Accuracy", engine='openpyxl')
        MS4_report=pd.read_excel(file, sheet_name="ms4", engine='openpyxl')
    except Exception as e:
        # Added a try-except block to prevent crashes if sheets are not found
        error_message = f"Could not read the Excel file. Please ensure it contains 'SKU Accuracy' and 'ms4' sheets. Original error: {e}"
        return pd.DataFrame({"ERROR": [error_message]})
        
    print("encontrados los dataframes")
    #Eliminar expacios excesivos y separar los SKUs y AVs de MS4 de sus regiones
    ms4sku_df=pd.DataFrame(MS4_report["SKU                                     "].str.split('#').str[0])
    ms4av_df=pd.DataFrame(MS4_report["SKU AV                                  "].str.split('#').str[0])
    ms4sku_df=ms4sku_df.replace(r"^ +| +$", r"", regex=True)
    ms4av_df=ms4av_df.replace(r"^ +| +$", r"", regex=True)

    #Validacion de datos de ambos dataframes ya limpios
    MS4_len=len(ms4sku_df.drop_duplicates())
    SKUAcc_len=len(SkuAcc["SKU"].drop_duplicates())
    
    # --- UPDATED ERROR REPORTING BLOCK ---
    if MS4_len != SKUAcc_len:
        # If the counts don't match, find and report the specific differences.
        
        # Get the actual sets of SKUs to compare
        sku_set_from_ms4 = set(ms4sku_df.iloc[:, 0].unique())
        sku_set_from_accuracy = set(SkuAcc["SKU"].astype(str).str.strip().unique())

        # Find which SKUs are in one sheet but not the other
        missing_in_ms4 = sku_set_from_accuracy - sku_set_from_ms4
        missing_in_accuracy = sku_set_from_ms4 - sku_set_from_accuracy
        
        # Build the detailed error message
        error_parts = ["SKU lists do not match between 'SKU Accuracy' and 'ms4' sheets."]
        if missing_in_ms4:
            missing_list = ", ".join(map(str, sorted(list(missing_in_ms4))))
            error_parts.append(f"SKUs in 'SKU Accuracy' but MISSING from 'ms4': [{missing_list}]")

        if missing_in_accuracy:
            missing_list = ", ".join(map(str, sorted(list(missing_in_accuracy))))
            error_parts.append(f"SKUs in 'ms4' but MISSING from 'SKU Accuracy': [{missing_list}]")
        
        # Join all parts of the error message with a newline for readability
        detailed_error_message = "\n".join(error_parts)
        
        error_df = pd.DataFrame({"ERROR": [detailed_error_message]})
        return error_df

    # --- THE REST OF YOUR ORIGINAL CODE CONTINUES UNCHANGED ---

    #Crear nuevos data frames para el análisis
    #DataFrame de SCS (Sku Accuracy)
    # Added a line to clean the 'Component' column to ensure the final merge works correctly
    SkuAcc['Component'] = SkuAcc['Component'].astype(str).str.strip()
    SKuAcc_df=pd.DataFrame(SkuAcc["Component"]).join(pd.DataFrame(SkuAcc["ComponentGroup"])).join(SkuAcc["SKU"])
    SKuAcc_df=SKuAcc_df.rename(columns={"SKU":"SCS_SKU","Component":"Component_SCS"})
    
    #DataFrame de BOM (MS4)
    MS4_df=ms4sku_df.join(ms4av_df)
    MS4_df=MS4_df.rename(columns={"SKU                                     ":"BOM_SKU","SKU AV                                  ":"Component_BOM"})

    #Crear nuevo data frame, buscando si un AV está asociado a X SKU
    lookup_df=SKuAcc_df.merge(
        MS4_df,
        left_on="Component_SCS",
        right_on="Component_BOM",
        how="left")

    #Filtrar AVs que no existan en algun SKU
    filter_df=lookup_df[lookup_df["BOM_SKU"].isnull()]

    #DataFrame que guarda los resultados del filtro
    df_s_final=pd.DataFrame(filter_df["SCS_SKU"]).join(pd.DataFrame(filter_df["ComponentGroup"]).join(filter_df["Component_SCS"]))
    #Eliminar registros duplicados del DataFrame resultante
    df_s_final=df_s_final.drop_duplicates()
    print("termino? antes de mandar return")
    
    return df_s_final