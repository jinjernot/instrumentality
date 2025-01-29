from app.routes.qs_tool.core.blocks.paragraph import insert_list

def graphics_section(doc, df):
    """Graphics techspecs section"""
    
    try:
        # Function to insert the list of values
        insert_list(doc, df, "Graphics")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)