from app.routes.qs_tool.core.blocks.paragraph import insert_list

def storage_section(doc, df):
    """Storage techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, df, "Storage and Drives")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)