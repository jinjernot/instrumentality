from app.routes.qs_tool.core.laptop.overview.callouts import callout_section

import pandas as pd

def overview_section(doc, file):
    """Add Overview section"""
    
    # Load sheet into df
    #df = pd.read_excel(file, sheet_name='Callouts')
    df = pd.read_excel(file.stream, sheet_name='Callouts', engine='openpyxl')

    prod_name = df.columns[1]
    # Run the functions to build the overview section
    callout_section(doc, file, prod_name, df)
