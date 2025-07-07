from app.routes.qs_tool.core.blocks.paragraph import insert_list

def certification_section(doc, df):
    """Certification and Compliance techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, df, "Certification and Compliance")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)