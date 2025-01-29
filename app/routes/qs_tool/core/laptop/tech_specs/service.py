from app.routes.qs_tool.core.blocks.paragraph import insert_list

def service_section(doc, df):
    """Service and support techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, df, "Service and Support")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)