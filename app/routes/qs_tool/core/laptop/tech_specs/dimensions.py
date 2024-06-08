from app.routes.qs_tool.core.blocks.paragraph import insert_list

def dimensions_section(doc, html_file, df):
    """Dimensions techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, html_file, df, "Weight & Dimensions")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)