from app.routes.qs_tool.core.blocks.paragraph import insert_list

def power_section(doc, df):
    """Power techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, df, "Power")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)