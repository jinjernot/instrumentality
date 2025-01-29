from app.routes.qs_tool.core.blocks.paragraph import insert_list

def display_section(doc, df):
    """Display techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, df, "Display")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)